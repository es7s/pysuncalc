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

ts2dt = datetime.utcfromtimestamp


class Test:
    @pytest.mark.parametrize(
        "date, lat, long, expected",
        [
            (ts2dt(1694198261), 55.7558, 37.6172, (1.66327, 0.05909)),
            (ts2dt(1694198261), 0.0, 0.0, (1.69393, 0.60976)),
            (ts2dt(1694198261), 0.0, -90.0, (-1.74485, 0.95027)),
            (ts2dt(1694198261), 0.0, 90.0, (1.74485, -0.95027)),
            (ts2dt(1694198261), 90.0, 0.0, (0.95745, 0.10086)),
            (ts2dt(1694198261), -90.0, 0.0, (2.18413, -0.100866)),
            (ts2dt(1000000000), 55.7558, 37.6172, (-3.05007, -0.50109)),
            (ts2dt(1000000000), 0.0, 0.0, (1.74311, -0.98802)),
            (ts2dt(1000000000), 0.0, -90.0, (1.68334, 0.57304)),
            (ts2dt(1000000000), 0.0, 90.0, (-1.68334, -0.57304)),
            (ts2dt(1000000000), 90.0, 0.0, (2.56565, 0.09451)),
            (ts2dt(1000000000), -90.0, 0.0, (0.57594, -0.09451)),
        ],
    )
    def test_get_position(
        self, date: datetime, lat: float, long: float, expected: tuple[float, float]
    ):
        assert_close(expected, get_position(date, lat, long))

    @pytest.mark.parametrize(
        "date, lat, long, expected",
        [
            (ts2dt(1694202441), 55.7558, 37.6172, {SUNRISE: ts2dt(1694130486)}),
            (ts2dt(1694202441), 55.7558, 37.6172, {SUNSET: ts2dt(1694178584)}),
            (ts2dt(1554757485), 56.07, 47.14, {ZENITH: ts2dt(1554789255)}),
            (ts2dt(1672520400), -90.0, 0.0, {ZENITH: ts2dt(1672477442)}),
            (ts2dt(1672520400), 90.0, 0.0, {NADIR: ts2dt(1672434242)}),
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
