# -*- coding: utf-8 -*-

# Copyright 2014-2018 by Christopher C. Little.
# This file is part of Abydos.
#
# Abydos is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Abydos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Abydos. If not, see <http://www.gnu.org/licenses/>.

"""abydos.distance.mra.

The distance.mra module implements the Match Rating Algorithm's distance
measure.
"""

from __future__ import division, unicode_literals

from six.moves import range

from ..phonetic.mra import mra


__all__ = ['dist_mra', 'mra_compare', 'sim_mra']


def mra_compare(src, tar):
    """Return the MRA comparison rating of two strings.

    The Western Airlines Surname Match Rating Algorithm comparison rating, as
    presented on page 18 of :cite:`Moore:1977`.

    :param str src: source string for comparison
    :param str tar: target string for comparison
    :returns: MRA comparison rating
    :rtype: int

    >>> mra_compare('cat', 'hat')
    5
    >>> mra_compare('Niall', 'Neil')
    6
    >>> mra_compare('aluminum', 'Catalan')
    0
    >>> mra_compare('ATCG', 'TAGC')
    5
    """
    if src == tar:
        return 6
    if src == '' or tar == '':
        return 0
    src = list(mra(src))
    tar = list(mra(tar))

    if abs(len(src)-len(tar)) > 2:
        return 0

    length_sum = len(src) + len(tar)
    if length_sum < 5:
        min_rating = 5
    elif length_sum < 8:
        min_rating = 4
    elif length_sum < 12:
        min_rating = 3
    else:
        min_rating = 2

    for _ in range(2):
        new_src = []
        new_tar = []
        minlen = min(len(src), len(tar))
        for i in range(minlen):
            if src[i] != tar[i]:
                new_src.append(src[i])
                new_tar.append(tar[i])
        src = new_src+src[minlen:]
        tar = new_tar+tar[minlen:]
        src.reverse()
        tar.reverse()

    similarity = 6 - max(len(src), len(tar))

    if similarity >= min_rating:
        return similarity
    return 0


def sim_mra(src, tar):
    """Return the normalized MRA similarity of two strings.

    This is the MRA normalized to :math:`[0, 1]`, given that MRA itself is
    constrained to the range :math:`[0, 6]`.

    :param str src: source string for comparison
    :param str tar: target string for comparison
    :returns: normalized MRA similarity
    :rtype: float

    >>> sim_mra('cat', 'hat')
    0.8333333333333334
    >>> sim_mra('Niall', 'Neil')
    1.0
    >>> sim_mra('aluminum', 'Catalan')
    0.0
    >>> sim_mra('ATCG', 'TAGC')
    0.8333333333333334
    """
    return mra_compare(src, tar)/6


def dist_mra(src, tar):
    """Return the normalized MRA distance between two strings.

    MRA distance is the complement of MRA similarity:
    :math:`dist_{MRA} = 1 - sim_{MRA}`.

    :param str src: source string for comparison
    :param str tar: target string for comparison
    :returns: normalized MRA distance
    :rtype: float

    >>> dist_mra('cat', 'hat')
    0.16666666666666663
    >>> dist_mra('Niall', 'Neil')
    0.0
    >>> dist_mra('aluminum', 'Catalan')
    1.0
    >>> dist_mra('ATCG', 'TAGC')
    0.16666666666666663
    """
    return 1 - sim_mra(src, tar)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
