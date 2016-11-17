import datetime
from zxcvbn import matching


def zxcvbn(password, user_inputs=None):
    start = datetime.time()
    sanitized_inputs = [str(arg) for arg in user_inputs]

    matching.set_user_input_dictionary(sanitized_inputs)
    # TODO
