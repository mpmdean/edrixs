"""Charge-transfer wrapper equivalence tests."""

import numpy as np
import pytest
from numpy.testing import assert_allclose

import edrixs


@pytest.fixture
def params():
    info = edrixs.get_atom_data('Ni', '3d', 8, edge='L3')
    f2, f4 = [info['slater_i'][i][1] * .8 for i in (1, 2)]
    f2dp, g1, g3 = [info['slater_n'][i][1] * .8 for i in (4, 5, 6)]
    f0 = 7.3 + edrixs.get_F0('d', f2, f4)
    f0dp = 8.5 + edrixs.get_F0('dp', g1, g3)
    return dict(
        slater=([f0, f2, f4], [f0, f2, f4, f0dp, f2dp, g1, g3]),
        impurity_levels=.56 * np.array([.6, -.4, -.4, .6, -.4]),
        bath_levels=1.44 * np.array([.6, -.4, -.4, .6, -.4]),
        hyb=[2.06, 1.21, 1.21, 2.06, 1.21], Delta=4.7, nd=8,
        v_soc=(info['v_soc_i'][0], info['v_soc_i'][0]),
        c_soc=info['c_soc'], om_shift=857.6,
        ext_B=.162 / (2 * np.sqrt(6)) * np.array([1., 1., 2.]),
    )


def explicit_model(p):
    """Assemble the example directly, with analytic CT reference energies."""
    si, sn = p['slater']
    ui = si[0] - (si[1] + si[2]) * 2 / 63
    un = sn[0] - (sn[1] + sn[2]) * 2 / 63
    udp = sn[3] - sn[5] / 15 - 3 * sn[6] / 70
    n, delta = p['nd'], p['Delta']
    # n*Ed + 10*EL + U*n*(n-1)/2 = 0; Ed-EL+U*n = Delta.
    el = (ui * n * (n + 1) / 2 - n * delta) / (n + 10)
    ed = el + delta - ui * n
    elc = (un * n * (n + 1) / 2 - (n + 6) * delta
           + 6 * udp * (n + 1)) / (n + 16)
    ep = elc + delta - udp * (n + 1)
    edc = elc + delta - un * n - 6 * udp
    t = edrixs.tmat_c2r('d', True)
    soc = p['v_soc']
    return edrixs.model_siam(
        ('d', 'p'), 1, v_noccu=n + 10, slater=p['slater'],
        trans_c2n=t, c_level=-p['om_shift'] - 5 * ep, c_soc=p['c_soc'],
        imp_mat=np.diag(np.repeat(p['impurity_levels'], 2) + ed)
        + edrixs.cb_op(edrixs.atom_hsoc('d', soc[0]), t),
        imp_mat_n=np.diag(np.repeat(p['impurity_levels'], 2) + edc)
        + edrixs.cb_op(edrixs.atom_hsoc('d', soc[1]), t),
        bath_level=np.array([np.repeat(p['bath_levels'], 2) + el]),
        bath_level_n=np.array([np.repeat(p['bath_levels'], 2) + elc]),
        hyb=np.array([np.repeat(p['hyb'], 2)]), ext_B=p['ext_B'],
        loc_axis=p.get('loc_axis'),
    )


@pytest.mark.parametrize('modified', [False, True])
def test_explicit_equivalence(params, modified):
    if modified:
        params['slater'][1][:3] = [8.9, 9.2, 5.8]
        params['v_soc'] = (.05, .09)
        params['impurity_levels'] += .3
        params['bath_levels'] -= .7
        params['hyb'] = np.array(params['hyb']) + .4j
        params['loc_axis'] = np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]])
    actual = edrixs.model_siam_2v1c(**params)
    expected = explicit_model(params)
    for i in (0, 1, 3, 4, 6):
        assert_allclose(actual[i], expected[i], atol=1e-10)
    for i in (2, 5):
        assert actual[i].shapes == expected[i].shapes
    assert actual[2].shapes == ((20, 18),)
    assert actual[5].shapes == ((20, 19), (6, 5))
    for i in (0, 3):
        assert_allclose(actual[i], actual[i].conj().T, atol=1e-12)


def test_sparse_and_shift(params):
    original = edrixs.model_siam_2v1c(**params)
    sparse = edrixs.model_siam_2v1c(**params, sparse_U=True)
    for i in (1, 4):
        dim = original[i].shape[0] ** 2
        assert_allclose(sparse[i].toarray(), original[i].reshape(dim, dim), atol=1e-10)
    shift = 2.5
    params['om_shift'] += shift
    shifted = edrixs.model_siam_2v1c(**params)
    di = shifted[0] - original[0]
    dn = shifted[3] - original[3]
    assert_allclose(di, -6 * shift / 18 * np.eye(20), atol=1e-12)
    expected = np.zeros((26, 26))
    expected[20:, 20:] = -shift * np.eye(6)
    assert_allclose(dn, expected, atol=1e-12)
    # Fixed occupancies turn these into scalar many-body energy shifts.
    assert_allclose(5 * dn[20, 20] - 18 * di[0, 0], shift)


@pytest.mark.parametrize('nd', [0, np.int64(9)])
def test_occupancy_boundaries_and_defaults(params, nd):
    params['nd'] = nd
    params.pop('v_soc')
    result = edrixs.model_siam_2v1c(**params)
    assert result[2].shapes == ((20, nd + 10),)
    assert result[5].shapes == ((20, nd + 11), (6, 5))
