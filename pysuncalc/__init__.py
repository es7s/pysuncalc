# ==============================================================================
#  es7s/pysuncalc [Library for sun timings calculations]
#  (c) 2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under MIT License
# ==============================================================================
"""
Library for sun timings calculations.

Python port of JS library SunCalc (partial).
Origin: https://github.com/mourner/suncalc

Based on math from http://aa.quae.nl/en/reken/zonpositie.html
"""
import math
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from ._version import __version__  # noqa

RAD: float = math.pi / 180
DAY_SEC: int = 60 * 60 * 24
DAY_MS: int = 1000 * DAY_SEC
J1970: int = 2440588
J2000: int = 2451545
J0: float = 0.0009

E: float = RAD * 23.4397
""" obliquity of the Earth """


@dataclass(frozen=True)
class SunTime:
    angle: float
    rise_name: str
    set_name: str


SUNRISE = "sunrise"
SUNSET = "sunset"
SUNRISE_END = "sunriseEnd"
SUNSET_START = "sunsetStart"
DAWN = "dawn"
DUSK = "dusk"
NAUTICAL_DAWN = "nauticalDawn"
NAUTICAL_DUSK = "nauticalDusk"
NIGHT_END = "nightEnd"
NIGHT = "night"
GOLDEN_HOUR_END = "goldenHourEnd"
GOLDEN_HOUR = "goldenHour"

ZENITH = "zenith"
NADIR = "nadir"


_SUN_TIMES = [
    SunTime(-0.833, SUNRISE, SUNSET),
    SunTime(-0.3, SUNRISE_END, SUNSET_START),
    SunTime(-6, DAWN, DUSK),
    SunTime(-12, NAUTICAL_DAWN, NAUTICAL_DUSK),
    SunTime(-18, NIGHT_END, NIGHT),
    SunTime(6, GOLDEN_HOUR_END, GOLDEN_HOUR),
]
""" sun times configuration """


def get_position(date: datetime, lat: float, long: float) -> tuple[float, float]:
    """
    calculate sun position at specified datetime and coordinates
    :return: (azimuth, altitude)
    """
    lw: float = RAD * -long
    phi: float = RAD * lat
    d: float = _to_days(date)

    dec, ra = _sun_coords(d)
    H = _sidereal_time(d, lw) - ra
    return _azimuth(H, phi, dec), _altitude(H, phi, dec)


def get_times(
    date: datetime,
    lat: float,
    long: float,
    names: Iterable[str] = None,
) -> dict[str, datetime]:
    """
    calculate sun times at specified datetime and coordinates

    >>> get_times(datetime(2023, 9, 8, 20, 31), 55.755833, 37.617222, [DAWN])
    {'dawn': datetime.datetime(2023, 9, 8, 5, 9, 55, 387933)}

    :return: {<name>: <datetime>, ...}
    """
    lw: float = RAD * -long
    phi: float = RAD * lat

    dh: float = _observer_angle(0)
    d: float = _to_days(date)
    n: int = _julian_cycle(d, lw)
    ds: float = _approx_transit(0, lw, n)

    M: float = _solar_mean_anomaly(ds)
    L: float = _ecliptic_longitude(M)
    dec: float = _declination(L, 0)

    j_noon: float = _solar_transit_j(ds, M, L)

    result: dict[str, datetime] = {
        ZENITH: _from_julian(j_noon),
        NADIR: _from_julian(j_noon - 0.5),
    }
    for time in _SUN_TIMES:
        h0: float = (time.angle + dh) * RAD
        j_set: float | None = _get_set_j(h0, lw, phi, dec, n, M, L)
        if j_set is None:  # acos at hour_angle() can fail
            continue
        j_rise: float = j_noon - (j_set - j_noon)

        result[time.rise_name] = _from_julian(j_rise)
        result[time.set_name] = _from_julian(j_set)

    # not part of the original library:
    if SUNRISE not in result.keys():
        if math.copysign(1, phi) == math.copysign(1, dec):  # polar day
            del result[NADIR]
        else:  # polar night
            del result[ZENITH]

    if names:
        result = {k: v for k, v in result.items() if k in names}
    # ==================================

    return result


def _to_days(date: datetime) -> float:
    return _to_julian(date) - J2000


def _to_julian(date: datetime) -> float:
    return (date.timestamp() / DAY_SEC) - 0.5 + J1970


def _from_julian(j: float) -> datetime:
    return datetime.fromtimestamp((j + 0.5 - J1970) * DAY_SEC)


def _right_ascension(l: float, b: float) -> float:
    return math.atan2(math.sin(l) * math.cos(E) - math.tan(b) * math.sin(E), math.cos(l))


def _declination(l: float, b: float) -> float:
    return math.asin(math.sin(b) * math.cos(E) + math.cos(b) * math.sin(E) * math.sin(l))


def _azimuth(H: float, phi: float, dec: float) -> float:
    return math.atan2(math.sin(H), math.cos(H) * math.sin(phi) - math.tan(dec) * math.cos(phi))


def _altitude(H: float, phi: float, dec: float) -> float:
    return math.asin(math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.cos(H))


def _sidereal_time(d: float, lw: float):
    return RAD * (280.16 + 360.9856235 * d) - lw


def _solar_mean_anomaly(d: float) -> float:
    return RAD * (357.5291 + 0.98560028 * d)


def _ecliptic_longitude(M: float) -> float:
    # equation of center:
    C: float = RAD * (1.9148 * math.sin(M) + 0.02 * math.sin(2 * M) + 0.0003 * math.sin(3 * M))
    # perihelion of the Earth:
    P: float = RAD * 102.9372
    return M + C + P + math.pi


def _sun_coords(d: float) -> tuple[float, float]:
    """
    :return: (declination, right_ascension)
    """
    M: float = _solar_mean_anomaly(d)
    L: float = _ecliptic_longitude(M)
    return _declination(L, 0), _right_ascension(L, 0)


def _julian_cycle(d: float, lw: float) -> int:
    return round(d - J0 - lw / (2 * math.pi))


def _approx_transit(Ht: float, lw: float, n: float) -> float:
    return J0 + (Ht + lw) / (2 * math.pi) + n


def _solar_transit_j(ds: float, M: float, L: float) -> float:
    return J2000 + ds + 0.0053 * math.sin(M) - 0.0069 * math.sin(2 * L)


def _hour_angle(h: float, phi: float, d: float) -> float:
    return math.acos((math.sin(h) - math.sin(phi) * math.sin(d)) / (math.cos(phi) * math.cos(d)))


def _observer_angle(height: float) -> float:
    return -2.076 * math.sqrt(height) / 60


def _get_set_j(
    h: float,
    lw: float,
    phi: float,
    dec: float,
    n: float,
    M: float,
    L: float,
) -> float | None:
    """return set time for the given sun altitude"""
    try:
        w: float = _hour_angle(h, phi, dec)
    except ValueError:  # pragma: no cover
        return None
    a: float = _approx_transit(w, lw, n)
    return _solar_transit_j(a, M, L)
