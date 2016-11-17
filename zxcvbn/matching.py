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


def dictionary_match(password, _ranked_dictionaries=RANKED_DICTIONARIES):
    pass  # TODO


def reverse_dictionary_match(password,
                             _ranked_dictionaries=RANKED_DICTIONARIES):
    pass  # TODO


def set_user_input_dictionary(ordered_list):
    RANKED_DICTIONARIES['user_inputs'] = build_ranked_dict(ordered_list)


def relevant_l33t_subtable(password, table):
    password_chars = {}
    for char in password.split():
        password_chars[char] = True

    subtable = {}
    for letter, subs in table:
        relevant_subs = [sub for sub in subs if sub in password_chars]
        if len(relevant_subs) > 0:
            subtable[letter] = relevant_subs

    return subtable


def __dedup(subs):
    # TODO
    return subs


def __helper(table, keys, subs):
    if not len(keys):
        return

    first_key = keys[0]
    rest_keys = keys[1:]
    next_subs = []
    for l33t_chr in table[first_key]:
        for sub in subs:
            dup_l33t_index = -1
            for i in range(len(sub)):
                if sub[i][0] == l33t_chr:
                    dup_l33t_index = i
                    break
            if dup_l33t_index == -1:
                sub_extension = l33t_chr + first_key
                next_subs.append(sub_extension)
            else:
                sub_alternative = sub
                sub_alternative.pop(dup_l33t_index)
                sub_alternative.append([l33t_chr, first_key])
                next_subs.append(sub)
                next_subs.append(sub_alternative)
    subs = __dedup(next_subs)
    __helper(rest_keys)
    # TODO this needs to return something or make sure original var is changeds


def enumerate_l33t_subs(table):
    keys = table.keys()
    subs = [[]]

    __helper(table, keys, subs)

    sub_dicts = []
    for sub in subs:
        sub_dict = {}
        for l33t_chr, chr in sub:
            sub_dict[l33t_chr] = chr
        sub_dicts.append()
    return sub_dicts


def __translate(string, chr_map):
    chars = []
    for char in string.split():
        if chr_map[char]:
            chars.append(chr_map[char])
        else:
            chars.append(char)

    return ''.join(chars)


def l33t_match(password, _ranked_dictionaries=RANKED_DICTIONARIES,
               _l33t_table=L33T_TABLE):
    matches = []

    for sub in enumerate_l33t_subs(
            relevant_l33t_subtable(password, _l33t_table)):
        if not bool(sub):
            break

        subbed_password = __translate(password, sub)
        for match in dictionary_match(subbed_password, _ranked_dictionaries):
            token = password[match['i']:match['j']]
            if token.lower() == match['matched_word']:
                # only return the matches that contain an actual substitution
                continue

            # subset of mappings in sub that are in use for this match
            match_sub = {}
            for subbed_chr, chr in sub:
                if token in subbed_chr:
                    match_sub[subbed_chr] = chr
            match['l33t'] = True
            match['token'] = token
            match['sub'] = match_sub
            match['sub_display'] = ', '.join(
                ["%s -> %s" % (k, v) for k, v in match_sub]
            )
            matches.append(match)

    matches = [match for match in matches if len(match['token']) > 1]

    return matches.sort()
