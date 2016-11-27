from unittest import TestCase

from zxcvbn import matching


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
        msg = "%s: matches[%s] should have [i, j] of [%s, %s]" % (prefix, k, i, j)
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
        matched_word: ['board', 'z'],
        rank: [3, 1],
        dictionary_name: ['d1', 'd2'],
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
