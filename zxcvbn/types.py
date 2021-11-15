from datetime import timedelta
from decimal import Decimal
from typing import *

AdjacencyGraph = Dict[str, Optional[str]]
RankedDict = Dict[str, int]
SubstitutionTable = Dict[str, Set[str]]


class PasswordMatchBase(TypedDict):
    token: str  # matched token
    pattern: str  # type of match
    guesses: int
    guesses_log10: float
    i: int
    j: int


class PasswordMatch(PasswordMatchBase, total=False):
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
    base_matches: Dict[str, Any] # best we can do without cyclic definition

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


class Result(TypedDict):
    password: str
    score: int
    feedback: Feedback
    sequence: List[PasswordMatch]
    guesses: Decimal
    guesses_log10: float
    calc_time: timedelta
    crack_times_seconds: Dict[str, Decimal]
    crack_times_display: Dict[str, str]
