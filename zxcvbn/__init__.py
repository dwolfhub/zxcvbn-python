from datetime import datetime, timezone
import typing

from . import matching, scoring, time_estimates, feedback

def zxcvbn(password: str, user_inputs: typing.List[str] = None) -> typing.Dict[str, typing.Any]:

    start = datetime.now(timezone.utc)

    sanitized_inputs = [s.lower() for s in user_inputs or [] if s]

    ranked_dictionaries = matching.RANKED_DICTIONARIES
    ranked_dictionaries['user_inputs'] = matching.build_ranked_dict(sanitized_inputs)

    matches = matching.omnimatch(password, ranked_dictionaries)
    result = scoring.most_guessable_match_sequence(password, matches)
    result['calc_time'] = datetime.now(timezone.utc) - start

    attack_times = time_estimates.estimate_attack_times(result['guesses'])
    for prop, val in attack_times.items():
        result[prop] = val

    result['feedback'] = feedback.get_feedback(result['score'],
                                               result['sequence'])

    return result
