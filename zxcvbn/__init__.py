from datetime import datetime

from . import matching, scoring, time_estimates, feedback


def zxcvbn(password, user_inputs=[]):
    start = datetime.now()

    sanitized_inputs = [str(arg).lower() for arg in user_inputs]
    matching.set_user_input_dictionary(sanitized_inputs)

    matches = matching.omnimatch(password)
    result = scoring.most_guessable_match_sequence(password, matches)
    result['calc_time'] = datetime.now() - start

    attack_times = time_estimates.estimate_attack_times(result['guesses'])
    for prop, val in attack_times.items():
        result[prop] = val

    result['feedback'] = feedback.get_feedback(result['score'],
                                               result['sequence'])

    return result
