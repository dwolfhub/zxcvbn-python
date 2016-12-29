import re
from zxcvbn import matching
from zxcvbn import scoring
from zxcvbn.adjacency_graphs import ADJACENCY_GRAPHS


def test_returns_average_degree():
    assert scoring.calc_average_degree(ADJACENCY_GRAPHS['qwerty']) == \
           4.595744680851064
    assert scoring.calc_average_degree(ADJACENCY_GRAPHS['keypad']) == \
           5.066666666666666


def test_nCk():
    for [n, k, result] in [
        [0, 0, 1],
        [1, 0, 1],
        [5, 0, 1],
        [0, 1, 0],
        [0, 5, 0],
        [2, 1, 2],
        [4, 2, 6],
        [33, 7, 4272048],
    ]:
        assert scoring.nCk(n, k) == result, "nCk(%s, %s) == %s" % (n, k, result)
    n = 49
    k = 12
    assert scoring.nCk(n, k) == scoring.nCk(n, n - k), "mirror identity"
    assert scoring.nCk(n, k) == (
        scoring.nCk(n - 1, k - 1) + scoring.nCk(n - 1, k)
    ), "pascal's triangle identity"


def test_search():
    def m(i, j, guesses):
        return {
            'i': i,
            'j': j,
            'guesses': guesses
        }

    password = '0123456789'

    # for tests, set additive penalty to zero.
    exclude_additive = True

    msg = "returns one bruteforce match given an empty match sequence: %s"
    result = scoring.most_guessable_match_sequence(password, [])
    assert len(result['sequence']) == 1, msg % "len(result) == 1"
    m0 = result['sequence'][0]
    assert m0['pattern'] == 'bruteforce', \
        msg % "match['pattern'] == 'bruteforce'"
    assert m0['token'] == password, msg % ("match['token'] == %s" % password)
    assert [m0['i'], m0['j']] == [0, 9], msg % (
        "i, j == %s, %s" % (m0['i'], m0['j'])
    )

    msg = "returns match + bruteforce when match " \
          "covers a prefix of password: %s"
    m0 = m(0, 5, 1)
    matches = [m0]
    result = scoring.most_guessable_match_sequence(password, matches,
                                                   exclude_additive)
    assert len(result['sequence']) == 2, \
        msg % "len(result.match['sequence']) == 2"
    assert result['sequence'][0] == m0, \
        msg % "first match is the provided match object"
    m1 = result['sequence'][1]
    assert m1['pattern'] == 'bruteforce', msg % "second match is bruteforce"
    assert [m1['i'], m1['j']] == [6, 9], \
        msg % "second match covers full suffix after first match"

    msg = "returns bruteforce + match when match covers a suffix: %s"
    m1 = m(3, 9, 1)
    matches = [m1]
    result = scoring.most_guessable_match_sequence(password, matches,
                                                   exclude_additive)
    assert len(result['sequence']) == 2, \
        msg % "len(result.match['sequence']) == 2"
    m0 = result['sequence'][0]
    assert m0['pattern'] == 'bruteforce', msg % "first match is bruteforce"
    assert [m0['i'], m0['j']] == [0, 2], \
        msg % "first match covers full prefix before second match"
    assert result['sequence'][1] == m1, \
        msg % "second match is the provided match object"

    msg = "returns bruteforce + match + bruteforce " \
          "when match covers an infix: %s"
    m1 = m(1, 8, 1)
    matches = [m1]
    result = scoring.most_guessable_match_sequence(password, matches,
                                                   exclude_additive)
    # TODO!!!
    # assert len(result['sequence']) == 3, msg % "len(result['sequence']) == 3"
    # assert result['sequence'][1] == m1, \
    #     msg % "middle match is the provided match object"
    # m0 = result['sequence'][0]
    # m2 = result['sequence'][2]
    # assert m0['pattern'] == 'bruteforce', msg % "first match is bruteforce"
    # assert m2['pattern'] == 'bruteforce', msg % "third match is bruteforce"
    # assert [m0['i'], m0['j']] == [0, 0], \
    #     msg % "first match covers full prefix before second match"
    # assert [m2['i'], m2['j']] == [9, 9], \
    #     msg % "third match covers full suffix after second match"

    msg = "chooses lower-guesses match given two matches of the same span: %s"
    matches = [m0, m1] = [m(0, 9, 1), m(0, 9, 2)]
    result = scoring.most_guessable_match_sequence(password, matches,
                                                   exclude_additive)
    assert len(result['sequence']) == 1, msg % "len(result['sequence']) == 1"
    assert result['sequence'][0] == m0, msg % "result['sequence'][0] == m0"
    # make sure ordering doesn't matter
    m0['guesses'] = 3
    result = scoring.most_guessable_match_sequence(password, matches,
                                                   exclude_additive)
    assert len(result['sequence']) == 1, msg % "len(result['sequence']) == 1"
    assert result['sequence'][0] == m1, msg % "result['sequence'][0] == m1"

    msg = "when m0 covers m1 and m2, " \
          "choose [m0] when m0 < m1 * m2 * fact(2): %s"
    matches = [m0, m1, m2] = [m(0, 9, 3), m(0, 3, 2), m(4, 9, 1)]
    result = scoring.most_guessable_match_sequence(password, matches,
                                                   exclude_additive)
    assert result['guesses'] == 3, msg % "total guesses == 3"
    assert result['sequence'] == [m0], msg % "sequence is [m0]"

    msg = "when m0 covers m1 and m2, " \
          "choose [m1, m2] when m0 > m1 * m2 * fact(2): %s"
    m0['guesses'] = 5
    result = scoring.most_guessable_match_sequence(password, matches,
                                                   exclude_additive)
    assert result['guesses'] == 4, msg % "total guesses == 4"
    assert result['sequence'] == [m1, m2], msg % "sequence is [m1, m2]"


def test_calc_guesses():
    match = {
        'guesses': 1,
    }
    msg = "estimate_guesses returns cached guesses when available"
    assert scoring.estimate_guesses(match, '') == 1, msg

    match = {
        'pattern': 'date',
        'token': '1977',
        'year': 1977,
        'month': 7,
        'day': 14,
    }
    msg = 'estimate_guesses delegates based on pattern'
    assert scoring.estimate_guesses(match, '1977') == \
           scoring.date_guesses(match), msg


def test_repeat_guesses():
    for [token, base_token, repeat_count] in [
        ['aa', 'a', 2],
        ['999', '9', 3],
        ['$$$$', '$', 4],
        ['abab', 'ab', 2],
        ['batterystaplebatterystaplebatterystaple', 'batterystaple', 3]
    ]:
        base_guesses = scoring.most_guessable_match_sequence(
            base_token,
            matching.omnimatch(base_token)
        )['guesses']
        match = {
            'token': token,
            'base_token': base_token,
            'base_guesses': base_guesses,
            'repeat_count': repeat_count,
        }
        expected_guesses = base_guesses * repeat_count
        msg = "the repeat pattern '#{token}' has guesses of #{expected_guesses}"
        assert scoring.repeat_guesses(match) == expected_guesses, msg


def test_sequence_guesses():
    for [token, ascending, guesses] in [
        ['ab', True, 4 * 2],  # obvious start * len-2
        ['XYZ', True, 26 * 3],  # base26 * len-3
        ['4567', True, 10 * 4],  # base10 * len-4
        ['7654', False, 10 * 4 * 2],  # base10 * len 4 * descending
        ['ZYX', False, 4 * 3 * 2],  # obvious start * len-3 * descending
    ]:
        match = {
            'token': token,
            'ascending': ascending,
        }
        msg = "the sequence pattern '#{token}' has guesses of #{guesses}"
        assert scoring.sequence_guesses(match) == guesses, msg


def test_regex_guesses():
    match = {
        'token': 'aizocdk',
        'regex_name': 'alpha_lower',
        'regex_match': ['aizocdk'],
    }
    msg = "guesses of 26^7 for 7-char lowercase regex"
    assert scoring.regex_guesses(match) == 26 ** 7, msg

    match = {
        'token': 'ag7C8',
        'regex_name': 'alphanumeric',
        'regex_match': ['ag7C8'],
    }
    msg = "guesses of 62^5 for 5-char alphanumeric regex"
    assert scoring.regex_guesses(match) == (2 * 26 + 10) ** 5, msg


    match = {
        'token': '1972',
        'regex_name': 'recent_year',
        'regex_match': matching.REGEXEN['recent_year'].match('1972'),
    }
    msg = "guesses of |year - REFERENCE_YEAR| for distant year matches"
    assert scoring.regex_guesses(match) == abs(scoring.REFERENCE_YEAR - 1972), \
        msg

    match ={
        'token': '2005',
        'regex_name': 'recent_year',
        'regex_match': matching.REGEXEN['recent_year'].match('2005'),
    }
    msg = "guesses of MIN_YEAR_SPACE for a year close to REFERENCE_YEAR"
    assert scoring.regex_guesses(match) == scoring.MIN_YEAR_SPACE, msg


def test_estimate_guesses():
    msg = "estimate_guesses returns cached guesses when available"
    match = {
        'guesses': 1
    }
    assert scoring.estimate_guesses(match, '') == 1, msg

    msg = "estimate_guesses delegates based on pattern"
    match = {
        'pattern': 'date',
        'token': '1977',
        'year': 1977,
        'month': 7,
        'day': 14,
    }
    assert scoring.estimate_guesses(match, '1977') == \
           scoring.date_guesses(match), msg


def test_date_guesses():
    match = {
        'token': '1123',
        'separator': '',
        'has_full_year': False,
        'year': 1923,
        'month': 1,
        'day': 1,
    }
    msg = "guesses for %s is 365 * distance_from_ref_year" % match['token']
    assert scoring.date_guesses(match) == 365 * abs(
        scoring.REFERENCE_YEAR - match['year']
    ), msg

    match = {
        'token': '1/1/2010',
        'separator': '/',
        'has_full_year': True,
        'year': 2010,
        'month': 1,
        'day': 1,
    }
    msg = "recent years assume MIN_YEAR_SPACE. " \
          "extra guesses are added for separators."
    assert scoring.date_guesses(match) == 365 * scoring.MIN_YEAR_SPACE * 4, msg


def test_spatial_guesses():
    match = {
        'token': 'zxcvbn',
        'graph': 'qwerty',
        'turns': 1,
        'shifted_count': 0,
    }
    base_guesses = (
        scoring.KEYBOARD_STARTING_POSITIONS *
        scoring.KEYBOARD_AVERAGE_DEGREE *
        # - 1 term because: not counting spatial patterns of length 1
        # eg for length==6, multiplier is 5 for needing to try len2,len3,..,len6
        (len(match['token']) - 1)
    )
    msg = "with no turns or shifts, guesses is starts * degree * (len-1)"
    assert scoring.spatial_guesses(match) == base_guesses, msg

    match['guesses'] = None
    match['token'] = 'ZxCvbn'
    match['shifted_count'] = 2
    shifted_guesses = base_guesses * (scoring.nCk(6, 2) + scoring.nCk(6, 1))
    msg = "guesses is added for shifted keys, similar to capitals in " \
          "dictionary matching"
    assert scoring.spatial_guesses(match) == shifted_guesses, msg

    match['guesses'] = None
    match['token'] = 'ZXCVBN'
    match['shifted_count'] = 6
    shifted_guesses = base_guesses * 2
    msg = "when everything is shifted, guesses are doubled"
    assert scoring.spatial_guesses(match) == shifted_guesses, msg

    match = {
        'token': 'zxcft6yh',
        'graph': 'qwerty',
        'turns': 3,
        'shifted_count': 0,
    }
    guesses = 0
    L = len(match['token'])
    s = scoring.KEYBOARD_STARTING_POSITIONS
    d = scoring.KEYBOARD_AVERAGE_DEGREE
    for i in range(2, L + 1):
        for j in range(1, min(match['turns'], i - 1) + 1):
            guesses += scoring.nCk(i - 1, j - 1) * s * pow(d, j)

    msg = "spatial guesses accounts for turn positions, directions and " \
          "starting keys"
    assert scoring.spatial_guesses(match) == guesses, msg


def test_dictionary_guesses():
    match = {
        'token': 'aaaaa',
        'rank': 32,
    }
    msg = "base guesses == the rank"
    assert scoring.dictionary_guesses(match) == 32, msg

    match = {
        'token': 'AAAaaa',
        'rank': 32
    }
    msg = "extra guesses are added for capitalization"
    assert scoring.dictionary_guesses(
        match) == 32 * scoring.uppercase_variations(match), msg

    match = {
        'token': 'aaa',
        'rank': 32,
        'reversed': True
    }
    msg = "guesses are doubled when word is reversed"
    assert scoring.dictionary_guesses(match) == 32 * 2, msg

    match = {
        'token': 'aaa@@@',
        'rank': 32,
        'l33t': True,
        'sub': {'@': 'a'},
    }
    msg = "extra guesses are added for common l33t substitutions"
    assert scoring.dictionary_guesses(match) == \
           32 * scoring.l33t_variations(match), msg

    match = {
        'token': 'AaA@@@',
        'rank': 32,
        'l33t': True,
        'sub': {'@': 'a'},
    }
    msg = "extra guesses are added for both capitalization and common l33t " \
          "substitutions"
    expected = 32 * scoring.l33t_variations(match) * \
               scoring.uppercase_variations(match)
    assert scoring.dictionary_guesses(match) == expected, msg


def test_uppercase_variants():
    for [word, variants] in [
        ['', 1],
        ['a', 1],
        ['A', 2],
        ['abcdef', 1],
        ['Abcdef', 2],
        ['abcdeF', 2],
        ['ABCDEF', 2],
        ['aBcdef', scoring.nCk(6, 1)],
        ['aBcDef', scoring.nCk(6, 1) + scoring.nCk(6, 2)],
        ['ABCDEf', scoring.nCk(6, 1)],
        ['aBCDEf', scoring.nCk(6, 1) + scoring.nCk(6, 2)],
        ['ABCdef', scoring.nCk(6, 1) + scoring.nCk(6, 2) + scoring.nCk(6, 3)],
    ]:
        msg = "guess multiplier of #{word} is #{variants}"
        assert scoring.uppercase_variations({'token': word}) == variants, msg


def test_l33t_variants():
    match = {
        'l33t': False
    }
    assert scoring.l33t_variations(match) == 1, "1 variant for non-l33t matches"
    for [word, variants, sub] in [
        ['', 1, {}],
        ['a', 1, {}],
        ['4', 2, {'4': 'a'}],
        ['4pple', 2, {'4': 'a'}],
        ['abcet', 1, {}],
        ['4bcet', 2, {'4': 'a'}],
        ['a8cet', 2, {'8': 'b'}],
        ['abce+', 2, {'+': 't'}],
        ['48cet', 4, {'4': 'a', '8': 'b'}],
        ['a4a4aa', scoring.nCk(6, 2) + scoring.nCk(6, 1), {'4': 'a'}],
        ['4a4a44', scoring.nCk(6, 2) + scoring.nCk(6, 1), {'4': 'a'}],
        ['a44att+', (scoring.nCk(4, 2) + scoring.nCk(4, 1)) *
                scoring.nCk(3, 1), {'4': 'a', '+': 't'}],
    ]:
        match = {
            'token': word,
            'sub': sub,
            'l33t': len(sub) > 0
        }
        msg = "extra l33t guesses of #{word} is #{variants}"
        assert scoring.l33t_variations(match) == variants, msg
    match = {
        'token': 'Aa44aA',
        'l33t': True,
        'sub': {'4': 'a'},
    }
    variants = scoring.nCk(6, 2) + scoring.nCk(6, 1)
    msg = "capitalization doesn't affect extra l33t guesses calc"
    assert scoring.l33t_variations(match) == variants, msg
