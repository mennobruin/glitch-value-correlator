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

from core.config import ConfigurationManager

LOG = ConfigurationManager.get_logger(__name__)

flintmax = 2 ** 53  # largest consecutive integer in float64


def myfloor(x, lg2):
    """floor(x * 2**lg2), as integer"""
    return np.floor(x * 2.0 ** lg2).astype(np.int64)  # int32 will overflow


def myroll(x, shift):
    """faster version of np.roll for vectors"""
    shift %= x.size
    return np.concatenate((x[-shift:], x[:-shift]))


class Hist(object):
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

    def __init__(self, x, l2nbin=14, spanlike=None):
        """calculates histogram of vector x with 2**l2nbin number of bins. If another histogram spanlike is given,
        its span will be used to avoid useless resizing when merging or comparing later.
        """

        self.l2nbin = l2nbin
        self.nbin = 2 ** l2nbin

        x = np.asarray(x)
        assert x.size < 2 ** 32  # counts are uint32, enough for 1 year at 50Hz
        assert x.ndim < 2
        self.ntot = x.size

        if not x.size:  # emtpy histo
            self.const_val = None
            self.check()
            return

        xmin = x.min()
        xmax = x.max()

        if not np.isfinite(xmax - xmin):  # no need to do np.isfinite(x).any()
            raise ValueError('Can not yet handle non-finite samples')
            # TODO: keep separate count of non-finite samples, and tolerate

        if xmin == xmax:  # constant data
            self.const_val = xmin
            self.check()
            return
        self.const_val = None

        # tiny bit extra, for xmin-xmax = 2**n, you need nbin+1
        margin = (self.nbin + 2) / self.nbin
        self.l2span = int(np.ceil(np.log2((xmax - xmin) * margin)))

        # only use spanlike if it is expanded
        if spanlike and not spanlike.isexpanded:
            spanlike = None

        if spanlike:  # make span at least as big as other to avoid resizing
            self.l2span = max(self.l2span, spanlike.l2span)

        # get bin indices for xmin and xmax on infinite scale
        self.imin = myfloor(xmin, self.l2nbin - self.l2span)
        self.imax = myfloor(xmax, self.l2nbin - self.l2span)
        if max(self.imax, -self.imin) > flintmax:
            raise ValueError('Data are badly scaled')
        assert self.imax - self.imin < self.nbin

        # get bin indices for data on infite scale
        ind = myfloor(x, self.l2nbin - self.l2span)

        if (spanlike and self.l2span == spanlike.l2span and
                spanlike.ioffset <= self.imin and
                self.imax < spanlike.ioffset + self.nbin):
            # use offset of spanlike to avoid shifting
            assert self.nbin == spanlike.nbin
            self.ioffset = spanlike.ioffset
        else:  # center histogram around data
            self.ioffset = (self.imin + self.imax + 1 - self.nbin) // 2

        # shift bin indices to range 0 .. nbin and make histogram
        # note: old numpy version does not support minlenght
        # self.counts = np.bincount(ind, minlength=self.nbin).astype(np.uint32)

        self.counts = np.zeros(self.nbin, dtype=np.uint32)
        cnts = np.bincount(ind - self.ioffset)  # fails if any(ind < ioffset)
        self.counts[:len(cnts)] = cnts  # fails if any(ind >= ioffset + nbin)

        self.check()

    # derived properties are always calculated
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
        return 2.0 ** self.l2span

    @property
    def offset(self):
        return self.ioffset * 2.0 ** (self.l2span - self.l2nbin)

    @property
    def xgrid(self):
        """returns grid for plotting"""
        xg = np.arange(self.nbin, dtype=float)
        xg *= 2.0 ** (self.l2span - self.l2nbin)
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
        if self.ioffset % 2:  # odd
            newcounts[0] = self.counts[0]
            newcounts[1:self.nbin // 2] = (self.counts[1:-1:2] +
                                           self.counts[2:-1:2])
            newcounts[self.nbin // 2] = self.counts[-1]
        else:  # even
            newcounts[:self.nbin // 2] = self.counts[::2] + self.counts[1::2]
        self.counts = newcounts

        """
        # in place version, might be illegal
        mid = self.nbin // 2
        cnt = self.counts
        if self.ioffset % 2:  # odd
            np.add(cnt[1:-1:2], cnt[2:-1:2], out=cnt[1:mid])
            cnt[mid] = cnt[-1]
            cnt[mid+1:] = 0
        else:  # even
            np.add(cnt[::2], cnt[1::2], out=cnt[:mid])
            cnt[mid:] = 0
        """

        self.l2span += 1
        self.ioffset //= 2
        self.imin //= 2
        self.imax //= 2
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
        self.ioffset += ishift
        self.check()

    def expand(self, l2span):
        """if histo is constant, expand it to one with given span"""
        if not self.isconst:  # empty or already expanded
            return
        self.l2span = l2span
        self.imin = myfloor(self.const_val, self.l2nbin - self.l2span)
        self.imax = self.imin
        self.ioffset = self.imin - self.nbin // 2  # center window
        self.counts = np.zeros(self.nbin, dtype=np.uint32)
        self.counts[self.nbin // 2] = self.ntot
        self.const_val = None
        self.check()

    def check(self):
        """checks various invariants of internal state of histogram"""
        # return #speedup
        if self.isempty:  # empty histogram
            assert self.const_val is None
        elif self.isexpanded:  # normal histogram
            istart = self.imin - self.ioffset
            istop = self.imax - self.ioffset
            assert 0 <= istart < self.nbin
            assert 0 <= istop < self.nbin
            assert self.counts[istart] > 0
            assert self.counts[istop] > 0
            assert (self.counts[:istart] == 0).all()
            assert (self.counts[istop + 1:] == 0).all()
            assert self.ntot == self.counts.sum()
        else:  # constant histogram
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

        # special case empty histos
        if other.isempty:
            return self
        if self.isempty:
            return other

        self.align(other)

        if self.isexpanded:
            self.counts += other.counts
            self.imin = min(self.imin, other.imin)
            self.imax = max(self.imax, other.imax)
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

        # handle constant histograms
        if self.isconst:
            if other.isconst:  # both constant
                if self.const_val == other.const_val:
                    return  # already aligned
                else:
                    l2span = int(np.ceil(np.log2(abs(
                        self.const_val - other.const_val))))
                    self.expand(l2span)
                    other.expand(l2span)

            else:  # self constant, other normal
                self.expand(other.l2span)
        elif other.isconst:  # other constant, self normal
            other.expand(self.l2span)
        assert self.isexpanded and other.isexpanded

        # increase span of histo with smallest span until they are equal
        smallest, biggest = sorted([self, other], key=lambda h: h.l2span)
        while smallest.l2span < biggest.l2span:
            smallest.enlarge()

        # if windows cannot fit in one aligned histogram, enlarge both
        while (max(self.imax, other.imax) -
               min(self.imin, other.imin)) >= self.nbin:
            self.enlarge()
            other.enlarge()
        assert self.l2span == other.l2span

        # shift to align
        if self.ioffset <= other.imin and other.imax < self.ioffset + self.nbin:
            # only need to shift other
            other.shift(self.ioffset - other.ioffset)
        else:  # need to shift both
            ioffset_new = (min(self.imin, other.imin) +
                           max(self.imax, other.imax) +
                           1 - self.nbin) // 2
            self.shift(ioffset_new - self.ioffset)  # checked at end
            other.shift(ioffset_new - other.ioffset)
        assert self.ioffset == other.ioffset


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
        h1 = Hist(x[:m], l2nbin=10)
        h2 = Hist(x[m:], l2nbin=10, spanlike=h1)
        plot_hist(h1)
        h1 += h2
        plot_hist(h1)
        h = Hist(x, l2nbin=10)
        assert h1 == h


if __name__ == '__main__':
    testme(nrep=1, size=1024)
