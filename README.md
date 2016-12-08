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
    'crack_times_seconds': {
        'online_no_throttling_10_per_second': 1500.0, 
        'online_throttling_100_per_hour': 0.041666666666666664, 
        'offline_fast_hashing_1e10_per_second': 1.5e-06, 
        'offline_slow_hashing_1e4_per_second': 1.5
    }, 
    'guesses': 15000, 
    'feedback': {
        'warning': '', 
        'suggestions': [
            'Add another word or two. Uncommon words are better.', 
            "Capitalization doesn't help very much"
        ]}, 
        'guesses_log10': 9.615805480084347, 
        'sequence': [
            {
                'guesses': 50, 
                'guesses_log10': 3.912023005428146, 
                'l33t_variations': 1, 
                'reversed': False, 
                'rank': 1, 
                'uppercase_variations': 2, 
                'dictionary_name': 'user_inputs', 
                'matched_word': 'john', 
                'base_guesses': 1, 
                'i': 0, 
                'pattern': 'dictionary', 
                'j': 3, 
                'l33t': False, 
                'token': 'John'
            }, {
                'guesses': 50, 
                'guesses_log10': 3.912023005428146, 
                'l33t_variations': 1, 
                'reversed': False, 
                'rank': 2, 
                'uppercase_variations': 2, 
                'dictionary_name': 'user_inputs', 
                'matched_word': 'smith', 
                'base_guesses': 2, 
                'i': 4, 
                'pattern': 'dictionary', 
                'j': 8, 
                'l33t': False, 
                'token': 'Smith'
            }
        ], 
        'crack_times_display': {
            'online_throttling_100_per_hour': 'less than a second', 
            'online_no_throttling_10_per_second': '1500.0 minutes', 
            'offline_fast_hashing_1e10_per_second': 'less than a second', 
            'offline_slow_hashing_1e4_per_second': '1.5 minutes'
        }, 
        'score': 1, 
        'password': 'JohnSmith', 
        'calc_time': datetime.timedelta(0, 0, 4143)
    }
```