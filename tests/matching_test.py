from unittest import TestCase

from zxcvbn import adjacency_graphs
from zxcvbn import matching


# takes a pattern and list of prefixes/suffixes
# returns a bunch of variants of that pattern embedded
# with each possible prefix/suffix combination, including no prefix/suffix
# returns a list of triplets [variant, i, j] where [i,j] is the start/end of the
# pattern, inclusive
def genpws(pattern, prefixes, suffixes):
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
        pattern_names = [pattern_names] * len(patterns)

    is_equal_len_args = len(pattern_names) == len(patterns) == len(ijs)
    for prop, lst in props.items():
        # props is structured as: keys that points to list of values
        if not is_equal_len_args or len(lst) != len(patterns):
            raise Exception('unequal argument lists to check_matches')

    msg = "%s: len(matches) == %s" % (prefix, len(patterns))
    assert len(matches) == len(patterns), msg
    for k in range(len(patterns)):
        match = matches[k]
        pattern_name = pattern_names[k]
        pattern = patterns[k]
        i, j = ijs[k]
        msg = "%s: matches[%s]['pattern'] == '%s'" % (prefix, k, pattern_name)
        assert match['pattern'] == pattern_name, msg

        msg = "%s: matches[%s] should have [i, j] of [%s, %s]" % (
            prefix, k, i, j)
        assert [match['i'], match['j']] == [i, j], msg

        msg = "%s: matches[%s]['token'] == '%s'" % (prefix, k, pattern)
        assert match['token'] == pattern, msg

        for prop_name, prop_list in props.items():
            prop_msg = prop_list[k]
            if isinstance(prop_msg, str):
                prop_msg = "'%s'" % prop_msg
            msg = "%s: matches[%s].%s == %s" % (prefix, k, prop_name, prop_msg)
            assert match[prop_name] == prop_list[k], msg


def test_build_ranked_dict():
    rd = matching.build_ranked_dict(['a', 'b', 'c', ])
    assert rd == {
        'a': 1,
        'b': 2,
        'c': 3,
    }


def test_add_frequency_lists():
    matching.add_frequency_lists({
        'test_words': ['qidkviflkdoejjfkd', 'sjdshfidssdkdjdhfkl']
    })

    assert 'test_words' in matching.RANKED_DICTIONARIES
    assert matching.RANKED_DICTIONARIES['test_words'] == {
        'qidkviflkdoejjfkd': 1,
        'sjdshfidssdkdjdhfkl': 2,
    }


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
            'asdf1234&*': 5,
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
    for password, i, j in genpws(word, prefixes, suffixes):
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


def test_reverse_dictionary_matching():
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


def test_l33t_matching():
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


def test_spatial_matching():
    for password in ['', '/', 'qw', '*/']:
        msg = "doesn't match 1- and 2-character spatial patterns"
        assert matching.spatial_match(password) == [], msg

    # for testing, make a subgraph that contains a single keyboard
    _graphs = {'qwerty': adjacency_graphs.ADJACENCY_GRAPHS['qwerty']}
    pattern = '6tfGHJ'
    matches = matching.spatial_match("rz!%s%%z" % pattern, _graphs)
    msg = "matches against spatial patterns surrounded by non-spatial patterns"
    check_matches(msg, matches, 'spatial', [pattern],
                  [[3, 3 + len(pattern) - 1]],
                  {
                      'graph': ['qwerty'],
                      'turns': [2],
                      'shifted_count': [3],
                  })

    for pattern, keyboard, turns, shifts in [
        ['12345', 'qwerty', 1, 0],
        ['@WSX', 'qwerty', 1, 4],
        ['6tfGHJ', 'qwerty', 2, 3],
        ['hGFd', 'qwerty', 1, 2],
        ['/;p09876yhn', 'qwerty', 3, 0],
        ['Xdr%', 'qwerty', 1, 2],
        ['159-', 'keypad', 1, 0],
        ['*84', 'keypad', 1, 0],
        ['/8520', 'keypad', 1, 0],
        ['369', 'keypad', 1, 0],
        ['/963.', 'mac_keypad', 1, 0],
        ['*-632.0214', 'mac_keypad', 9, 0],
        ['aoEP%yIxkjq:', 'dvorak', 4, 5],
        [';qoaOQ:Aoq;a', 'dvorak', 11, 4],
    ]:
        _graphs = {keyboard: adjacency_graphs.ADJACENCY_GRAPHS[keyboard]}
        matches = matching.spatial_match(pattern, _graphs)
        msg = "matches '%s' as a %s pattern" % (pattern, keyboard)
        check_matches(msg, matches, 'spatial', [pattern],
                      [[0, len(pattern) - 1]],
                      {
                          'graph': [keyboard],
                          'turns': [turns],
                          'shifted_count': [shifts],
                      })


def test_sequence_matching():
    for password in ['', 'a', '1']:
        msg = "doesn't match length-#{len(password)} sequences"
        assert matching.sequence_match(password) == [], msg

    matches = matching.sequence_match('abcbabc')
    msg = "matches overlapping patterns"
    check_matches(msg, matches, 'sequence', ['abc', 'cba', 'abc'],
                  [[0, 2], [2, 4], [4, 6]],
                  {'ascending': [True, False, True]})

    prefixes = ['!', '22']
    suffixes = ['!', '22']
    pattern = 'jihg'
    for password, i, j in genpws(pattern, prefixes, suffixes):
        matches = matching.sequence_match(password)
        msg = 'matches embedded sequence patterns'
        check_matches(msg, matches, 'sequence', [pattern], [[i, j]],
                      {
                          'sequence_name': ['lower'],
                          'ascending': [False],
                      })

    for [pattern, name, is_ascending] in [
        ['ABC', 'upper', True],
        ['CBA', 'upper', False],
        ['PQR', 'upper', True],
        ['RQP', 'upper', False],
        ['XYZ', 'upper', True],
        ['ZYX', 'upper', False],
        ['abcd', 'lower', True],
        ['dcba', 'lower', False],
        ['jihg', 'lower', False],
        ['wxyz', 'lower', True],
        ['zxvt', 'lower', False],
        ['0369', 'digits', True],
        ['97531', 'digits', False],
    ]:
        matches = matching.sequence_match(pattern)
        msg = "matches '#{pattern}' as a '#{name}' sequence"
        check_matches(msg, matches, 'sequence', [pattern],
                      [[0, len(pattern) - 1]],
                      {
                          'sequence_name': [name],
                          'ascending': [is_ascending],
                      })


def test_repeat_matching():
    for password in ['', '#']:
        msg = "doesn't match length-%s repeat patterns" % len(password)
        assert matching.repeat_match(password) == [], msg

    # test single-character repeats
    prefixes = ['@', 'y4@']
    suffixes = ['u', 'u%7']
    pattern = '&&&&&'
    for password, i, j in genpws(pattern, prefixes, suffixes):
        matches = matching.repeat_match(password)
        msg = "matches embedded repeat patterns"
        check_matches(msg, matches, 'repeat', [pattern], [[i, j]],
                      {'base_token': ['&']})

    for length in [3, 12]:
        for chr in ['a', 'Z', '4', '&']:
            pattern = chr * (length + 1)
            matches = matching.repeat_match(pattern)
            msg = "matches repeats with base character '%s'" % chr
            check_matches(msg, matches, 'repeat', [pattern],
                          [[0, len(pattern) - 1]],
                          {'base_token': [chr]})

    matches = matching.repeat_match('BBB1111aaaaa@@@@@@')
    patterns = ['BBB', '1111', 'aaaaa', '@@@@@@']
    msg = 'matches multiple adjacent repeats'
    check_matches(msg, matches, 'repeat', patterns,
                  [[0, 2], [3, 6], [7, 11], [12, 17]],
                  {'base_token': ['B', '1', 'a', '@']})

    matches = matching.repeat_match('2818BBBbzsdf1111@*&@!aaaaaEUDA@@@@@@1729')
    msg = 'matches multiple repeats with non-repeats in-between'
    check_matches(msg, matches, 'repeat', patterns,
                  [[4, 6], [12, 15], [21, 25], [30, 35]],
                  {'base_token': ['B', '1', 'a', '@']})

    # test multi-character repeats
    pattern = 'abab'
    matches = matching.repeat_match(pattern)
    msg = 'matches multi-character repeat pattern'
    check_matches(msg, matches, 'repeat', [pattern], [[0, len(pattern) - 1]],
                  {'base_token': ['ab']})

    pattern = 'aabaab'
    matches = matching.repeat_match(pattern)
    msg = 'matches aabaab as a repeat instead of the aa prefix'
    check_matches(msg, matches, 'repeat', [pattern], [[0, len(pattern) - 1]],
                  {'base_token': ['aab']})

    pattern = 'abababab'
    matches = matching.repeat_match(pattern)
    msg = 'identifies ab as repeat string, even though abab is also repeated'
    check_matches(msg, matches, 'repeat', [pattern], [[0, len(pattern) - 1]],
                  {'base_token': ['ab']})


def test_regex_matching():
    for pattern, name in [
        ['1922', 'recent_year'],
        ['2017', 'recent_year'],
    ]:
        matches = matching.regex_match(pattern)
        msg = "matches #{pattern} as a #{name} pattern"
        check_matches(
            msg, matches, 'regex', [pattern],
            [[0, len(pattern) - 1]],
            {'regex_name': [name]}
        )


def test_date_matching():
    for sep in ['', ' ', '-', '/', '\\', '_', '.']:
        password = "13%s2%s1921" % (sep, sep)
        matches = matching.date_match(password)
        msg = "matches dates that use '%s' as a separator" % sep
        check_matches(msg, matches, 'date', [password],
                      [[0, len(password) - 1]],
                      {
                          'separator': [sep],
                          'year': [1921],
                          'month': [2],
                          'day': [13],
                      })

    for order in ['mdy', 'dmy', 'ymd', 'ydm']:
        d, m, y = 8, 8, 88
        password = order.replace('y', str(y)).replace('m', str(m)).replace('d', str(d))
        matches = matching.date_match(password)
        msg = "matches dates with '%s' format" % order
        check_matches(msg, matches, 'date', [password],
                      [[0, len(password) - 1]],
                      {
                          'separator': [''],
                          'year': [1988],
                          'month': [8],
                          'day': [8],
                      })

    password = '111504'
    matches = matching.date_match(password)
    msg = "matches the date with year closest to REFERENCE_YEAR when ambiguous"
    check_matches(msg, matches, 'date', [password], [[0, len(password) - 1]],
                  {
                      'separator': [''],
                      'year': [2004],  # picks '04' -> 2004 as year, not '1504'
                      'month': [11],
                      'day': [15],
                  })

    for day, month, year in [
        [1, 1, 1999],
        [11, 8, 2000],
        [9, 12, 2005],
        [22, 11, 1551],
    ]:
        password = "%s%s%s" % (year, month, day)
        matches = matching.date_match(password)
        msg = "matches %s" % password
        check_matches(msg, matches, 'date', [password],
                      [[0, len(password) - 1]],
                      {
                          'separator': [''],
                          'year': [year],
                      })
        password = "%s.%s.%s" % (year, month, day)
        matches = matching.date_match(password)
        msg = "matches %s" % password
        check_matches(msg, matches, 'date', [password],
                      [[0, len(password) - 1]],
                      {
                          'separator': ['.'],
                          'year': [year],
                      })

    password = "02/02/02"
    matches = matching.date_match(password)
    msg = "matches zero-padded dates"
    check_matches(msg, matches, 'date', [password], [[0, len(password) - 1]],
                  {
                      'separator': ['/'],
                      'year': [2002],
                      'month': [2],
                      'day': [2],
                  })

    prefixes = ['a', 'ab']
    suffixes = ['!']
    pattern = '1/1/91'
    for password, i, j in genpws(pattern, prefixes, suffixes):
        matches = matching.date_match(password)
        msg = "matches embedded dates"
        check_matches(msg, matches, 'date', [pattern], [[i, j]],
                      {
                          'year': [1991],
                          'month': [1],
                          'day': [1],
                      })

    matches = matching.date_match('12/20/1991.12.20')
    msg = "matches overlapping dates"
    check_matches(msg, matches, 'date', ['12/20/1991', '1991.12.20'],
                  [[0, 9], [6, 15]],
                  {
                      'separator': ['/', '.'],
                      'year': [1991, 1991],
                      'month': [12, 12],
                      'day': [20, 20],
                  })

    matches = matching.date_match('912/20/919')
    msg = "matches dates padded by non-ambiguous digits"
    check_matches(msg, matches, 'date', ['12/20/91'], [[1, 8]],
                  {
                      'separator': ['/'],
                      'year': [1991],
                      'month': [12],
                      'day': [20],
                  })


def test_omnimatch():
    assert matching.omnimatch('') == [], "doesn't match ''"
    password = 'r0sebudmaelstrom11/20/91aaaa'
    matches = matching.omnimatch(password)
    for [pattern_name, [i, j]] in [
        ['dictionary', [0, 6]],
        ['dictionary', [7, 15]],
        ['date', [16, 23]],
        ['repeat', [24, 27]],
    ]:
        included = False
        for match in matches:
            if match['i'] == i and match['j'] == j \
                    and match['pattern'] == pattern_name:
                included = True
        msg = "for %s, matches a %s pattern at [%s, %s]" % (
            password, pattern_name, i, j
        )
        assert included, msg
