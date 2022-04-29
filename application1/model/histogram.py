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

flintmax = 2 ** 53  # largest consecutive integer in float64


def myfloor(x, lg2):
    """floor(x * 2**lg2), as integer"""
    return np.floor(x * 2.0 ** lg2).astype(np.int64)  # int32 will overflow


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

    def __init__(self, x: np.ndarray, l2_nbin=14, spanlike=None):
        """calculates histogram of vector x with 2**l2nbin number of bins. If another histogram spanlike is given,
        its span will be used to avoid useless resizing when merging or comparing later.
        """

        self.l2_nbin = l2_nbin
        self.n_bin = 2 ** l2_nbin

        assert x.size < 2 ** 32  # counts are uint32, enough for 1 year at 50Hz
        assert x.ndim < 2
        self.n_tot = x.size

        if not x.size:  # emtpy histo
            self.const_val = None
            self.check()
            return

        x_min = x.min()
        x_max = x.max()

        if not np.isfinite(x_max - x_min):  # no need to do np.isfinite(x).any()
            raise ValueError('Can not yet handle non-finite samples')
            # TODO: keep separate count of non-finite samples, and tolerate

        if x_min == x_max:  # constant data
            self.const_val = x_min
            self.check()
            return
        self.const_val = None

        # tiny bit extra, for x_min-x_max = 2**n, you need nbin+1
        margin = (self.n_bin + 2) / self.n_bin
        self.l2_span = int(np.ceil(np.log2((x_max - x_min) * margin)))

        if spanlike:
            if spanlike.isexpanded:  # make span at least as big as other to avoid resizing
                self.l2_span = max(self.l2_span, spanlike.l2_span)
            else:
                spanlike = None

        # get bin indices for x_min and x_max on infinite scale
        self.i_min = myfloor(x_min, self.l2_nbin - self.l2_span)
        self.i_max = myfloor(x_max, self.l2_nbin - self.l2_span)
        if max(self.i_max, -self.i_min) > flintmax:
            raise ValueError('Data are badly scaled')
        assert self.i_max - self.i_min < self.n_bin

        # get bin indices for data on infinite scale
        ind = myfloor(x, self.l2_nbin - self.l2_span)

        if (spanlike and self.l2_span == spanlike.l2_span and
                spanlike.i_offset <= self.i_min and
                self.i_max < spanlike.i_offset + self.n_bin):
            # use offset of spanlike to avoid shifting
            assert self.n_bin == spanlike.nbin
            self.i_offset = spanlike.i_offset
        else:  # center histogram around data
            self.i_offset = (self.i_min + self.i_max + 1 - self.n_bin) // 2

        # shift bin indices to range 0 .. nbin and make histogram
        # note: old numpy version does not support minlenght
        self.counts = np.bincount(ind - self.i_offset, minlength=self.n_bin).astype(np.uint32)

        # self.counts = np.zeros(self.nbin, dtype=np.uint32)
        # cnts = np.bincount(ind - self.i_offset)  # fails if any(ind < i_offset)
        # self.counts[:len(cnts)] = cnts  # fails if any(ind >= i_offset + nbin)

        self.check()

    # derived properties are always calculated
    @property
    def isempty(self):
        return self.n_tot == 0

    @property
    def isconst(self):
        return self.const_val is not None

    @property
    def isexpanded(self):
        return self.n_tot > 0 and self.const_val is None

    @property
    def span(self):
        return 2.0 ** self.l2_span

    @property
    def offset(self):
        return self.i_offset * 2.0 ** (self.l2_span - self.l2_nbin)

    @property
    def xgrid(self):
        """returns grid for plotting"""
        xg = np.arange(self.n_bin, dtype=float)
        xg *= 2.0 ** (self.l2_span - self.l2_nbin)
        xg += self.offset
        return xg

    @property
    def cdf(self):
        """returns cumulative distribution function. Note that the
        last point should be 1 by definition and that a first
        implicit point equal to zero is missing"""
        assert self.isexpanded
        return self.counts.cumsum() / self.n_tot

    def __repr__(self):
        if self.isempty:
            return 'empty histogram'
        if self.isconst:
            return 'histogram of %i points with constant value %g' % (
                self.n_tot, self.const_val)
        return 'histogram of %i points, span = %g, offset = %g' % (
            self.n_tot, self.span, self.offset)

    def enlarge(self):
        """increase span by 2 and merge bins"""
        assert self.isexpanded

        newcounts = np.zeros(self.n_bin, dtype=np.uint32)
        if self.i_offset % 2:  # odd
            newcounts[0] = self.counts[0]
            newcounts[1:self.n_bin // 2] = (self.counts[1:-1:2] +
                                           self.counts[2:-1:2])
            newcounts[self.n_bin // 2] = self.counts[-1]
        else:  # even
            newcounts[:self.n_bin // 2] = self.counts[::2] + self.counts[1::2]
        self.counts = newcounts

        """
        # in place version, might be illegal
        mid = self.nbin // 2
        cnt = self.counts
        if self.i_offset % 2:  # odd
            np.add(cnt[1:-1:2], cnt[2:-1:2], out=cnt[1:mid])
            cnt[mid] = cnt[-1]
            cnt[mid+1:] = 0
        else:  # even
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

        if ishift < 0:  # histogram shifts left, counts go right
            assert not np.any(self.counts[ishift:]), 'bins not emtpy'
        elif ishift > 0:  # histogram shifts right, counts go left
            assert not np.any(self.counts[:ishift]), 'bins not emtpy'
        self.counts = myroll(self.counts, -ishift)
        self.i_offset += ishift
        self.check()

    def expand(self, l2_span):
        """if histo is constant, expand it to one with given span"""
        if not self.isconst:  # empty or already expanded
            return
        self.l2_span = l2_span
        self.i_min = myfloor(self.const_val, self.l2_nbin - self.l2_span)
        self.i_max = self.i_min
        self.i_offset = self.i_min - self.n_bin // 2  # center window
        self.counts = np.zeros(self.n_bin, dtype=np.uint32)
        self.counts[self.n_bin // 2] = self.n_tot
        self.const_val = None
        self.check()

    def check(self):
        """checks various invariants of internal state of histogram"""
        # return #speedup
        if self.isempty:  # empty histogram
            assert self.const_val is None
        elif self.isexpanded:  # normal histogram
            istart = self.i_min - self.i_offset
            istop = self.i_max - self.i_offset
            assert 0 <= istart < self.n_bin
            assert 0 <= istop < self.n_bin
            assert self.counts[istart] > 0
            assert self.counts[istop] > 0
            assert (self.counts[:istart] == 0).all()
            assert (self.counts[istop + 1:] == 0).all()
            assert self.n_tot == self.counts.sum()
        else:  # constant histogram
            assert self.isconst

    def __eq__(self, other):
        """only for debugging purposes, this might alter both self and other"""
        if self.isempty and other.isempty:
            return True
        if self.n_tot != other.n_tot:
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

        # special case empty histos
        if other.isempty:
            return self
        if self.isempty:
            return other

        self.align(other)

        if self.isexpanded:
            self.counts += other.counts
            self.i_min = min(self.i_min, other.i_min)
            self.i_max = max(self.i_max, other.i_max)
        else:
            assert self.const_val == other.const_val
        self.n_tot += other.n_tot
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
        assert self.n_bin == other.n_bin

        # handle constant histograms
        if self.isconst:
            if other.isconst:  # both constant
                if self.const_val == other.const_val:
                    return  # already aligned
                else:
                    l2_span = int(np.ceil(np.log2(abs(
                        self.const_val - other.const_val))))
                    self.expand(l2_span)
                    other.expand(l2_span)

            else:  # self constant, other normal
                self.expand(other.l2_span)
        elif other.isconst:  # other constant, self normal
            other.expand(self.l2_span)
        assert self.isexpanded and other.isexpanded

        # increase span of histo with smallest span until they are equal
        smallest, biggest = sorted([self, other], key=lambda h: h.l2_span)
        while smallest.l2_span < biggest.l2_span:
            smallest.enlarge()

        # if windows cannot fit in one aligned histogram, enlarge both
        while (max(self.i_max, other.i_max) -
               min(self.i_min, other.i_min)) >= self.n_bin:
            self.enlarge()
            other.enlarge()
        assert self.l2_span == other.l2_span

        # shift to align
        if self.i_offset <= other.i_min and other.i_max < self.i_offset + self.n_bin:
            # only need to shift other
            other.shift(self.i_offset - other.i_offset)
        else:  # need to shift both
            i_offset_new = (min(self.i_min, other.i_min) +
                            max(self.i_max, other.i_max) +
                            1 - self.n_bin) // 2
            self.shift(i_offset_new - self.i_offset)  # checked at end
            other.shift(i_offset_new - other.i_offset)
        assert self.i_offset == other.i_offset


def plot_hist(h, **kwargs):
    import matplotlib.pyplot as plt
    plt.bar(h.xgrid, h.counts, width=h.span / h.n_bin, **kwargs)
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
    testme(nrep=1, size=1024)
