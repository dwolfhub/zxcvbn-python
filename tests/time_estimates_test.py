from zxcvbn.time_estimates import estimate_attack_times
import sys

def test_long_ints_dont_overflow():
    try:
        long_guesses = sys.maxsize + 1
    except expression as identifier:
        long_guesses = sys.maxint + 1

    attack_times = estimate_attack_times(long_guesses)
    assert 'crack_times_seconds' in attack_times
    assert 'crack_times_display' in attack_times
    assert 'score' in attack_times