# -*- coding: utf-8 -*-

# Copyright 2018 by Christopher C. Little.
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

"""abydos.phonetic.fr.

The phonetic.fr module implements phonetic algorithms intended for French,
including:

    - FONEM
    - an early version of Henry Code
"""

from __future__ import unicode_literals

from re import compile as re_compile
from unicodedata import normalize as unicode_normalize

from six import text_type

__all__ = ['fonem', 'henry_early']


def fonem(word):
    """Return the FONEM code of a word.

    FONEM is a phonetic algorithm designed for French (particularly surnames in
    Saguenay, Canada), defined in :cite:`Bouchard:1981`.

    Guillaume Plique's Javascript implementation :cite:`Plique:2018` at
    https://github.com/Yomguithereal/talisman/blob/master/src/phonetics/french/fonem.js
    was also consulted for this implementation.

    :param str word: the word to transform
    :returns: the FONEM code
    :rtype: str

    >>> fonem('Marchand')
    'MARCHEN'
    >>> fonem('Beaulieu')
    'BOLIEU'
    >>> fonem('Beaumont')
    'BOMON'
    >>> fonem('Legrand')
    'LEGREN'
    >>> fonem('Pelletier')
    'PELETIER'
    """
    # I don't see a sane way of doing this without regexps :(
    rule_table = {
        # Vowels & groups of vowels
        'V-1':     (re_compile('E?AU'), 'O'),
        'V-2,5':   (re_compile('(E?AU|O)L[TX]$'), 'O'),
        'V-3,4':   (re_compile('E?AU[TX]$'), 'O'),
        'V-6':     (re_compile('E?AUL?D$'), 'O'),
        'V-7':     (re_compile(r'(?<!G)AY$'), 'E'),
        'V-8':     (re_compile('EUX$'), 'EU'),
        'V-9':     (re_compile('EY(?=$|[BCDFGHJKLMNPQRSTVWXZ])'), 'E'),
        'V-10':    ('Y', 'I'),
        'V-11':    (re_compile('(?<=[AEIOUY])I(?=[AEIOUY])'), 'Y'),
        'V-12':    (re_compile('(?<=[AEIOUY])ILL'), 'Y'),
        'V-13':    (re_compile('OU(?=[AEOU]|I(?!LL))'), 'W'),
        'V-14':    (re_compile(r'([AEIOUY])(?=\1)'), ''),
        # Nasal vowels
        'V-15':    (re_compile('[AE]M(?=[BCDFGHJKLMPQRSTVWXZ])(?!$)'), 'EN'),
        'V-16':    (re_compile('OM(?=[BCDFGHJKLMPQRSTVWXZ])'), 'ON'),
        'V-17':    (re_compile('AN(?=[BCDFGHJKLMNPQRSTVWXZ])'), 'EN'),
        'V-18':    (re_compile('(AI[MN]|EIN)(?=[BCDFGHJKLMNPQRSTVWXZ]|$)'),
                    'IN'),
        'V-19':    (re_compile('B(O|U|OU)RNE?$'), 'BURN'),
        'V-20':    (re_compile('(^IM|(?<=[BCDFGHJKLMNPQRSTVWXZ])' +
                               'IM(?=[BCDFGHJKLMPQRSTVWXZ]))'), 'IN'),
        # Consonants and groups of consonants
        'C-1':     ('BV', 'V'),
        'C-2':     (re_compile('(?<=[AEIOUY])C(?=[EIY])'), 'SS'),
        'C-3':     (re_compile('(?<=[BDFGHJKLMNPQRSTVWZ])C(?=[EIY])'), 'S'),
        'C-4':     (re_compile('^C(?=[EIY])'), 'S'),
        'C-5':     (re_compile('^C(?=[OUA])'), 'K'),
        'C-6':     (re_compile('(?<=[AEIOUY])C$'), 'K'),
        'C-7':     (re_compile('C(?=[BDFGJKLMNPQRSTVWXZ])'), 'K'),
        'C-8':     (re_compile('CC(?=[AOU])'), 'K'),
        'C-9':     (re_compile('CC(?=[EIY])'), 'X'),
        'C-10':    (re_compile('G(?=[EIY])'), 'J'),
        'C-11':    (re_compile('GA(?=I?[MN])'), 'G#'),
        'C-12':    (re_compile('GE(O|AU)'), 'JO'),
        'C-13':    (re_compile('GNI(?=[AEIOUY])'), 'GN'),
        'C-14':    (re_compile('(?<![PCS])H'), ''),
        'C-15':    ('JEA', 'JA'),
        'C-16':    (re_compile('^MAC(?=[BCDFGHJKLMNPQRSTVWXZ])'), 'MA#'),
        'C-17':    (re_compile('^MC'), 'MA#'),
        'C-18':    ('PH', 'F'),
        'C-19':    ('QU', 'K'),
        'C-20':    (re_compile('^SC(?=[EIY])'), 'S'),
        'C-21':    (re_compile('(?<=.)SC(?=[EIY])'), 'SS'),
        'C-22':    (re_compile('(?<=.)SC(?=[AOU])'), 'SK'),
        'C-23':    ('SH', 'CH'),
        'C-24':    (re_compile('TIA$'), 'SSIA'),
        'C-25':    (re_compile('(?<=[AIOUY])W'), ''),
        'C-26':    (re_compile('X[CSZ]'), 'X'),
        'C-27':    (re_compile('(?<=[AEIOUY])Z|(?<=[BCDFGHJKLMNPQRSTVWXZ])' +
                               'Z(?=[BCDFGHJKLMNPQRSTVWXZ])'), 'S'),
        'C-28':    (re_compile(r'([BDFGHJKMNPQRTVWXZ])\1'), r'\1'),
        'C-28a':   (re_compile('CC(?=[BCDFGHJKLMNPQRSTVWXZ]|$)'), 'C'),
        'C-28b':   (re_compile('((?<=[BCDFGHJKLMNPQRSTVWXZ])|^)SS'), 'S'),
        'C-28bb':  (re_compile('SS(?=[BCDFGHJKLMNPQRSTVWXZ]|$)'), 'S'),
        'C-28c':   (re_compile('((?<=[^I])|^)LL'), 'L'),
        'C-28d':   (re_compile('ILE$'), 'ILLE'),
        'C-29':    (re_compile('(ILS|[CS]H|[MN]P|R[CFKLNSX])$|([BCDFGHJKL' +
                               'MNPQRSTVWXZ])[BCDFGHJKLMNPQRSTVWXZ]$'),
                    lambda m: (m.group(1) or '') + (m.group(2) or '')),
        'C-30,32': (re_compile('^(SA?INT?|SEI[NM]|CINQ?|ST)(?!E)-?'), 'ST-'),
        'C-31,33': (re_compile('^(SAINTE|STE)-?'), 'STE-'),
        # Rules to undo rule bleeding prevention in C-11, C-16, C-17
        'C-34':    ('G#', 'GA'),
        'C-35':    ('MA#', 'MAC')
    }
    rule_order = [
        'V-14', 'C-28', 'C-28a', 'C-28b', 'C-28bb', 'C-28c', 'C-28d',
        'C-12',
        'C-8', 'C-9', 'C-10',
        'C-16', 'C-17', 'C-2', 'C-3', 'C-7',
        'V-2,5', 'V-3,4', 'V-6',
        'V-1', 'C-14',
        'C-31,33', 'C-30,32',
        'C-11', 'V-15', 'V-17', 'V-18',
        'V-7', 'V-8', 'V-9', 'V-10', 'V-11', 'V-12', 'V-13', 'V-16',
        'V-19', 'V-20',
        'C-1', 'C-4', 'C-5', 'C-6', 'C-13', 'C-15',
        'C-18', 'C-19', 'C-20', 'C-21', 'C-22', 'C-23', 'C-24',
        'C-25', 'C-26', 'C-27',
        'C-29',
        'V-14', 'C-28', 'C-28a', 'C-28b', 'C-28bb', 'C-28c', 'C-28d',
        'C-34', 'C-35'
    ]

    # normalize, upper-case, and filter non-French letters
    word = unicode_normalize('NFKD', text_type(word.upper()))
    word = word.translate({198: 'AE', 338: 'OE'})
    word = ''.join(c for c in word if c in
                   {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                    'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                    'Y', 'Z', '-'})

    for rule in rule_order:
        regex, repl = rule_table[rule]
        if isinstance(regex, text_type):
            word = word.replace(regex, repl)
        else:
            word = regex.sub(repl, word)

    return word


def henry_early(word, max_length=3):
    """Calculate the early version of the Henry code for a word.

    The early version of Henry coding is given in :cite:`Legare:1972`. This is
    different from the later version defined in :cite:`Henry:1976`.

    :param str word: the word to transform
    :param int max_length: the length of the code returned (defaults to 3)
    :returns: the early Henry code
    :rtype: str

    >>> henry_early('Marchand')
    'MRC'
    >>> henry_early('Beaulieu')
    'BL'
    >>> henry_early('Beaumont')
    'BM'
    >>> henry_early('Legrand')
    'LGR'
    >>> henry_early('Pelletier')
    'PLT'
    """
    _cons = {'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q',
             'R', 'S', 'T', 'V', 'W', 'X', 'Z'}
    _vows = {'A', 'E', 'I', 'O', 'U', 'Y'}
    _diph = {'AI': 'E', 'AY': 'E', 'EI': 'E', 'AU': 'O', 'OI': 'O', 'OU': 'O',
             'EU': 'U'}
    # _unaltered = {'B', 'D', 'F', 'J', 'K', 'L', 'M', 'N', 'R', 'T', 'V'}
    _simple = {'W': 'V', 'X': 'S', 'Z': 'S'}

    word = unicode_normalize('NFKD', text_type(word.upper()))
    word = ''.join(c for c in word if c in
                   {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                    'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                    'Y', 'Z'})

    if not word:
        return ''

    # Rule Ia seems to be covered entirely in II

    # Rule Ib
    if word[0] in _vows:
        # Ib1
        if (((word[1:2] in _cons-{'M', 'N'} and word[2:3] in _cons) or
             (word[1:2] in _cons and word[2:3] not in _cons))):
            if word[0] == 'Y':
                word = 'I'+word[1:]
        # Ib2
        elif word[1:2] in {'M', 'N'} and word[2:3] in _cons:
            if word[0] == 'E':
                word = 'A'+word[1:]
            elif word[0] in {'I', 'U', 'Y'}:
                word = 'E'+word[1:]
        # Ib3
        elif word[:2] in _diph:
            word = _diph[word[:2]]+word[2:]
        # Ib4
        elif word[1:2] in _vows and word[0] == 'Y':
            word = 'I' + word[1:]

    code = ''
    skip = 0

    # Rule II
    for pos, char in enumerate(word):
        nxch = word[pos+1:pos+2]
        prev = word[pos-1:pos]

        if skip:
            skip -= 1
        elif char in _vows:
            code += char
        # IIc
        elif char == nxch:
            skip = 1
            code += char
        elif word[pos:pos+2] in {'CQ', 'DT', 'SC'}:
            continue
        # IIb
        elif char in _simple:
            code += _simple[char]
        elif char in {'C', 'G', 'P', 'Q', 'S'}:
            if char == 'C':
                if nxch in {'A', 'O', 'U', 'L', 'R'}:
                    code += 'K'
                elif nxch in {'E', 'I', 'Y'}:
                    code += 'S'
                elif nxch == 'H':
                    if word[pos+2:pos+3] in _vows:
                        code += 'C'
                    else:  # CHR, CHL, etc.
                        code += 'K'
                else:
                    code += 'C'
            elif char == 'G':
                if nxch in {'A', 'O', 'U', 'L', 'R'}:
                    code += 'G'
                elif nxch in {'E', 'I', 'Y'}:
                    code += 'J'
                elif nxch == 'N':
                    code += 'N'
            elif char == 'P':
                if nxch != 'H':
                    code += 'P'
                else:
                    code += 'F'
            elif char == 'Q':
                if word[pos+1:pos+3] in {'UE', 'UI', 'UY'}:
                    code += 'G'
                else:  # QUA, QUO, etc.
                    code += 'K'
            else:  # S...
                if word[pos:pos+6] == 'SAINTE':
                    code += 'X'
                    skip = 5
                elif word[pos:pos+5] == 'SAINT':
                    code += 'X'
                    skip = 4
                elif word[pos:pos+3] == 'STE':
                    code += 'X'
                    skip = 2
                elif word[pos:pos+2] == 'ST':
                    code += 'X'
                    skip = 1
                elif nxch in _cons:
                    continue
                else:
                    code += 'S'
        # IId
        elif char == 'H' and prev in _cons:
            continue
        elif char in _cons-{'L', 'R'} and nxch in _cons-{'L', 'R'}:
            continue
        elif char == 'L' and nxch in {'M', 'N'}:
            continue
        elif char in {'M', 'N'} and prev in _vows and nxch in _cons:
            continue
        # IIa
        else:
            code += char

    # IIe1
    if code[-4:] in {'AULT', 'EULT', 'OULT'}:
        code = code[:-2]
    # The following are blocked by rules above
    # elif code[-4:-3] in _vows and code[-3:] == 'MPS':
    #    code = code[:-3]
    # elif code[-3:-2] in _vows and code[-2:] in {'MB', 'MP', 'ND',
    #                                             'NS', 'NT'}:
    #    code = code[:-2]
    elif code[-2:-1] == 'R' and code[-1:] in _cons:
        code = code[:-1]
    # IIe2
    elif code[-2:-1] in _vows and code[-1:] in {'D', 'M', 'N', 'S', 'T'}:
        code = code[:-1]
    elif code[-2:] == 'ER':
        code = code[:-1]

    # Drop non-initial vowels
    code = code[:1]+code[1:].translate({65: '', 69: '', 73: '', 79: '', 85: '',
                                        89: ''})

    if max_length != -1:
            code = code[:max_length]

    return code


if __name__ == '__main__':
    import doctest
    doctest.testmod()
