from unittest import TestCase

from zxcvbn import matching


def genpws(pattern, prefixes, suffixes):
    prefixes = prefixes
    suffixes = suffixes
    for lst in [prefixes, suffixes]:
        if '' not in lst:
            lst.insert(0, '')
    result = []
    for prefix in prefixes:
        for suffix in suffixes:
            i, j = len(prefix), len(prefix) + len(pattern) - 1
            result.append([prefix + pattern + suffix, i, j])
    return result


def check_matches(prefix, matches, pattern_names, patterns, ijs, props):
    if isinstance(pattern_names, str):
        # shortcut: if checking for a list of the same type of patterns,
        # allow passing a string 'pat' instead of array ['pat', 'pat', ...]
        pattern_names *= (len(patterns) - 1)

    is_equal_len_args = len(pattern_names) == len(patterns) == len(ijs)
    for prop, lst in props.items():
        # props is structured as: keys that points to list of values
        is_equal_len_args = is_equal_len_args and (len(lst) == len(patterns))
        if not is_equal_len_args:
            raise Exception('unequal argument lists to check_matches')

    msg = "%s: len(matches) == %s" % (prefix, len(patterns))
    assert len(matches) == len(patterns), msg
    for k in range(len(patterns)):
        match = matches[k]
        pattern_name = pattern_names[k]
        pattern = patterns[k]
        i, j = ijs[k]
        msg = "%s: matches[%s].pattern == '%s'" % (prefix, k, pattern_name)
        assert match.pattern == pattern_name, msg
        msg = "%s: matches[%s] should have [i, j] of [%s, %s]" % (
            prefix, k, i, j)
        assert [match.i, match.j] == [i, j], msg
        msg = "%s: matches[%s].token == '%s'" % (prefix, k, pattern)
        assert match.token == pattern, msg
        for prop_name, prop_list in props.items():
            prop_msg = prop_list[k]
            if isinstance(prop_msg, basestring):
                prop_msg = "'%s'" % prop_msg
            msg = "%s: matches[%s].%s == %s" % (prefix, k, prop_name, prop_msg)
            assert match[prop_name] == prop_list[k], msg


def test_matching_utils():
    chr_map = {
        'a': 'A',
        'b': 'B',
    }

    for string, map, result in [
        ['a', chr_map, 'A'],
        ['c', chr_map, 'c'],
        ['ab', chr_map, 'AB'],
        ['abc', chr_map, 'ABc'],
        ['aa', chr_map, 'AA'],
        ['abab', chr_map, 'ABAB'],
        ['', chr_map, ''],
        ['', {}, ''],
        ['abc', {}, 'abc'],
    ]:
        assert matching.translate(string, map) == result, \
            "translates '%s' to '%s' with provided charmap" % (string, result)


def test_dictionary_matching():
    def dm(pw):
        return matching.dictionary_match(pw, test_dicts)

    test_dicts = {
        'd1': {
            'motherboard': 1,
            'mother': 2,
            'board': 3,
            'abcd': 4,
            'cdef': 5,
        },
        'd2': {
            'z': 1,
            '8': 2,
            '99': 3,
            '$': 4,
            'asdf1234&': 5,
        }
    }

    matches = dm('motherboard')
    patterns = ['mother', 'motherboard', 'board']
    msg = 'matches words that contain other words'
    check_matches(msg, matches, 'dictionary', patterns,
                  [[0, 5], [0, 10], [6, 10]], {
                      'matched_word': ['mother', 'motherboard', 'board'],
                      'rank': [2, 1, 3],
                      'dictionary_name': ['d1', 'd1', 'd1'],
                  })

    matches = dm('abcdef')
    patterns = ['abcd', 'cdef']
    msg = "matches multiple words when they overlap"
    check_matches(msg, matches, 'dictionary', patterns, [[0, 3], [2, 5]], {
        'matched_word': ['abcd', 'cdef'],
        'rank': [4, 5],
        'dictionary_name': ['d1', 'd1'],
    })

    matches = dm('BoaRdZ')
    patterns = ['BoaRd', 'Z']
    msg = "ignores uppercasing"
    check_matches(msg, matches, 'dictionary', patterns, [[0, 4], [5, 5]], {
        'matched_word': ['board', 'z'],
        'rank': [3, 1],
        'dictionary_name': ['d1', 'd2'],
    })

    prefixes = ['q', '%%']
    suffixes = ['%', 'qq']
    word = 'asdf1234&*'
    for [password, i, j] in genpws(word, prefixes, suffixes):
        matches = dm(password)
        msg = "identifies words surrounded by non-words"
        check_matches(msg, matches, 'dictionary', [word], [[i, j]], {
            'matched_word': [word],
            'rank': [5],
            'dictionary_name': ['d2'],
        })

    for name, dict in test_dicts.items():
        for word, rank in dict.items():
            if word is 'motherboard':
                continue  # skip words that contain others
            matches = dm(word)
            msg = "matches against all words in provided dictionaries"
            check_matches(msg, matches, 'dictionary', [word],
                          [[0, len(word) - 1]], {
                              'matched_word': [word],
                              'rank': [rank],
                              'dictionary_name': [name],
                          })

    # test the default dictionaries
    matches = matching.dictionary_match('wow')
    patterns = ['wow']
    ijs = [[0, 2]]
    msg = "default dictionaries"
    check_matches(msg, matches, 'dictionary', patterns, ijs, {
        'matched_word': patterns,
        'rank': [322],
        'dictionary_name': ['us_tv_and_film'],
    })

    matching.set_user_input_dictionary('foo', 'bar')
    matches = matching.dictionary_match('foobar')
    matches = [match for match in matches
               if match['dictionary_name'] == 'user_inputs']
    msg = "matches with provided user input dictionary"
    check_matches(msg, matches, 'dictionary', ['foo', 'bar'],
                  [[0, 2], [3, 5]], {
                      'matched_word': ['foo', 'bar'],
                      'rank': [1, 2],
                  })


def reverse_dictionary_matching():
    test_dicts = {
        'd1': {
            '123': 1,
            '321': 2,
            '456': 3,
            '654': 4,
        }
    }
    password = '0123456789'
    matches = matching.reverse_dictionary_match(password, test_dicts)
    msg = 'matches against reversed words'
    check_matches(msg, matches, 'dictionary', ['123', '456'], [[1, 3], [4, 6]],
                  {
                      'matched_word': ['321', '654'],
                      'reversed': [True, True],
                      'dictionary_name': ['d1', 'd1'],
                      'rank': [2, 4],
                  })


def l33t_matching():
    test_table = {
        'a': ['4', '@'],
        'c': ['(', '{', '[', '<'],
        'g': ['6', '9'],
        'o': ['0'],
    }
    for pw, expected in [
        ['', {}],
        ['abcdefgo123578!#$&*)]}>', {}],
        ['a', {}],
        ['4', {'a': ['4']}],
        ['4@', {'a': ['4', '@']}],
        ['4({60', {'a': ['4'], 'c': ['(', '{'], 'g': ['6'], 'o': ['0']}],
    ]:
        msg = "reduces l33t table to only the substitutions that a password might be employing"
        assert matching.relevant_l33t_subtable(pw, test_table) == expected, msg

    for table, subs in [
        [{}, [{}]],
        [{'a': ['@']}, [{'@': 'a'}]],
        [{'a': ['@', '4']}, [{'@': 'a'}, {'4': 'a'}]],
        [{'a': ['@', '4'], 'c': ['(']},
         [{'@': 'a', '(': 'c'}, {'4': 'a', '(': 'c'}]],
    ]:
        msg = "enumerates the different sets of l33t substitutions a password might be using"
        assert matching.enumerate_l33t_subs(table) == subs, msg

    def lm(pw):
        return matching.l33t_match(pw, dicts, test_table)

    dicts = {
        'words': {
            'aac': 1,
            'password': 3,
            'paassword': 4,
            'asdf0': 5,
        },
        'words2': {
            'cgo': 1,
        }
    }
    assert lm('') == [], "doesn't match ''"
    assert lm('password') == [], "doesn't match pure dictionary words"
    for password, pattern, word, dictionary_name, rank, ij, sub in [
        ['p4ssword', 'p4ssword', 'password', 'words', 3, [0, 7], {'4': 'a'}],
        ['p@ssw0rd', 'p@ssw0rd', 'password', 'words', 3, [0, 7],
         {'@': 'a', '0': 'o'}],
        ['aSdfO{G0asDfO', '{G0', 'cgo', 'words2', 1, [5, 7],
         {'{': 'c', '0': 'o'}],
    ]:
        msg = "matches against common l33t substitutions"
        check_matches(msg, lm(password), 'dictionary', [pattern], [ij],
                      {
                          'l33t': [True],
                          'sub': [sub],
                          'matched_word': [word],
                          'rank': [rank],
                          'dictionary_name': [dictionary_name],
                          })

    matches = lm('@a(go{G0')
    msg = "matches against overlapping l33t patterns"
    check_matches(msg, matches, 'dictionary', ['@a(', '(go', '{G0'],
                  [[0, 2], [2, 4], [5, 7]], {
                      'l33t': [True, True, True],
                      'sub': [{'@': 'a', '(': 'c'}, {'(': 'c'},
                              {'{': 'c', '0': 'o'}],
                      'matched_word': ['aac', 'cgo', 'cgo'],
                      'rank': [1, 1, 1],
                      'dictionary_name': ['words', 'words2', 'words2'],
                  })

    msg = "doesn't match when multiple l33t substitutions are needed for the same letter"
    assert lm('p4@ssword') == [], msg

    msg = "doesn't match single-character l33ted words"
    matches = matching.l33t_match('4 1 @')
    assert matches == [], msg

    # known issue: subsets of substitutions aren't tried.
    # for long inputs, trying every subset of every possible substitution could quickly get large,
    # but there might be a performant way to fix.
    # (so in this example: {'4': a, '0': 'o'} is detected as a possible sub,
    # but the subset {'4': 'a'} isn't tried, missing the match for asdf0.)
    # TODO: consider partially fixing by trying all subsets of size 1 and maybe 2
    msg = "doesn't match with subsets of possible l33t substitutions"
    assert lm('4sdf0') == [], msg
