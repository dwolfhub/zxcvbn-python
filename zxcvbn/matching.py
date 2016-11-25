from . import adjacency_graphs
from zxcvbn.frequency_lists import FREQUENCY_LISTS
import re

from zxcvbn.scoring import most_guessable_match_sequence


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
    'recent_year': re.compile('/19\d\d|200\d|201\d/g')
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

SHIFTED_RX = re.compile('/[~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?]/')


def omnimatch(password):
    matches = []
    matchers = [
        dictionary_match,
        reverse_dictionary_match,
        l33t_match,
        spatial_match,
        repeat_match,
        sequence_match,
        regex_match,
        date_match,
    ]
    for matcher in matchers
        @extend matches, matcher.call(this, password)

    return sorted(matches)


def dictionary_match(password, _ranked_dictionaries=RANKED_DICTIONARIES):
    matches = []
    length = len(password)
    password_lower = password.lower()
    for dictionary_name, ranked_dict in _ranked_dictionaries:
        for i in range(length):
            for j in range(i, length):
                if password_lower[i:j + 1] in ranked_dict:
                    word = password_lower[i:j + 1]
                    rank = ranked_dict[word]
                    matches.append({
                        'pattern': 'dictionary',
                        'i': i,
                        'j': j,
                        'token': password[i:j + 1],
                        'matched_word': word,
                        'rank': rank,
                        'dictionary_name': dictionary_name,
                        'reversed': False,
                        'l33t': False,
                    })

    return reversed(matches)


def reverse_dictionary_match(password,
                             _ranked_dictionaries=RANKED_DICTIONARIES):
    reversed_password = ''.join(reversed(password))
    matches = dictionary_match(reversed_password, _ranked_dictionaries)
    for match in matches:
        match['token'] = ''.join(reversed(match['token']))
        match['reversed'] = True
        match['i'], match['j'] = len(password) - 1 - match['j'], \
                                 len(password) - 1 - match['i']

    return sorted(matches)


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


def enumerate_l33t_subs(table):
    keys = table.keys()
    subs = [[]]

    def dedup(subs):
        deduped = []
        members = {}

        for sub in subs:
            assoc = [(k, v) for k, v in sub]
            assoc.sort()
            label = '-'.join([k + ',' + v for k, v in assoc])
            if label not in members:
                members[label] = True
                deduped.append(sub)

        return deduped

    def helper(table, keys, subs):
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
        subs = dedup(next_subs)
        helper(rest_keys)

    helper(table, keys, subs)

    sub_dicts = []
    for sub in subs:
        sub_dict = {}
        for l33t_chr, chr in sub:
            sub_dict[l33t_chr] = chr
        sub_dicts.append()
    return sub_dicts


def translate(string, chr_map):
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

        subbed_password = translate(password, sub)
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


def spacial_match_helper(password, graph, graph_name):
    matches = []
    i = 0
    password_len = len(password)
    while i < password_len - 1:
        j = i + 1
        last_direction = None
        turns = 0
        if graph_name in ['qwerty', 'dvorak', ] and \
                SHIFTED_RX.match(password[i]):
            shifted_count = 1
        else:
            shifted_count = 0

        while True:
            prev_char = password[j - 1]
            found = False
            found_direction = -1
            cur_direction = -1
            adjacents = graph[prev_char] or []
            if j < password_len:
                cur_char = password[j]
                for adj in adjacents:
                    cur_direction += 1
                    if adj and cur_char in adj:
                        found = True
                        found_direction = cur_direction
                        if adj.index(cur_char) == 1:
                            shifted_count += 1
                        if last_direction != found_direction:
                            turns += 1
                            last_direction = found_direction
                        break
            if found:
                j += 1
            else:
                if j - i > 2:
                    matches.append({
                        'pattern': 'spatial',
                        'i': i,
                        'j': j - 1,
                        'token': password[i:j],
                        'turns': turns,
                        'shifted_count': shifted_count,
                    })
                i = j
                break

    return matches


def repeat_match(password):
    matches = []
    greedy = re.compile(r'(.+)\1+')
    lazy = re.compile(r'(.+?)\1+')
    lazy_anchored = re.compile(r'^(.+?)\1+$')
    last_index = 0
    while last_index < len(password):
        # greedy.last_index = lazy.last_index = last_index
        greedy_match = [
            (match.start(), match.end(), match.group(0), match.group(1))
            for match in greedy.finditer(password)
            ]
        lazy_match = [
            (match.start(), match.end(), match.group(0), match.group(1))
            for match in lazy.finditer(password)
            ]

        if not greedy_match:
            break

        if len(greedy_match[0][2]) > len(lazy_match[0][2]):
            # greedy beats lazy for 'aabaab'
            #   greedy: [aabaab, aab]
            #   lazy:   [aa,     a]
            match = greedy_match
            # greedy's repeated string might itself be repeated, eg.
            # aabaab in aabaabaabaab.
            # run an anchored lazy match on greedy's repeated string
            # to find the shortest repeated string
            base_token = lazy_anchored.finditer(match[0][2])[1]
        else:
            match = lazy_match
            base_token = match[0][3]

        i, j = match[0][0], match[0][1]
        base_analysis = most_guessable_match_sequence(
            base_token,
            omnimatch(base_token)
        )
        last_index = j + 1

    return matches


def spacial_match(password, _graphs=GRAPHS):
    matches = []
    for graph_name, graph in _graphs:
        matches.append(spacial_match_helper(password, graph, graph_name))

    return matches.sort()
