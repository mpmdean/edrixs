import numpy as np

from edrixs.photon_transition import powder_average


def _rotation_z(angle):
    cosine = np.cos(angle)
    sine = np.sin(angle)
    return np.array([[cosine, -sine, 0.0],
                     [sine, cosine, 0.0],
                     [0.0, 0.0, 1.0]])


def _rotation_y(angle):
    cosine = np.cos(angle)
    sine = np.sin(angle)
    return np.array([[cosine, 0.0, sine],
                     [0.0, 1.0, 0.0],
                     [-sine, 0.0, cosine]])


def _orientation_average(scattering_tensor, incident_pol, outgoing_pol):
    """Integrate a rank-four intensity exactly enough over SO(3)."""
    angles = 2 * np.pi * np.arange(8) / 8
    cos_beta, beta_weights = np.polynomial.legendre.leggauss(5)
    result = 0.0
    for alpha in angles:
        for gamma in angles:
            for value, weight in zip(cos_beta, beta_weights):
                rotation = (
                    _rotation_z(alpha)
                    @ _rotation_y(np.arccos(value))
                    @ _rotation_z(gamma)
                )
                rotated = rotation @ scattering_tensor @ rotation.T
                amplitude = outgoing_pol.conj() @ rotated @ incident_pol
                result += weight * np.abs(amplitude)**2
    return result / (2 * len(angles)**2)


def test_powder_average_matches_so3_integration():
    scattering_tensor = np.array([
        [1.2 + 0.3j, -0.4 + 0.7j, 0.2 - 0.1j],
        [0.8 - 0.2j, -0.6 + 0.4j, 0.5 + 0.9j],
        [-0.3 + 0.6j, 0.1 - 0.8j, 0.7 + 0.2j],
    ])
    incident_pol = np.array([1.0, 1.0j, 0.0]) / np.sqrt(2)
    outgoing_pol = np.array([0.3, 0.4j, np.sqrt(0.75)])

    expected = _orientation_average(scattering_tensor, incident_pol, outgoing_pol)
    result = powder_average(scattering_tensor, incident_pol, outgoing_pol)

    np.testing.assert_allclose(result, expected, rtol=1e-13, atol=1e-13)
