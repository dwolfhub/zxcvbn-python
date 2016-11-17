from zxcvbn import adjacency_graphs
from zxcvbn.frequency_lists import FREQUENCY_LISTS


def build_ranked_dict(ordered_list):
    result = {}
    i = 1
    for word in ordered_list:
        result[word] = i
        i += 1

    return result


RANKED_DICTIONARIES = {}
for name, lst in FREQUENCY_LISTS.items():
    RANKED_DICTIONARIES[name] = build_ranked_dict(lst)

GRAPHS = {
    'qwerty': adjacency_graphs.ADJACENCY_GRAPHS['qwerty'],
    'dvorak': adjacency_graphs.ADJACENCY_GRAPHS['dvorak'],
    'keypad': adjacency_graphs.ADJACENCY_GRAPHS['keypad'],
    'mac_keypad': adjacency_graphs.ADJACENCY_GRAPHS['mac_keypad'],
}

L33T_TABLE = {
    'a': ['4', '@'],
    'b': ['8'],
    'c': ['(', '{', '[', '<'],
    'e': ['3'],
    'g': ['6', '9'],
    'i': ['1', '!', '|'],
    'l': ['1', '|', '7'],
    'o': ['0'],
    's': ['$', '5'],
    't': ['+', '7'],
    'x': ['%'],
    'z': ['2'],
}

REGEXEN = {
    'recent_year': '/19\d\d|200\d|201\d/g'
}

DATE_MAX_YEAR = 2050
DATE_MIN_YEAR = 1000
DATE_SPLITS = {
    4: [  # for length-4 strings, eg 1191 or 9111, two ways to split:
        [1, 2],  # 1 1 91 (2nd split starts at index 1, 3rd at index 2)
        [2, 3],  # 91 1 1
    ],
    5: [
        [1, 3],  # 1 11 91
        [2, 3],  # 11 1 91
    ],
    6: [
        [1, 2],  # 1 1 1991
        [2, 4],  # 11 11 91
        [4, 5],  # 1991 1 1
    ],
    7: [
        [1, 3],  # 1 11 1991
        [2, 3],  # 11 1 1991
        [4, 5],  # 1991 1 11
        [4, 6],  # 1991 11 1
    ],
    8: [
        [2, 4],  # 11 11 1991
        [4, 6],  # 1991 11 11
    ],
}


def omnimatch(password):
    matches = (dictionary_match, reverse_dictionary_match,)  # TODO


def dictionary_match(password, ranked_dictionaries=RANKED_DICTIONARIES):
    pass  # TODO


def reverse_dictionary_match(password, ranked_dictionaries=RANKED_DICTIONARIES):
    pass  # TODO


def set_user_input_dictionary(ordered_list):
    RANKED_DICTIONARIES['user_inputs'] = build_ranked_dict(ordered_list)


def relevant_l33t_subtable(password, table):
    password_chars = {}
    for chr in password.split():
        password_chars[chr] = True

    subtable = {}
    for letter, subs in table:
        relevant_subs = [sub for sub in subs if sub in password_chars]
        if len(relevant_subs) > 0:
            subtable[letter] = relevant_subs

    return subtable


def enumerate_l33t_subs(table):
    