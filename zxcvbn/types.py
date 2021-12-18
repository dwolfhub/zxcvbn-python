from datetime import timedelta
from decimal import Decimal
from typing import Any, Dict, List, Match, Optional, Set, Tuple, TypedDict

AdjacencyGraph = Dict[str, List[Optional[str]]]
RankedDict = Dict[str, int]
SubstitutionTable = Dict[str, Set[str]]
SubstitutionDict = Dict[str, str]


class PasswordMatchBase(TypedDict):
    token: str  # matched token
    pattern: str  # type of match
    i: int
    j: int


class PasswordMatch(PasswordMatchBase, total=False):
    guesses: int
    guesses_log10: float

    base_guesses: int
    dictionary_name: str
    matched_word: str
    rank: int
    reversed: bool
    uppercase_variations: int

    regex_match: Match
    regex_name: str

    l33t: bool
    l33t_variations: int
    sub: Dict[str, str]
    sub_display: str

    repeat_count: int
    base_token: str
    base_matches: List[Any]  # List[PasswordMatch] but mypy doesn't support cyclic definition

    ascending: bool
    sequence_name: str
    sequence_space: int

    year: int
    month: int
    day: int
    separator: str

    graph: str
    shifted_count: int
    turns: int


class Feedback(TypedDict):
    suggestions: List[str]
    warning: str


class ResultBase(TypedDict):
    password: str
    sequence: List[PasswordMatch]
    guesses: int
    guesses_log10: float

class Result(ResultBase):
    score: int
    feedback: Feedback
    calc_time: timedelta
    crack_times_seconds: Dict[str, Decimal]
    crack_times_display: Dict[str, str]
