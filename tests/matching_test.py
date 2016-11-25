from unittest import TestCase

from zxcvbn import matching


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
        assert matching.tra(string, map) == result, "translates '%s' to '%s' with provided charmap" % (string, result)
