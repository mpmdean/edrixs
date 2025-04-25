import edrixs


def test_fast_fock():
    """Confirm that fast version of the function behaves
    the same as the more easily interpretable slow version."""
    N = 5
    r = 3
    assert (edrixs.get_fock_full_N_fast(N, r)
            == edrixs.get_fock_full_N(N, r))
