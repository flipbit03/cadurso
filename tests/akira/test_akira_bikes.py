from cadurso import Cadurso
from tests.akira.conftest import (
    Bike,
    BikePermission,
    Character,
)


def test_kaneda_can_drive_his_bike(
    akira_authz: Cadurso, kaneda: Character, kaneda_bike: Bike
) -> None:
    """
    Kaneda is inseparable from his trademark ride.
    Let no one question his right to steer it.
    """

    # Using can() and do() methods
    assert akira_authz.can(kaneda).do(BikePermission.DRIVE).on(kaneda_bike)

    # Same thing, using is_allowed() method
    assert akira_authz.is_allowed(kaneda, BikePermission.DRIVE, kaneda_bike)


def test_colonel_can_drive_any_bike(
    akira_authz: Cadurso, colonel: Character, kaneda_bike: Bike, tetsuo_bike: Bike
) -> None:
    """
    The Colonel's iron grip extends even to bikes that
    were never his to begin with.
    """
    assert akira_authz.is_allowed(colonel, BikePermission.DRIVE, kaneda_bike)
    assert akira_authz.is_allowed(colonel, BikePermission.DRIVE, tetsuo_bike)


def test_tetsuo_explode_bike_when_psychic_power_grows(
    akira_authz: Cadurso, tetsuo: Character, kaneda_bike: Bike
) -> None:
    """
    Tetsuo may not start out powerful enough to destroy Kaneda's
    beloved machine, but that can change in a rage-filled instant.
    """
    assert not akira_authz.is_allowed(tetsuo, BikePermission.EXPLODE, kaneda_bike)

    tetsuo.psychic_level = 90
    assert akira_authz.is_allowed(tetsuo, BikePermission.EXPLODE, kaneda_bike)
