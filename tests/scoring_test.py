import pytest

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


def test_most_guessable_match_sequence():
    def m(i, j, guesses):
        return {
            'i': i,
            'j': j,
            'guesses': guesses
        }

    password = '0123456789'
    exclude_additive = True

    msg = "returns one bruteforce match given an empty match sequence: %s"
    result = scoring.most_guessable_match_sequence(password, [])
    assert len(result['sequence']) == 1, msg % "len(result) == 1"
    m0 = result['sequence'][0]
    assert m0['pattern'] == 'bruteforce', \
        msg % "match['pattern']== 'bruteforce'"
    assert m0['token'] == password, msg % ("match['token']== %s" % password)
    assert [m0['i'], m0['j']] == [0, 9], msg % (
        "[i, j] == [%s, %s]" % (m0['i'], m0['j'])
    )

    msg = "returns match + bruteforce when match " \
          "covers a prefix of password: %s"
    m0 = m(0, 5, 1)
    matches = [m0]
    result = scoring.most_guessable_match_sequence(password, matches,
                                                   exclude_additive)
    assert result.sequence.length == 2, \
        msg % "result.match.sequence.length == 2"
    assert result.sequence[0] == m0, \
        msg % "first match is the provided match object"
    m1 = result.sequence[1]
    assert m1.pattern == 'bruteforce', msg % "second match is bruteforce"
    assert [m1.i, m1.j] == [6, 9], \
        msg % "second match covers full suffix after first match"

    msg = "returns bruteforce + match when match covers a suffix: %s"
    m1 = m(3, 9, 1)
    matches = [m1]
    result = scoring.most_guessable_match_sequence(password, matches,
                                                   exclude_additive)
    assert result.sequence.length == 2, \
        msg % "result.match.sequence.length == 2"
    m0 = result.sequence[0]
    assert m0.pattern == 'bruteforce', msg % "first match is bruteforce"
    assert [m0.i, m0.j] == [0, 2], \
        msg % "first match covers full prefix before second match"
    assert result.sequence[1] == m1, \
        msg % "second match is the provided match object"

    msg = "returns bruteforce + match + bruteforce " \
          "when match covers an infix: %s"
    matches = [m1] = [m(1, 8, 1)]
    result = scoring.most_guessable_match_sequence(password, matches,
                                                   exclude_additive)
    assert result.sequence.length == 3, msg % "result.length == 3"
    assert result.sequence[
               1] == m1, msg % "middle match is the provided match object"
    m0 = result.sequence[0]
    m2 = result.sequence[2]
    assert m0.pattern == 'bruteforce', msg % "first match is bruteforce"
    assert m2.pattern == 'bruteforce', msg % "third match is bruteforce"
    assert [m0.i, m0.j] == [0, 0], \
        msg % "first match covers full prefix before second match"
    assert [m2.i, m2.j] == [9, 9], \
        msg % "third match covers full suffix after second match"

    msg = "chooses lower-guesses match given two matches of the same span: %s"
    matches = [m0, m1] = [m(0, 9, 1), m(0, 9, 2)]
    result = scoring.most_guessable_match_sequence(password, matches,
                                                   exclude_additive)
    assert result.sequence.length == 1, msg % "result.length == 1"
    assert result.sequence[0] == m0, msg % "result.sequence[0] == m0"
    # make sure ordering doesn't matter
    m0.guesses = 3
    result = scoring.most_guessable_match_sequence(password, matches,
                                                   exclude_additive)
    assert result.sequence.length == 1, msg % "result.length == 1"
    assert result.sequence[0] == m1, msg % "result.sequence[0] == m1"

    msg = "when m0 covers m1 and m2, " \
          "choose [m0] when m0 < m1 * m2 * fact(2): %s"
    matches = [m0, m1, m2] = [m(0, 9, 3), m(0, 3, 2), m(4, 9, 1)]
    result = scoring.most_guessable_match_sequence(password, matches,
                                                   exclude_additive)
    assert result.guesses == 3, msg % "total guesses == 3"
    assert result.sequence == [m0], msg % "sequence is [m0]"

    msg = "when m0 covers m1 and m2, " \
          "choose [m1, m2] when m0 > m1 * m2 * fact(2): %s"
    m0.guesses = 5
    result = scoring.most_guessable_match_sequence(password, matches,
                                                   exclude_additive)
    assert result.guesses == 4, msg % "total guesses == 4"
    assert result.sequence == [m1, m2], msg % "sequence is [m1, m2]"


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
