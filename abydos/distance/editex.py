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

"""abydos.distance.editex.

The distance.editex module implements editex functions.
"""

from __future__ import division, unicode_literals

from unicodedata import normalize as unicode_normalize

from numpy import int as np_int
from numpy import zeros as np_zeros

from six import text_type
from six.moves import range

__all__ = ['dist_editex', 'editex', 'sim_editex']


def editex(src, tar, cost=(0, 1, 2), local=False):
    """Return the Editex distance between two strings.

    As described on pages 3 & 4 of :cite:`Zobel:1996`.

    The local variant is based on :cite:`Ring:2009`.

    :param str src: source string for comparison
    :param str tar: target string for comparison
    :param tuple cost: a 3-tuple representing the cost of the four possible
        edits:
        match, same-group, and mismatch respectively (by default: (0, 1, 2))
    :param bool local: if True, the local variant of Editex is used
    :returns: Editex distance
    :rtype: int

    >>> editex('cat', 'hat')
    2
    >>> editex('Niall', 'Neil')
    2
    >>> editex('aluminum', 'Catalan')
    12
    >>> editex('ATCG', 'TAGC')
    6
    """
    match_cost, group_cost, mismatch_cost = cost
    letter_groups = ({'A', 'E', 'I', 'O', 'U', 'Y'},
                     {'B', 'P'},
                     {'C', 'K', 'Q'},
                     {'D', 'T'},
                     {'L', 'R'},
                     {'M', 'N'},
                     {'G', 'J'},
                     {'F', 'P', 'V'},
                     {'S', 'X', 'Z'},
                     {'C', 'S', 'Z'})
    all_letters = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'J', 'K', 'L', 'M',
                   'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'X', 'Y', 'Z'}

    def r_cost(ch1, ch2):
        """Return r(a,b) according to Zobel & Dart's definition."""
        if ch1 == ch2:
            return match_cost
        if ch1 in all_letters and ch2 in all_letters:
            for group in letter_groups:
                if ch1 in group and ch2 in group:
                    return group_cost
        return mismatch_cost

    def d_cost(ch1, ch2):
        """Return d(a,b) according to Zobel & Dart's definition."""
        if ch1 != ch2 and (ch1 == 'H' or ch1 == 'W'):
            return group_cost
        return r_cost(ch1, ch2)

    # convert both src & tar to NFKD normalized unicode
    src = unicode_normalize('NFKD', text_type(src.upper()))
    tar = unicode_normalize('NFKD', text_type(tar.upper()))
    # convert ß to SS (for Python2)
    src = src.replace('ß', 'SS')
    tar = tar.replace('ß', 'SS')

    if src == tar:
        return 0
    if not src:
        return len(tar) * mismatch_cost
    if not tar:
        return len(src) * mismatch_cost

    d_mat = np_zeros((len(src)+1, len(tar)+1), dtype=np_int)
    lens = len(src)
    lent = len(tar)
    src = ' '+src
    tar = ' '+tar

    if not local:
        for i in range(1, lens+1):
            d_mat[i, 0] = d_mat[i-1, 0] + d_cost(src[i-1], src[i])
    for j in range(1, lent+1):
        d_mat[0, j] = d_mat[0, j-1] + d_cost(tar[j-1], tar[j])

    for i in range(1, lens+1):
        for j in range(1, lent+1):
            d_mat[i, j] = min(d_mat[i-1, j] + d_cost(src[i-1], src[i]),
                              d_mat[i, j-1] + d_cost(tar[j-1], tar[j]),
                              d_mat[i-1, j-1] + r_cost(src[i], tar[j]))

    return d_mat[lens, lent]


def dist_editex(src, tar, cost=(0, 1, 2), local=False):
    """Return the normalized Editex distance between two strings.

    The Editex distance is normalized by dividing the Editex distance
    (calculated by any of the three supported methods) by the greater of
    the number of characters in src times the cost of a delete and
    the number of characters in tar times the cost of an insert.
    For the case in which all operations have :math:`cost = 1`, this is
    equivalent to the greater of the length of the two strings src & tar.

    :param str src: source string for comparison
    :param str tar: target string for comparison
    :param tuple cost: a 3-tuple representing the cost of the four possible
        edits:
        match, same-group, and mismatch respectively (by default: (0, 1, 2))
    :param bool local: if True, the local variant of Editex is used
    :returns: normalized Editex distance
    :rtype: float

    >>> round(dist_editex('cat', 'hat'), 12)
    0.333333333333
    >>> round(dist_editex('Niall', 'Neil'), 12)
    0.2
    >>> dist_editex('aluminum', 'Catalan')
    0.75
    >>> dist_editex('ATCG', 'TAGC')
    0.75
    """
    if src == tar:
        return 0
    mismatch_cost = cost[2]
    return (editex(src, tar, cost, local) /
            (max(len(src)*mismatch_cost, len(tar)*mismatch_cost)))


def sim_editex(src, tar, cost=(0, 1, 2), local=False):
    """Return the normalized Editex similarity of two strings.

    The Editex similarity is the complement of Editex distance:
    :math:`sim_{Editex} = 1 - dist_{Editex}`.

    :param str src: source string for comparison
    :param str tar: target string for comparison
    :param tuple cost: a 3-tuple representing the cost of the four possible
        edits:
        match, same-group, and mismatch respectively (by default: (0, 1, 2))
    :param bool local: if True, the local variant of Editex is used
    :returns: normalized Editex similarity
    :rtype: float

    >>> round(sim_editex('cat', 'hat'), 12)
    0.666666666667
    >>> round(sim_editex('Niall', 'Neil'), 12)
    0.8
    >>> sim_editex('aluminum', 'Catalan')
    0.25
    >>> sim_editex('ATCG', 'TAGC')
    0.25
    """
    return 1 - dist_editex(src, tar, cost, local)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
