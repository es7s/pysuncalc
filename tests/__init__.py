# ==============================================================================
#  es7s/pysuncalc [Library for sun timings calculations]
#  (c) 2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under MIT License
# ==============================================================================
import typing
from datetime import datetime
from math import isclose
from typing import TypeVar, Iterable

TT = TypeVar("TT")


def assert_close_sorted(a: Iterable[TT], b: Iterable[TT]):
    assert_close(sorted(a), sorted(b))


def assert_close(a: TT, b: TT):
    def get_base_type(v) -> type:
        if isinstance(v, int):
            return int
        elif isinstance(v, float):
            return float
        elif isinstance(v, tuple):
            return tuple
        return type(v)

    def assert_timestamp(dta, dtb):
        def dt2ts(dt) -> int:
            if isinstance(dt, datetime):
                return int(dt.timestamp())
            return dt
        assert_close(dt2ts(dta), dt2ts(dtb))

    def assert_nested(na, nb, pa, pb, **kwargs):
        try:
            assert_close(na, nb)
        except AssertionError as e:
            raise AssertionError(f'{pa} != {pb} at {kwargs}') from e

    types = {get_base_type(a), get_base_type(b)}
    if types == {int, datetime} or types == {float, datetime}:
        assert_timestamp(a, b)

    elif types == {float} or types == {int, float}:
        assert isclose(float(a), float(b), abs_tol=0.0001), f"{a:.3f} !≈ {b:.3f}"

    elif len(types) == 1:
        t = types.pop()
        del types

        if t == int:
            assert a == b, f"{a} != {b}, 0x{a:06x} != 0x{b:06x}"
        elif t == datetime:
            assert_close(a.timestamp(), b.timestamp())
        elif t == dict:
            ka, kb = {*a.keys()}, {*b.keys()}
            kd = ka.symmetric_difference(kb)
            assert not kd, f"Key asymmetry, unique left: {ka & kd}, unique right: {kb & kd}"
            for k in ka:
                assert_nested(a.get(k), b.get(k), a, b, key=k)
        elif t in (tuple, list):
            assert (la := len(a)) == (lb := len(b)), f"Length mismatch: {la} != {lb}"
            for idx, (va, vb) in enumerate(zip(a, b)):
                assert_nested(va, vb, a, b, idx=idx)
        elif t == str:
            raise NotImplementedError(t)
        elif isinstance(a, typing.Iterable) and isinstance(b, typing.Iterable):
            assert_close([*a], [*b])

    else:
        raise TypeError(f"Cannot compare {a} and {b} ({', '.join(map(str, types))})")
