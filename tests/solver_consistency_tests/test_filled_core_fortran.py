"""Modern and legacy native workflows with active initial core interactions."""

import importlib.util
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose

import edrixs

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(importlib.util.find_spec('edrixs.fedrixs') is None,
                       reason='requires compiled Fortran solvers'),
    pytest.mark.filterwarnings('ignore:.*is deprecated.*:DeprecationWarning'),
]


def _case(kind):
    # Break spin degeneracy so one-state spectra do not depend on eigenvectors
    # chosen inside a degenerate ground-state subspace.
    common = dict(slater=([0.4] * 30, [0.5] * 30), c_soc=0.11)
    if kind == '1v1c':
        return dict(shell_name=('s', 'p'), v_noccu=1, shell_level=(0.2, -3),
                    v_othermat=np.array([[-0.2, 0.03j], [-0.03j, 0.2]]), **common)
    if kind == '2v1c':
        return dict(shell_name=('s', 's', 'p'), v_tot_noccu=1,
                    shell_level=(0.2, 0.7, -3),
                    v1_othermat=np.diag([-0.2, 0.2]),
                    hopping_v1v2=np.array([[0.1, 0.03j], [0.02j, 0.08]]), **common)
    return dict(shell_name=('s', 'p'), nbath=1, v_noccu=1, c_level=-3,
                imp_mat=np.diag([-0.2, 0.2]), bath_level=np.array([[0.6, 0.8]]),
                hyb=np.array([[0.1+0.02j, 0.08-0.03j]]), **common)


@pytest.mark.parametrize('kind', ['1v1c', '2v1c', 'siam'])
def test_modern_legacy_and_dense_ed_xas_rixs(kind, tmp_path, monkeypatch):
    from mpi4py import MPI
    monkeypatch.chdir(tmp_path)
    kwargs = _case(kind)
    problem = getattr(edrixs, 'model_' + kind)(**kwargs)
    dense_i, dense_n, dense_t = edrixs.get_ops(*problem, backend='dense')
    exact_e, exact_v = np.linalg.eigh(dense_i)
    center = np.median(np.linalg.eigvalsh(dense_n)) - exact_e[0]
    ominc = np.array([center - 0.15, center + 0.2])
    loss = np.linspace(-0.1, 1.0, 5)
    xargs = dict(gamma_c=0.25, thin=0.7, phi=0.2, pol_type=[('isotropic', 0)])
    rargs = dict(gamma_c=0.25, gamma_f=0.1, thin=0.7, thout=1.1, phi=0.2,
                 pol_type=[('linear', 0.1, 'linear', -0.2)])
    exact_x = edrixs.xas(exact_e[:1], exact_v[:, :1], dense_n, dense_t, ominc,
                         backend='dense', **xargs)
    exact_r = edrixs.rixs(exact_e[:1], exact_v[:, :1], dense_i, dense_n, dense_t,
                         ominc, loss, backend='dense', **rargs)
    hi, hn, trans = edrixs.get_ops(*problem, backend='fortran')
    modern_e, vectors = edrixs.ed(hi, num_evals=1,
                                 backend_kws={'ed_solver': 0, 'nvector': 1})
    modern_x = edrixs.xas(modern_e, vectors, hn, trans, ominc,
                          backend_kws={'nkryl': len(dense_n)}, **xargs)
    modern_r = edrixs.rixs(modern_e, vectors, hi, hn, trans, ominc, loss,
                           backend_kws={'nkryl': len(dense_n), 'linsys_tol': 1e-12},
                           **rargs)
    staged = {name: Path(name).read_bytes() for name in (
        'hopping_i.in', 'hopping_n.in', 'coulomb_i.in', 'coulomb_n.in',
        'fock_i.in', 'fock_n.in', 'fock_f.in')}
    legacy_ed = getattr(edrixs, 'ed_' + kind + '_fort')
    # File-only mode must stage the same reduced problem as modern get_ops.
    result = legacy_ed(MPI.COMM_WORLD, **kwargs, do_ed=2 if kind == 'siam' else False)
    assert all(item is None for item in result)
    for name in ('hopping_i.in', 'hopping_n.in', 'coulomb_i.in', 'coulomb_n.in', 'fock_i.in'):
        assert Path(name).read_bytes() == staged[name]
    legacy = legacy_ed(MPI.COMM_WORLD, **kwargs, ed_solver=0, neval=1,
                       nvector=1, idump=True, do_ed=1)
    legacy_e, denmat = legacy[:2]
    nv = problem[2].shapes[0][0]
    assert denmat.shape == (1, nv, nv)
    assert_allclose(np.trace(denmat[0]), 1, atol=1e-12)
    spectrum_args = dict(shell_name=kwargs['shell_name'])
    if kind == 'siam':
        spectrum_args['nbath'] = 1
    legacy_x, _ = getattr(edrixs, 'xas_' + kind + '_fort')(
        MPI.COMM_WORLD, ominc=ominc, nkryl=len(dense_n), **spectrum_args, **xargs)
    legacy_r, _ = getattr(edrixs, 'rixs_' + kind + '_fort')(
        MPI.COMM_WORLD, ominc=ominc, eloss=loss, nkryl=len(dense_n),
        linsys_tol=1e-12, **spectrum_args, **rargs)
    for name in ('fock_i.in', 'fock_n.in', 'fock_f.in'):
        assert Path(name).read_bytes() == staged[name]
    for energies in (modern_e, legacy_e):
        assert_allclose(energies, exact_e[:1], atol=2e-9)
    for spectrum in (modern_x, legacy_x):
        assert_allclose(spectrum, exact_x, rtol=2e-7, atol=2e-9)
    for spectrum in (modern_r, legacy_r):
        assert_allclose(spectrum, exact_r, rtol=2e-6, atol=2e-8)


def test_siam_occupancy_search_contracts_potential_and_restores_constant(tmp_path, monkeypatch):
    from mpi4py import MPI
    monkeypatch.chdir(tmp_path)
    # Filled-core repulsion raises the impurity above the bath. Omitting the
    # contraction incorrectly fills the impurity as well (N=4 instead of N=2).
    kwargs = dict(shell_name=('s', 's'), nbath=1, c_level=-3,
                  imp_mat=np.diag([-0.8, -0.7]), bath_level=np.array([[-0.5, -0.4]]),
                  slater=([0, 0.8, 0, 0.6], [0, 0.8, 0, 0.6]))
    exact = {}
    for nocc in range(5):
        problem = edrixs.model_siam(**kwargs, v_noccu=nocc)
        hi = edrixs.build_op(*problem[:3], backend='dense')
        exact[nocc] = np.linalg.eigvalsh(hi)[0]
    assert min(exact, key=exact.get) == 2
    energies, density, nocc = edrixs.ed_siam_fort(
        MPI.COMM_WORLD, **kwargs, do_ed=0, ed_solver=0, neval=1, nvector=1)
    assert nocc == 2
    assert_allclose(energies, [exact[nocc]], atol=2e-9)
    assert_allclose(np.trace(density[0]), nocc, atol=1e-12)
    for filename in ('search_gs.log', 'search_result.dat'):
        for sector, energy, _ in np.loadtxt(filename, ndmin=2):
            assert_allclose(energy, exact[int(sector)], atol=2e-9)
    staged = Path('hopping_i.in').read_bytes()
    edrixs.get_ops(*edrixs.model_siam(**kwargs, v_noccu=nocc), backend='fortran')
    assert Path('hopping_i.in').read_bytes() == staged


@pytest.mark.parametrize('kind', ['1v1c', '2v1c', 'siam'])
def test_legacy_file_only_modes_do_not_write_on_nonroot(kind, tmp_path, monkeypatch):
    import edrixs.solvers as solvers
    import edrixs._solvers_helpers as helpers
    from edrixs.fortran_backend import fortran_backend

    class Nonroot:
        def Get_rank(self):
            return 1

        def Get_size(self):
            return 2

        def py2f(self):
            return 0

    def forbidden(*args, **kwargs):
        raise AssertionError('non-root wrote native input files')

    monkeypatch.chdir(tmp_path)
    for module in (solvers, helpers, fortran_backend):
        for name in ('write_emat', 'write_umat', 'write_config'):
            monkeypatch.setattr(module, name, forbidden)
    monkeypatch.setattr(fortran_backend, '_write_fock_basis', forbidden)
    result = getattr(edrixs, 'ed_' + kind + '_fort')(
        Nonroot(), **_case(kind), do_ed=2 if kind == 'siam' else False)
    assert all(item is None for item in result)
    assert not list(tmp_path.iterdir())
