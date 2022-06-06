"""
implementation of Hist class, a histogram with a fixed number of bins that
can be merged efficiently
"""

# Copyright (C) Bas Swinkels, 2013
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import numpy as np

from application1.config import config_manager

LOG = config_manager.get_logger(__name__)

flintmax = 2 ** 53


def myfloor(x, lg2):
    """floor(x * 2**lg2), as integer"""
    return np.floor(x * 2.0 ** lg2).astype(np.int64)


def myroll(x, shift):
    """faster version of np.roll for vectors"""
    shift %= x.size
    return np.concatenate((x[-shift:], x[:-shift]))


class Hist:
    """Histogram that allows for easy merging, so that calculating a histogram
    over long stretches can be done in pieces. To avoid floating point issues,
    calculations are done with integers as far as possible. Most calculations
    are done as powers of 2. Because of this, the bins are not always aligned
    perfectly with the data, but a filling factor close to 50% is guarenteed.
    Typical application:

    cum_hist = Hist([])
    for data in iterator:
        hist = Hist(data)
        cum_hist += hist

    plot(cum_hist.xgrid, cum_hist.counts)
    plot(cum_hist.xgrid, cum_hist.cdf)
    """

    def __init__(self, x: np.ndarray, l2_nbin=12, spanlike=None):
        """calculates histogram of vector x with 2**l2nbin number of bins. If another histogram spanlike is given,
        its span will be used to avoid useless resizing when merging or comparing later.
        """

        self.l2_nbin = l2_nbin
        self.nbin = 2 ** l2_nbin

        assert x.size < 2 ** 32
        assert x.ndim < 2
        self.ntot = x.size

        if not x.size:
            self.const_val = None
            self.check()
            return

        self.x_min = x.min()
        self.x_max = x.max()

        if not np.isfinite(self.x_max - self.x_min):
            assert not np.isnan(x).all(), "Array of only NaNs encountered"
            mean = np.nanmean(x)
            x = np.nan_to_num(x, copy=False, nan=mean)
            self.x_min = x.min()
            self.x_max = x.max()

        if self.x_min == self.x_max:
            self.const_val = self.x_min
            self.check()
            return
        self.const_val = None

        margin = (self.nbin + 2) / self.nbin
        self.l2_span = int(np.ceil(np.log2((self.x_max - self.x_min) * margin)))

        if spanlike:
            if spanlike.isexpanded:
                self.l2_span = max(self.l2_span, spanlike.l2_span)
            else:
                spanlike = None

        self.i_min = myfloor(self.x_min, self.l2_nbin - self.l2_span)
        self.i_max = myfloor(self.x_max, self.l2_nbin - self.l2_span)
        if max(self.i_max, -self.i_min) > flintmax:
            raise ValueError('Data are badly scaled')
        assert self.i_max - self.i_min < self.nbin

        ind = myfloor(x, self.l2_nbin - self.l2_span)

        if (spanlike and self.l2_span == spanlike.l2_span and
                spanlike.i_offset <= self.i_min and
                self.i_max < spanlike.i_offset + self.nbin):

            assert self.nbin == spanlike.nbin
            self.i_offset = spanlike.i_offset
        else:
            self.i_offset = (self.i_min + self.i_max + 1 - self.nbin) // 2

        self.counts = np.bincount(ind - self.i_offset, minlength=self.nbin).astype(np.uint32)

        self.check()

    @property
    def isempty(self):
        return self.ntot == 0

    @property
    def isconst(self):
        return self.const_val is not None

    @property
    def isexpanded(self):
        return self.ntot > 0 and self.const_val is None

    @property
    def span(self):
        return 2.0 ** self.l2_span

    @property
    def offset(self):
        return self.i_offset * 2.0 ** (self.l2_span - self.l2_nbin)

    @property
    def xgrid(self):
        """returns grid for plotting"""
        xg = np.arange(self.nbin, dtype=float)
        xg *= 2.0 ** (self.l2_span - self.l2_nbin)
        xg += self.offset
        return xg

    @property
    def cdf(self):
        """returns cumulative distribution function. Note that the
        last point should be 1 by definition and that a first
        implicit point equal to zero is missing"""
        assert self.isexpanded
        return self.counts.cumsum() / self.ntot

    def __repr__(self):
        if self.isempty:
            return 'empty histogram'
        if self.isconst:
            return 'histogram of %i points with constant value %g' % (
                self.ntot, self.const_val)
        return 'histogram of %i points, span = %g, offset = %g' % (
            self.ntot, self.span, self.offset)

    def enlarge(self):
        """increase span by 2 and merge bins"""
        assert self.isexpanded

        newcounts = np.zeros(self.nbin, dtype=np.uint32)
        if self.i_offset % 2:
            newcounts[0] = self.counts[0]
            newcounts[1:self.nbin // 2] = (self.counts[1:-1:2] +
                                           self.counts[2:-1:2])
            newcounts[self.nbin // 2] = self.counts[-1]
        else:
            newcounts[:self.nbin // 2] = self.counts[::2] + self.counts[1::2]
        self.counts = newcounts

        """
      
        mid = self.nbin // 2
        cnt = self.counts
        if self.i_offset % 2:
            np.add(cnt[1:-1:2], cnt[2:-1:2], out=cnt[1:mid])
            cnt[mid] = cnt[-1]
            cnt[mid+1:] = 0
        else:
            np.add(cnt[::2], cnt[1::2], out=cnt[:mid])
            cnt[mid:] = 0
        """

        self.l2_span += 1
        self.i_offset //= 2
        self.i_min //= 2
        self.i_max //= 2
        self.check()

    def shift(self, ishift):
        """shifts histogram by shift_counts to the right.
        Counts and offset are adjusted"""
        if ishift == 0:
            return

        if ishift < 0:
            assert not np.any(self.counts[ishift:]), 'bins not emtpy'
        elif ishift > 0:
            assert not np.any(self.counts[:ishift]), 'bins not emtpy'
        self.counts = myroll(self.counts, -ishift)
        self.i_offset += ishift
        self.check()

    def expand(self, l2_span):
        """if histo is constant, expand it to one with given span"""
        if not self.isconst:
            return
        self.l2_span = l2_span
        self.i_min = myfloor(self.const_val, self.l2_nbin - self.l2_span)
        self.i_max = self.i_min
        self.i_offset = self.i_min - self.nbin // 2
        self.counts = np.zeros(self.nbin, dtype=np.uint32)
        self.counts[self.nbin // 2] = self.ntot
        print(f'{self.counts.cumsum()[-1]=}')
        self.const_val = None
        self.check()

    def check(self):
        """checks various invariants of internal state of histogram"""

        if self.isempty:
            assert self.const_val is None
        elif self.isexpanded:
            istart = self.i_min - self.i_offset
            istop = self.i_max - self.i_offset
            assert 0 <= istart < self.nbin
            assert 0 <= istop < self.nbin
            assert self.counts[istart] > 0
            assert self.counts[istop] > 0
            assert (self.counts[:istart] == 0).all()
            assert (self.counts[istop + 1:] == 0).all()
            assert self.ntot == self.counts.sum()
        else:
            assert self.isconst

    def __eq__(self, other):
        """only for debugging purposes, this might alter both self and other"""
        if self.isempty and other.isempty:
            return True
        if self.ntot != other.ntot:
            return False
        if self.isconst and other.isconst:
            return self.const_val == other.const_val
        self.align(other)
        return (self.counts == other.counts).all()

    def __iadd__(self, other):
        """
        merges the counts of other with self. Histograms will be aligned
        first, which might modify self and other. Returned object can be
        be either self or other.
        """

        if other.isempty:
            return self
        if self.isempty:
            return other

        self.align(other)

        if self.isexpanded:
            self.counts += other.counts
            self.i_min = min(self.i_min, other.i_min)
            self.x_min = min(self.x_min, other.x_min)
            self.i_max = max(self.i_max, other.i_max)
            self.x_max = max(self.x_max, other.x_max)
        else:
            assert self.const_val == other.const_val
        self.ntot += other.ntot
        self.check()
        return self

    def align(self, other):
        """
        Aligns two histograms so that they can be merged or compared
        Note that both self and other can be modified in the process.
        Result is either two expanded and aligned histos, or two constant
        histos with the same value.
        """
        assert not (self.isempty or other.isempty), 'cannot align empty histos'
        assert self.nbin == other.nbin

        if self.isconst:
            if other.isconst:
                if self.const_val == other.const_val:
                    return
                else:
                    l2_span = int(np.ceil(np.log2(abs(
                        self.const_val - other.const_val))))
                    self.expand(l2_span)
                    other.expand(l2_span)

            else:
                self.expand(other.l2_span)
        elif other.isconst:
            other.expand(self.l2_span)
        assert self.isexpanded and other.isexpanded

        smallest, biggest = sorted([self, other], key=lambda h: h.l2_span)
        while smallest.l2_span < biggest.l2_span:
            smallest.enlarge()

        while (max(self.i_max, other.i_max) -
               min(self.i_min, other.i_min)) >= self.nbin:
            self.enlarge()
            other.enlarge()
        assert self.l2_span == other.l2_span

        if self.i_offset <= other.i_min and other.i_max < self.i_offset + self.nbin:

            other.shift(self.i_offset - other.i_offset)
        else:
            i_offset_new = (min(self.i_min, other.i_min) +
                            max(self.i_max, other.i_max) +
                            1 - self.nbin) // 2
            self.shift(i_offset_new - self.i_offset)
            other.shift(i_offset_new - other.i_offset)
        assert self.i_offset == other.i_offset


def plot_hist(h, **kwargs):
    import matplotlib.pyplot as plt
    plt.bar(h.xgrid, h.counts, width=h.span / h.nbin, **kwargs)
    plt.xlim([h.offset, h.offset + h.span])
    plt.show()


# some quick test for correctness and profiling
def testme(nrep, size):
    for i in range(nrep):
        n = np.random.randint(1, size)
        m = np.random.randint(n)
        x = 10 ** (20 * np.random.rand(1) - 10) * np.random.randn(n)
        h1 = Hist(x[:m], l2_nbin=10)
        h2 = Hist(x[m:], l2_nbin=10, spanlike=h1)
        plot_hist(h1)
        h1 += h2
        plot_hist(h1)
        h = Hist(x, l2_nbin=10)
        assert h1 == h


if __name__ == '__main__':
    testme(nrep=1, size=16384)
