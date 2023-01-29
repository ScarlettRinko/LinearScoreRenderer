SOLFEGE_PITCH: list[int] = [-1000, 0, 2, 4, 5, 7, 9, 11]

NOTATION_PITCH: dict[str, int] = {'.': 12, ',': -12, '#': 1, 'b': -1}
NOTATION_BEATS: dict[str, int] = {'-': 1, '~': 1.5, '=': 2, '+': 4, '*': 0.5, '^': 0.25, "'": 0.125}

CHORD_INTERVAL_TO_INDEX = {1: 0, 3: 1, 5: 2, 7: 3, 9: 4, 11: 5, 13: 6}
CHORD_INDEX_TO_PITCH = [0, 4, 7, 11, 14, 17, 21]

CHORD_FAMILIES = ['M', 'mM', 'm', 'dim', 'augM', 'aug', '']
CHORD_TYPES = {'7': 7, '9': 9, '11': 11, '13': 13, '': 3}
CHORD_FAMILY_NOTES: dict[str, dict[int, int]] = {
    'M':    [0,  0,  0,  0, None, None, None],
    'm':    [0, -1,  0, -1, None, None, None],
    'dim':  [0, -1, -1, -2, None, None, None],
    'aug':  [0,  0,  1, -1, None, None, None],
    '':     [0,  0,  0, -1, None, None, None],
    'mM':   [0, -1,  0,  0, None, None, None],
    'augM': [0,  0,  1,  0, None, None, None]
}

RE_PATTERN_CHORD_SUFFIX = '(add\d+|omit\d+|sus2?|#\d+|b\d+)'