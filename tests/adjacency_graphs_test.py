from zxcvbn.adjacency_graphs import ADJACENCY_GRAPHS


def test_adjacency_graphs_dict():
    assert isinstance(ADJACENCY_GRAPHS, dict)
    assert 'qwerty' in ADJACENCY_GRAPHS
    assert 'dvorak' in ADJACENCY_GRAPHS
    assert 'keypad' in ADJACENCY_GRAPHS
    assert 'mac_keypad' in ADJACENCY_GRAPHS
