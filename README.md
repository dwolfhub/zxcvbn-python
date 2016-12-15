[![Build Status](https://travis-ci.org/dwolfhub/zxcvbn-python.svg?branch=master)](https://travis-ci.org/dwolfhub/zxcvbn-python)

# zxcvbn-python
Python implementation of Dropbox's realistic password strength estimator. The original library, written for JavaScript, can be found [here](https://github.com/dropbox/zxcvbn).

Tested in Python versions 2.6-2.7, 3.3-3.5

## Installation

Install the package using pip: `pip install zxcvbn-python`

## Usage

Pass a password as the first parameter, and a list of user-provided inputs as the `user_inputs` parameter (optional).

```python
from zxcvbn import zxcvbn

results = zxcvbn('JohnSmith123', user_inputs=['John', 'Smith'])

print(results)
```

Output:

```
{
    'password': 'JohnSmith123', 
    'score': 2, 
    'guesses': 2567800, 
    'guesses_log10': 14.75856005913912, 
    'calc_time': datetime.timedelta(0, 0, 3519), 
    'feedback': {
        'suggestions': [
            'Add another word or two. Uncommon words are better.', 
            "Capitalization doesn't help very much"
        ], 
        'warning': ''
    }, 
    'crack_times_display': {
        'offline_fast_hashing_1e10_per_second': 'less than a second',
        'online_no_throttling_10_per_second': '3 days', 
        'online_throttling_100_per_hour': '3 years', 
        'offline_slow_hashing_1e4_per_second': '4 minutes', 
    }, 
    'crack_times_seconds': {
        'offline_fast_hashing_1e10_per_second': 0.00025678, 
        'offline_slow_hashing_1e4_per_second': 256.78, 
        'online_no_throttling_10_per_second': 256780.0, 
        'online_throttling_100_per_hour': 92440800.0
    }, 
    'sequence': [{
        'guesses_log10': 3.912023005428146, 
        'base_guesses': 1, 
        'rank': 1, 
        'guesses': 50, 
        'l33t': False, 
        'uppercase_variations': 2, 
        'matched_word': 'john', 
        'j': 3, 
        'pattern': 'dictionary', 
        'reversed': False, 
        'i': 0, 
        'token': 'John', 
        'l33t_variations': 1, 
        'dictionary_name': 'user_inputs'
    }, {
        'guesses_log10': 10.149487885993265, 
        'base_guesses': 12789, 
        'rank': 12789, 
        'guesses': 25578, 
        'l33t': False, 
        'uppercase_variations': 2, 
        'matched_word': 'smith123', 
        'j': 11, 
        'pattern': 'dictionary', 
        'reversed': False, 
        'i': 4, 
        'token': 'Smith123', 
        'l33t_variations': 1, 
        'dictionary_name': 'passwords'
    }]
}
```