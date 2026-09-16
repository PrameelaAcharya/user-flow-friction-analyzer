from src.summarizer import select_top_friction


class MockFriction:
    def __init__(self, step_id, score):
        self.step_id = step_id
        self.score = score


def test_empty_points():
    result = select_top_friction([])

    assert result == []


def test_zero_limit():
    points = [
        MockFriction(1, 5),
        MockFriction(2, 4),
        MockFriction(3, 3),
    ]

    result = select_top_friction(points, limit=0)

    assert result == []


def test_fewer_than_three_points():
    points = [
        MockFriction(1, 5),
        MockFriction(2, 3),
    ]

    result = select_top_friction(points)

    assert [p.step_id for p in result] == [1, 2]


def test_exactly_three_points():
    points = [
        MockFriction(1, 5),
        MockFriction(2, 3),
        MockFriction(3, 2),
    ]

    result = select_top_friction(points)

    assert [p.step_id for p in result] == [1, 2, 3]


def test_more_than_three_without_ties():
    points = [
        MockFriction(1, 5),
        MockFriction(2, 4),
        MockFriction(3, 3),
        MockFriction(4, 2),
        MockFriction(5, 1),
    ]

    result = select_top_friction(points)

    assert [p.step_id for p in result] == [1, 2, 3]


def test_tie_at_third_position():
    points = [
        MockFriction(1, 5),
        MockFriction(2, 4),
        MockFriction(3, 3),
        MockFriction(4, 3),
        MockFriction(5, 2),
    ]

    result = select_top_friction(points)

    assert [p.step_id for p in result] == [1, 2, 3, 4]


def test_multiple_ties_at_third_position():
    points = [
        MockFriction(1, 5),
        MockFriction(2, 4),
        MockFriction(3, 3),
        MockFriction(4, 3),
        MockFriction(5, 3),
        MockFriction(6, 3),
        MockFriction(7, 2),
    ]

    result = select_top_friction(points)

    assert [p.step_id for p in result] == [1, 2, 3, 4, 5, 6]


def test_unsorted_input():
    points = [
        MockFriction(5, 1),
        MockFriction(2, 4),
        MockFriction(4, 2),
        MockFriction(1, 5),
        MockFriction(3, 3),
    ]

    result = select_top_friction(points)

    assert [p.step_id for p in result] == [1, 2, 3]