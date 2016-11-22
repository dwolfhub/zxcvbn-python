from unittest import TestCase

import pytest

from zxcvbn.matching import repeat_match


@pytest.mark.skip(reason="not ready to be tested")
def test_returns_match():
    assert repeat_match('repeatrepeat')
    assert repeat_match('yesyes123')
