from zxcvbn.scoring import START_UPPER, ALL_UPPER
from gettext import gettext as _


def get_feedback(score, sequence):
    if len(sequence) == 0:
        return {
            'warning': '',
            'suggestions': [
                "WORDS",
                "OOPS",
            ]
        }

    if score > 2:
        return {
            'warning': '',
            'suggestions': [],
        }

    longest_match = sequence[0]
    for match in sequence[1:]:
        if len(match['token']) > len(longest_match['token']):
            longest_match = match

    feedback = get_match_feedback(longest_match, len(sequence) == 1)
    extra_feedback = "MORE_WORDS"
    if feedback:
        feedback['suggestions'].insert(0, extra_feedback)
        if not feedback['warning']:
            feedback['warning'] = ''
    else:
        feedback = {
            'warning': '',
            'suggestions': [extra_feedback]
        }

    return feedback


def get_match_feedback(match, is_sole_match):
    if match['pattern'] == 'dictionary':
        return get_dictionary_match_feedback(match, is_sole_match)
    elif match['pattern'] == 'spatial':
        if match['turns'] == 1:
            warning = "ROWS"
        else:
            warning = "SHORT"

        return {
            'warning': warning,
            'suggestions': [
                "LONGER"
            ]
        }
    elif match['pattern'] == 'repeat':
        if len(match['base_token']) == 1:
            warning = "REPEAT_CHAR"
        else:
            warning = "REPEAT_SEQ"
        return {
            'warning': warning,
            'suggestions': [
                "REPEAT_WORD"
            ]
        }
    elif match['pattern'] == 'sequence':
        return {
            'warning': "SEQUENCE1",
            'suggestions': [
                "SEQUENCE2"
            ]
        }
    elif match['pattern'] == 'regex':
        if match['regex_name'] == 'recent_year':
            return {
                'warning': "YEARS2",
                'suggestions': [
                    "YEARS",
                    "YEARS_RELEVANT",
                ]
            }
    elif match['pattern'] == 'date':
        return {
            'warning': "DATE",
            'suggestions': [
                "DATES_RELEVANT",
            ],
        }


def get_dictionary_match_feedback(match, is_sole_match):
    warning = ''
    if match['dictionary_name'] == 'passwords':
        if is_sole_match and not match.get('l33t', False) and not \
                match['reversed']:
            if match['rank'] <= 10:
                warning = "TOP10"
            elif match['rank'] <= 100:
                warning = "TOP100"
            else:
                warning = "COMMON"
        elif match['guesses_log10'] <= 4:
            warning = "COMMON2"
    elif match['dictionary_name'] == 'english':
        if is_sole_match:
            warning = "SINGLE_WORD"
    elif match['dictionary_name'] in ['surnames', 'male_names',
                                      'female_names', ]:
        if is_sole_match:
            warning = "NAME"
        else:
            warning = "COMMON_NAME"
    else:
        warning = ''

    suggestions = []
    word = match['token']
    if START_UPPER.search(word):
        suggestions.append("CAPS")
    elif ALL_UPPER.search(word) and word.lower() != word:
        suggestions.append("ALL_UPPER")

    if match['reversed'] and len(match['token']) >= 4:
        suggestions.append("REVERSE")
    if match.get('l33t', False):
        suggestions.append("SUBS")

    return {
        'warning': warning,
        'suggestions': suggestions,
    }
