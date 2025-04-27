import edrixs


def test_get_fock_full_N():
    """Reproduce known behavior of get_fock_full_N"""
    assert edrixs.get_fock_full_N(4, 2) == [3, 5, 6, 9, 10, 12]


def binary_from_full(norb, N):
    """Helper function, which generates binary
    from the fock_bin function."""
    return [int(''.join(str(b) for b in binary), 2)
            for binary in edrixs.fock_bin(norb, N)]


def test_fast_fock_compare():
    """Confirm that fast version of the function behaves
    the same as the more easily interpretable slow version."""
    norb = 5
    for N in [0, 3]:
        assert (sorted(edrixs.get_fock_full_N(norb, N))
                == sorted(binary_from_full(norb, N)))
