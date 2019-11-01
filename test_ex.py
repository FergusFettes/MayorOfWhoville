import pytest
import asyncio

from ex import TheLandOfWhos


@pytest.fixture
def init():
    return TheLandOfWhos()

def test_all_towns_are_sampled(init):
    towns = []
    for i in range(10000):
        towns.append(init.choose_unexamined_town())
    assert list(init.TOWNSHIPS)[0] in towns
    assert list(init.TOWNSHIPS)[-1] in towns

def test_other_towns_are_sampled(init):
    towns = []
    for i in range(10000):
        towns.append(init.choose_other_town())
    assert len(set(towns)) == (len(init.TOWNSHIPS) - 1)

def test_set_different_produces_whoville(init):
    init.PLACES_CHECKED = init.TOWNSHIPS.difference(
        set([init.LOCATION_OF_THE_MAYOR_OF_WHOVILLE])
    )
    assert init.choose_unexamined_town() == "Whoville"

def test_escape_works(init):
    initial_location = init.LOCATION_OF_THE_MAYOR_OF_WHOVILLE
    asyncio.get_event_loop().run_until_complete(init.escape_to_some_other_town())
    assert not init.LOCATION_OF_THE_MAYOR_OF_WHOVILLE == initial_location

def test_can_find_mayor(init):
    assert not init.MAYOR_WHEREABOUTS_KNOWN
    init.PLACES_CHECKED = init.TOWNSHIPS.difference(
        set([init.LOCATION_OF_THE_MAYOR_OF_WHOVILLE])
    )
    asyncio.get_event_loop().run_until_complete(init.check_random_town())
    assert init.MAYOR_WHEREABOUTS_KNOWN


