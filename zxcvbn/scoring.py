import operator

from math import log, factorial, inf


def calc_average_degree(graph):
    average = 0
    for key, neighbors in graph.items():
        average += len([n for n in neighbors if n])
    average /= len([k for k, v in graph.items()])

    return average


BRUTEFORCE_CARDINALITY = 10
MIN_GUESSES_BEFORE_GROWING_SEQUENCE = 10000
MIN_SUBMATCH_GUESSES_SINGLE_CHAR = 10
MIN_SUBMATCH_GUESSES_MULTI_CHAR = 50

MIN_YEAR_SPACE = 20
REFERENCE_YEAR = 2016


def nCk(n, k):
    """http://blog.plover.com/math/choose.html"""
    if k > n:
        return 0
    if k == 0:
        return 1

    r = 1
    for d in range(1, k + 1):
        r *= n
        r /= d
        n -= 1

    return r


def most_guessable_match_sequence(password, matches, _exclude_additive=False):
    """ search --- most guessable match sequence
    ----------------------------------------------------------------------------
    takes a sequence of overlapping matches, returns the non-overlapping
    sequence with minimum guesses. the following is a O(l_max * (n + m)) dynamic
    programming algorithm for a length-n password with m candidate matches.
    l_max is the maximum optimal sequence length spanning each prefix of the
    password. In practice it rarely exceeds 5 and the search terminates rapidly.
    the optimal "minimum guesses" sequence is here defined to be the sequence
    that minimizes the following function:
       g = l! * Product(m.guesses for m in sequence) + D^(l - 1)
    where l is the length of the sequence.
    the factorial term is the number of ways to order l patterns.
    the D^(l-1) term is another length penalty, roughly capturing the idea that
    an attacker will try lower-length sequences first before trying length-l
    sequences.
    for example, consider a sequence that is date-repeat-dictionary.
     - an attacker would need to try other date-repeat-dictionary combinations,
       hence the product term.
     - an attacker would need to try repeat-date-dictionary,
       dictionary-repeat-date, ..., hence the factorial term.
     - an attacker would also likely try length-1 (dictionary) and length-2
       (dictionary-date) sequences before length-3. assuming at minimum D
       guesses per pattern type, D^(l-1) approximates Sum(D^i for i in [1..l-1]

    :param password:
    :param matches:
    :param _exclude_additive:
    :return:
    """
    n = len(password)

    # partition matches into sublists according to ending index j
    matches_by_j = [[]] * n
    for m in matches:
        matches_by_j[m['j']].append(m)
    # small detail: for deterministic output, sort each sublist by i.
    for lst in matches_by_j:
        lst.sort(key=operator.attrgetter('i'))

    optimal = {
        'm': [{}] * n,
        'pi': [{}] * n,
        'g': [{}] * n,
    }

    def update(m, l):
        k = m['j']
        pi = estimate_guesses(m, password)
        if l > 1:
            # we're considering a length-l sequence ending with match m:
            # obtain the product term in the minimization function by
            # multiplying m's guesses by the product of the length-(l-1)
            # sequence ending just before m, at m.i - 1.
            pi *= optimal['pie'][m['i'] - 1][l - 1]
        # calculate the minimization func
        g = factorial(l) * pi
        if not _exclude_additive:
            g += pow(MIN_GUESSES_BEFORE_GROWING_SEQUENCE, l - 1)

        # update state if new best.
        # first see if any competing sequences covering this prefix, with l or
        # fewer matches, fare better than this sequence. if so, skip it and
        # return.
        for completing_l, competing_g in enumerate(optimal['g'][k]):
            if completing_l > l:
                continue
            if competing_g <= g:
                return

        optimal['g'][k][l] = g
        optimal['m'][k][l] = m
        optimal['pi'][k][l] = pi

    def bruteforce_update(k):
        m = make_bruteforce_match(0, k)
        update(m, 1)
        for i in range(1, k):
            m = make_bruteforce_match(i, k)
            for l, last_m in optimal['m'][i - 1].items():
                l = int(l)

                if last_m['pattern'] == 'bruteforce':
                    continue

                update(m, l + 1)

    def make_bruteforce_match(i, j):
        return {
            'pattern': 'bruteforce',
            'token': password[i:j],
            'i': i,
            'j': j,
        }

    def unwind(n):
        optimal_match_sequence = []
        k = n - 1
        l = None
        g = inf

        for candidate_l, candidate_g in optimal['g'][k].items():
            if candidate_g < g:
                l = candidate_l
                g = candidate_g
        while k >= 0:
            m = optimal['m'][k][l]
            optimal_match_sequence.insert(0, m)
            k = m['i'] - 1
            l -= 1

        return optimal_match_sequence

    for k in range(n):
        for m in matches_by_j[k]:
            if m['i'] > 0:
                for l in optimal['m'][m['i'] - 1]:
                    l = int(l)
                    update(m, l + 1)
            else:
                update(m, 1)
        bruteforce_update(k)
    optimal_match_sequence = unwind(n)
    optimal_l = len(optimal_match_sequence)

    if len(password) == 0:
        guesses = 1
    else:
        guesses = optimal['g'][n - 1][optimal_l]

    return {
        'password': password,
        'guesses': guesses,
        'guesses_log10': log(guesses),
        'sequence': optimal_match_sequence,
    }


def estimate_guesses(match, password):
    if match.get('guesses', False):
        return match['guesses']

    min_guesses = 1
    if len(match['token']) < len(password):
        if len(match['token']) == 1:
            min_guesses = MIN_SUBMATCH_GUESSES_SINGLE_CHAR
        else:
            min_guesses = MIN_SUBMATCH_GUESSES_MULTI_CHAR

    estimation_functions = {
        'bruteforce': bruteforce_guesses,
        'dictionary': dictionary_guesses,
        'spatial': spatial_guesses,
        'repeat': repeat_guesses,
        'sequence': sequence_guesses,
        'regex': regex_guesses,
        'date': date_guesses,
    }

    guesses = estimation_functions[match['pattern']](match)
    match['guesses'] = max(guesses, min_guesses)
    match['guesses_log10'] = log(match['guesses'])

    return match['guesses']


def bruteforce_guesses(match):
    guesses = pow(BRUTEFORCE_CARDINALITY, len(match['token']))
    # small detail: make bruteforce matches at minimum one guess bigger than
    # smallest allowed submatch guesses, such that non-bruteforce submatches
    # over the same [i..j] take precedence.
    if len(match['token']) == 1:
        min_guesses = MIN_SUBMATCH_GUESSES_SINGLE_CHAR + 1
    else:
        min_guesses = MIN_SUBMATCH_GUESSES_MULTI_CHAR + 1

    return max(guesses, min_guesses)


def dictionary_guesses(match):
    # keep these as properties for display purposes
    match['base_guesses'] = match['rank']
    match['uppercase_variations'] = uppercase_variations(match)
    match['l33t_variations'] = l33t_variations(match)
    reversed_variations = match['reversed'] and 2 or 1

    return match['base_guesses'] * match['uppercase_variations'] * \
           match['l33t_variations'] * reversed_variations


def spatial_guesses(match):
    pass


def repeat_guesses(match):
    pass


def sequence_guesses(match):
    pass


def regex_guesses(match):
    pass


def date_guesses(match):
    your_space = max(abs(match['year'] - REFERENCE_YEAR), MIN_YEAR_SPACE)
    guesses = your_space * 365
    if match.get('separator', False):
        guesses *= 4

    return guesses


def uppercase_variations(match):
    pass


def l33t_variations(match):
    pass
