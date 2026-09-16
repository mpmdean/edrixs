import numpy as np
import pytest

from edrixs import solvers
from edrixs.photon_transition import dipole_polvec_rixs, powder_average


def test_xas_powder_is_incoherent_cartesian_average():
    eval_i = np.array([0.0])
    eval_n = np.array([0.0])
    trans_op = np.array([1.0 + 0.5j, -0.2 + 0.8j, 0.7 - 0.4j])[:, None, None]
    ominc = np.array([-0.3, 0.0, 0.6])
    gamma_c = 0.2

    result = solvers.xas_1v1c_py(
        eval_i,
        eval_n,
        trans_op,
        ominc,
        gamma_c=gamma_c,
        pol_type=[('powder', 0)],
    )
    with pytest.warns(DeprecationWarning, match="'isotropic'.*'powder'"):
        alias_result = solvers.xas_1v1c_py(
            eval_i,
            eval_n,
            trans_op,
            ominc,
            gamma_c=gamma_c,
            pol_type=[('isotropic', 0)],
        )

    transition_strength = np.sum(np.abs(trans_op[:, 0, 0])**2) / 3.0
    expected = transition_strength * gamma_c / np.pi / (ominc**2 + gamma_c**2)
    np.testing.assert_allclose(result[:, 0], expected)
    np.testing.assert_allclose(alias_result, result)


def test_rixs_powder_uses_powder_average(monkeypatch):
    scattering_amplitudes = np.array([
        [[1.0 + 0.2j, -0.2 + 0.4j],
         [0.1 - 0.3j, 0.8 + 0.1j],
         [0.5 + 0.6j, -0.7 + 0.2j]],
        [[-0.3 + 0.9j, 0.4 - 0.5j],
         [0.6 + 0.2j, -0.1 + 0.3j],
         [0.2 - 0.4j, 0.9 + 0.7j]],
        [[0.7 - 0.1j, 0.3 + 0.8j],
         [-0.5 + 0.4j, 0.2 - 0.6j],
         [0.4 + 0.5j, -0.8 + 0.1j]],
    ])[:, :, :, np.newaxis]
    monkeypatch.setattr(
        solvers, "scattering_mat", lambda *args, **kwargs: scattering_amplitudes
    )

    eval_i = np.array([0.0, 1.0])
    eloss = np.array([-0.2, 0.5, 1.2])
    gamma_f = 0.15
    thin, thout = 0.4, 0.7
    alpha, beta = 0.2, 1.1
    result = solvers.rixs_1v1c_py(
        eval_i,
        np.array([0.0]),
        np.zeros((3, 1, 2), dtype=complex),
        np.array([0.0]),
        eloss,
        gamma_f=gamma_f,
        thin=thin,
        thout=thout,
        pol_type=[('powder', alpha, 'powder', beta)],
    )
    with pytest.warns(DeprecationWarning, match="'isotropic'.*'powder'"):
        alias_result = solvers.rixs_1v1c_py(
            eval_i,
            np.array([0.0]),
            np.zeros((3, 1, 2), dtype=complex),
            np.array([0.0]),
            eloss,
            gamma_f=gamma_f,
            thin=thin,
            thout=thout,
            pol_type=[('isotropic', alpha, 'powder', beta)],
        )

    incident_pol, outgoing_pol = dipole_polvec_rixs(
        thin, thout, alpha=alpha, beta=beta, pol_type=('linear', 'linear')
    )
    tensors = np.moveaxis(scattering_amplitudes, (0, 1), (-2, -1))
    strengths = powder_average(tensors, incident_pol, outgoing_pol)[:, 0]
    expected = sum(
        strength * gamma_f / np.pi / ((eloss - energy)**2 + gamma_f**2)
        for strength, energy in zip(strengths, eval_i)
    )

    np.testing.assert_allclose(result[0, :, 0], expected)
    np.testing.assert_allclose(alias_result, result)
