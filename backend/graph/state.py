from typing import TypedDict


class StartupState(TypedDict):
    idea:         str
    founder:      dict
    market:       dict
    competitor:   dict
    customer:     dict
    investor:     dict
    failure:      dict
    india_policy: dict
    judge:        dict


def initial_state(idea: str) -> StartupState:
    return StartupState(
        idea=idea,
        founder={}, market={}, competitor={}, customer={},
        investor={}, failure={}, india_policy={}, judge={},
    )
