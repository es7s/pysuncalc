# ==============================================================================
#  es7s/pysuncalc [Library for sun timings calculations]
#  (c) 2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under MIT License
# ==============================================================================
from collections.abc import Iterable
from datetime import datetime, timezone, timedelta
from functools import partial

import pytest

from pysuncalc import get_times, get_position, SUNRISE, SUNSET, ZENITH, NADIR, _SUN_TIMES
from . import assert_close

ts2dtu = lambda *args: datetime(*args, tzinfo=timezone(timedelta(hours=0)))
str2dt = lambda dstr: datetime.strptime(dstr, "%d-%b-%y %H:%M:%ST%z")


class Test:
    @pytest.mark.parametrize(
        "dt, lat, long, expected",
        [
            (str2dt("10-Sep-23 18:27:32T+03:00"), 55.7558, 37.6172, (1.62185, 0.07142)),
            # (ts2dtl(2023, 9, 10, 18, 24, 11), 55.7558, 37.6172, (2.34878, -0.33646)),
            # (ts2dtl(1694198261), 0.0, 0.0, (1.67233, -0.17137)),
            # (ts2dtl(1694198261), 0.0, -90.0, (2.10061, 1.37185)),
            # (ts2dtl(1694198261), 0.0, 90.0, (-2.10061, -1.37185)),
            # (ts2dtl(1694198261), 90.0, 0.0, (1.74304, 0.10004)),
            # (ts2dtl(1694198261), -90.0, 0.0, (1.39854, -0.10004)),
            # (ts2dtl(1000000000), 55.7558, 37.6172, (-1.99389, -0.16365)),
            # (ts2dtl(1000000000), 0.0, 0.0, (-1.77419, -1.09080)),
            # (ts2dtl(1000000000), 0.0, -90.0, (1.67556, -0.46928)),
            # (ts2dtl(1000000000), 0.0, 90.0, (-1.67556, 0.46928)),
            # (ts2dtl(1000000000), 90.0, 0.0, (-2.67008, 0.09341)),
            # (ts2dtl(1000000000), -90.0, 0.0, (-0.47150, -0.09341)),
        ],
    )
    def test_get_position(
        self, dt: datetime, lat: float, long: float, expected: tuple[float, float]
    ):
        assert_close(expected, get_position(dt, lat, long))

    @pytest.mark.parametrize(
        "dt, lat, long, expected, extra_names",
        [
            # (ts2dtl(1694202441), 55.7558, 37.6172, {SUNRISE: ts2dtu(1694141286)}, []),
            # (ts2dtl(1694202441), 55.7558, 37.6172, {SUNSET: ts2dtu(1694189383)}, []),
            # (ts2dtl(1554757485), 56.07, 47.14, {ZENITH: ts2dtu(1554800055)}, []),
            # (ts2dtl(1672520400), -90.0, 0.0, {}, [NADIR]),
            # (ts2dtl(1672520400), 90.0, 0.0, {}, [ZENITH]),
        ],
    )
    def test_get_times(
        self,
        dt: datetime,
        lat: float,
        long: float,
        expected: dict[str, datetime],
        extra_names: list[str],
    ):
        assert_close(expected, get_times(dt, lat, long, [*expected.keys()] + (extra_names or [])))

    def test_get_times_keys(self):
        def _expected() -> Iterable[str]:
            for st in _SUN_TIMES:
                yield from (st.set_name, st.rise_name)
                yield NADIR
                yield ZENITH

        assert {*_expected()} == {*get_times(ts2dtl(1694202441), 55.7558, 37.6172).keys()}
