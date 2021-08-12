# -*- coding: utf-8 -*-
from zxcvbn import zxcvbn


def test_unicode_user_inputs():
    # test Issue #12 -- don't raise a UnicodeError with unicode user_inputs or
    # passwords.
    input_ = u'Фамилия'
    password = u'pÄssword junkiË'

    zxcvbn(password, user_inputs=[input_])


def test_invalid_user_inputs():
    # don't raise an error with non-string types for user_inputs
    input_ = None
    password = u'pÄssword junkiË'

    zxcvbn(password, user_inputs=[input_])


def test_long_password():
    input_ = None
    password = "weopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioej"

    zxcvbn(password, user_inputs=[input_])


def test_dictionary_password():
    # return the correct error message for a english match
    input_ = None
    password = "musculature"

    result = zxcvbn(password, user_inputs=[input_])

    assert result["feedback"]["warning"] == \
           "A word by itself is easy to guess.", \
           "Gives specific error for single-word passwords"
