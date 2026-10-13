import pytest

from algorithms import array_sum, array_max, count_equal_pairs, binpow


@pytest.mark.parametrize("arr", [[], [42], [1, 1, 1], [3, 1, 4, 1, 5, 9, 2, 6]])
def test_sum_matches_builtin(arr):
    assert array_sum(arr) == sum(arr)


@pytest.mark.parametrize("arr", [[42], [1, 1, 1], [3, 1, 4, 1, 5, 9, 2, 6]])
def test_max_matches_builtin(arr):
    assert array_max(arr) == max(arr)


def test_max_empty_raises():
    with pytest.raises(ValueError):
        array_max([])


@pytest.mark.parametrize("arr", [[], [42], [1, 1, 1], [1, 2, 1, 2, 1]])
def test_count_equal_pairs_bruteforce(arr):
    expected = sum(
        1 for i in range(len(arr)) for j in range(i + 1, len(arr))
        if arr[i] == arr[j]
    )
    assert count_equal_pairs(arr) == expected


@pytest.mark.parametrize("a,b", [(2, 0), (2, 10), (3, 100), (123, 456)])
def test_binpow_no_mod(a, b):
    assert binpow(a, b) == pow(a, b)


@pytest.mark.parametrize("a,b,mod", [(2, 10**6, 10**9 + 7),
                                     (123456, 987654321, 10**9 + 7)])
def test_binpow_mod(a, b, mod):
    assert binpow(a, b, mod) == pow(a, b, mod)


def test_binpow_negative_raises():
    with pytest.raises(ValueError):
        binpow(2, -1)