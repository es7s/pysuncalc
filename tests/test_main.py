# ==============================================================================
#  es7s/pysuncalc [Library for sun timings calculations]
#  (c) 2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under MIT License
# ==============================================================================
from collections.abc import Iterable
from datetime import datetime

import pytest

from pysuncalc import get_times, get_position, SUNRISE, SUNSET, ZENITH, NADIR, _SUN_TIMES
from . import assert_close

ts2dt = datetime.fromtimestamp


class Test:
    @pytest.mark.parametrize(
        "date, lat, long, expected",
        [
            (ts2dt(1694198261), 55.7558, 37.6172, (2.34878, -0.33646)),
            (ts2dt(1694198261), 0.0, 0.0, (1.67233, -0.17137)),
            (ts2dt(1694198261), 0.0, -90.0, (2.10061, 1.37185)),
            (ts2dt(1694198261), 0.0, 90.0, (-2.10061, -1.37185)),
            (ts2dt(1694198261), 90.0, 0.0, (1.74304, 0.10004)),
            (ts2dt(1694198261), -90.0, 0.0, (1.39854, -0.10004)),
            (ts2dt(1000000000), 55.7558, 37.6172, (-1.99389, -0.16365)),
            (ts2dt(1000000000), 0.0, 0.0, (-1.77419, -1.09080)),
            (ts2dt(1000000000), 0.0, -90.0, (1.67556, -0.46928)),
            (ts2dt(1000000000), 0.0, 90.0, (-1.67556, 0.46928)),
            (ts2dt(1000000000), 90.0, 0.0, (-2.67008, 0.09341)),
            (ts2dt(1000000000), -90.0, 0.0, (-0.47150, -0.09341)),
        ],
    )
    def test_get_position(
        self, date: datetime, lat: float, long: float, expected: tuple[float, float]
    ):
        assert_close(expected, get_position(date, lat, long))

    @pytest.mark.parametrize(
        "date, lat, long, expected",
        [
            (ts2dt(1694202441), 55.7558, 37.6172, {SUNRISE: ts2dt(1694141286)}),
            (ts2dt(1694202441), 55.7558, 37.6172, {SUNSET: ts2dt(1694189383)}),
            (ts2dt(1554757485), 56.07, 47.14, {ZENITH: ts2dt(1554800055)}),
            (ts2dt(1672520400), -90.0, 0.0, {ZENITH: ts2dt(1672488242)}),
            (ts2dt(1672520400), 90.0, 0.0, {NADIR: ts2dt(1672445042)}),
        ],
    )
    def test_get_times(
        self,
        date: datetime,
        lat: float,
        long: float,
        expected: dict[str, datetime],
    ):
        assert_close(expected, get_times(date, lat, long, expected.keys()))

    def test_get_times_keys(self):
        def _expected() -> Iterable[str]:
            for st in _SUN_TIMES:
                yield from (st.set_name, st.rise_name)
                yield NADIR
                yield ZENITH

        assert {*_expected()} == {*get_times(ts2dt(1694202441), 55.7558, 37.6172).keys()}
