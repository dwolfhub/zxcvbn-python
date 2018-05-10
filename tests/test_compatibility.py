import json
from zxcvbn import zxcvbn
import sys, getopt
from decimal import Decimal

MAX_NUMBER_FOR_ACCURACY = 1000000000000
MIN_NUMBER_FOR_ACCURACY = 1

def update_console_status(total):
    """ iterate from 0 to total and show progress in console """
    total = int(total)
    try:
        range_total = xrange(total)
        range_100_min_total = xrange(100-total)
    except NameError:
        range_total = range(total)
        range_100_min_total = range(100-total)

    str_progress = "%d%% ["%total + "".join(['#' for s in range_total]) + "".join([' ' for s in range_100_min_total]) + "] \r"
    sys.stdout.write(str_progress)
    sys.stdout.flush()

def main(argv):

    verbose = False
    tests_file = ""

    try:
        tests_file = argv[0]
        opts, args = getopt.getopt(argv[1:],"v")
    except getopt.GetoptError:
        print (""""test_compatibility <path/to/tests.json> [options]
            options:
            -v: verbose""")
    for opt, arg in opts:
        if opt == '-v':
            verbose = True

    with open(tests_file) as json_data:
        d = json.load(json_data)

    number_of_passwords = len(d)
    scores_collision = 0
    guesses_collision = 0
    refresh_rate = number_of_passwords/100

    i = 0
    for js_zxcvbn_score in d:
        if i%refresh_rate== 0:
            update_console_status(i*100/number_of_passwords)
        i += 1

        py_zxcvbn_scroe = dict()
        py_zxcvbn_scroe_full = zxcvbn(js_zxcvbn_score['password'])
        py_zxcvbn_scroe["password"] = py_zxcvbn_scroe_full["password"]
        py_zxcvbn_scroe["guesses"] = py_zxcvbn_scroe_full["guesses"]
        py_zxcvbn_scroe["score"] = py_zxcvbn_scroe_full["score"]

        if (abs(py_zxcvbn_scroe["guesses"] - Decimal(js_zxcvbn_score["guesses"])) > MIN_NUMBER_FOR_ACCURACY and
           py_zxcvbn_scroe["guesses"] < MAX_NUMBER_FOR_ACCURACY):
            guesses_collision += 1
            if verbose:
                print ("""\033[91m==========================================
expected:
%s
results:
%s\033[00m""")%(js_zxcvbn_score, py_zxcvbn_scroe)

        if py_zxcvbn_scroe["score"] != js_zxcvbn_score["score"]:
            scores_collision += 1

    if (guesses_collision or scores_collision):
        print ("""\033[91mFailed!
guesses_collision:%d
guesses_score:%d""")%(guesses_collision, scores_collision)
    else:
        print ("\033[92mPassed!")

if __name__ == "__main__":
    main(sys.argv[1:])
