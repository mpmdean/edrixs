.. _introduction:

**********************
Introduction to edrixs
**********************

edrixs computes X-ray absorption (XAS) and resonant inelastic X-ray scattering
(RIXS) spectra by exact diagonalization (ED) of model Hamiltonians for
correlated electrons.

Every calculation follows the same path (shown below): a physical model
produces single-particle matrices and a Fock-basis specification; these are
combined into many-body operators; the Hamiltonian is diagonalized for its
low-energy eigenstates; and a spectrum is built from transition operators
acting on them.  Each stage is a thin layer of functions, and the numerical
linear algebra is handed to an interchangeable backend.

.. figure:: /_static/calculation_structure.svg
   :width: 85%
   :align: center
   :alt: Flow chart of the stages of an edrixs calculation.

   The stages of an edrixs calculation.  The quantities passed from one stage
   to the next are shown on the right; ``_i`` labels the initial/final state
   with no core hole and ``_n`` the intermediate state with one core hole.

The sections below follow the figure box by box: :ref:`the physical model
<physical-model>`, the :ref:`many-body operators <many-body-operators>` built
from it, their :ref:`exact diagonalization <exact-diagonalization>`, and the
:ref:`XAS <xas>` and :ref:`RIXS <rixs>` spectra computed from the eigenstates.
A closing section covers the :ref:`backend <backend>` that carries out the
linear algebra for the last three.  The orbital orderings, single-particle
bases and spectral conventions are collected separately on the
:ref:`conventions` page, and the :ref:`pedagogical examples <examples>` work
through the same material in more physical detail.

.. _physical-model:

The physical model
==================

The first stage sets up the physics and nothing else.  The ``edrixs.models``
constructors -- ``model_1v1c``, ``model_2v1c`` and ``model_siam`` for one
valence shell and one core shell, two valence shells and one core shell, or an
Anderson impurity model -- return a *backend-independent* description of the
problem and build no operators:

* the one-body matrices ``emat_i`` / ``emat_n``,
* the Coulomb tensors ``umat_i`` / ``umat_n``,
* compact Fock-basis specifications ``basis_i`` / ``basis_n``, and
* the Cartesian photon transition matrices ``trans_mat``.

Throughout edrixs, ``_i`` labels the initial and final states, which have no
core hole, and ``_n`` the intermediate state, which has one.

``emat`` and ``umat`` are the coefficients of a second-quantized Hamiltonian

.. math::

   \hat{H} = \sum_{ij} t_{ij}\, \hat{f}_i^{\dagger} \hat{f}_j
           + \sum_{ijlk} U_{ijlk}\, \hat{f}_i^{\dagger} \hat{f}_j^{\dagger}
             \hat{f}_k \hat{f}_l ,

with the one-body coefficients :math:`t_{ij}` passed as ``emat`` and the
two-body coefficients :math:`U_{ijkl}` as ``umat``.  Their single-particle
index runs over spin-orbitals in the default basis and orbital order set out in
:ref:`conventions`.

Parameters entering these matrices:

* All energies are in **eV**.
* The absolute energy of a core level is not known to the calculation.  Set the
  resonance position by hand through ``shell_level`` (or ``c_level``) and an
  offset chosen to match experiment.
* Coulomb interactions are parameterized by Slater integrals :math:`F^k`
  (and :math:`G^k` for core-valence terms).  edrixs ships Hartree-Fock values
  in ``edrixs.get_atom_data`` and provides some conversions between different
  notations for the electron correlations.
* Atomic Slater and SOC values are usually **scaled down** (often 70-90%) to
  approximate screening in the solid.

A single-shell problem needs no model constructor: build the matrices directly
with helpers such as ``get_umat_slater`` and ``atom_hsoc``.

.. code-block:: python

    import edrixs

    Ud = 4
    JH = 1
    F0, F2, F4 = edrixs.UdJH_to_F0F2F4(Ud, JH)

    umat = edrixs.get_umat_slater('t2g', F0, F2, F4)   # two-body tensor
    emat = edrixs.atom_hsoc('t2g', 0.2)                # one-body: SOC

Crystal-field, hopping or Zeeman terms are further additive contributions to
``emat``.

.. _many-body-operators:

Many-body operators
===================

The second stage picks a many-body Fock basis :math:`\lvert F \rangle` over the
single-particle spin-orbitals and evaluates the Hamiltonian in it.

``build_op(emat, umat, basis, backend=...)`` evaluates
:math:`\langle F_l | \hat{H} | F_r \rangle` for the one- and two-body terms
above and returns the many-body operator in the chosen backend's
representation; pass ``None`` for whichever term is absent. Since XAS and RIXS
involve initial states with no core hole and final states with exactly one core
hole, it is efficient to prepare separate Hamiltonians. ``get_ops`` is the
spectroscopy-oriented wrapper: given the ``_i`` and ``_n`` matrices and
``trans_mat`` from a model, it returns ``hmat_i``, ``hmat_n`` and the many-body
transition operators ``trans_ops`` in one call.

A few useful conventions are:

* Valence orbitals come first.  When a problem has both valence and core
  electrons, all valence spin-orbitals are indexed before all core
  spin-orbitals.
* A Fock state is a string of 1s (occupied) and 0s (empty), stored as an
  integer for efficiency.
* Bases are described compactly by :class:`~edrixs.FockBasisSpec`, built from
  ``(norb, nocc)`` pairs, one per shell with fixed occupancy::

      basis = edrixs.FockBasisSpec.from_args(norb_v, noccu_v, norb_c, noccu_c)

  For a single shell, ``edrixs.get_fock_basis_int(norb, noccu)`` returns a
  realized integer-encoded basis directly.  ``get_ops`` and ``build_op`` accept
  either the spec or a realized basis.

.. code-block:: python

    # For a t2g example with 2 electrons in the 6 spin-orbitals.
    basis = edrixs.get_fock_basis_int(6, 2)
    hmat = edrixs.build_op(emat, umat, basis, backend='dense')

.. _exact-diagonalization:

Exact diagonalization
=====================

The third stage finds the low-energy eigenstates of the many-body Hamiltonian.

``eval_i, evec_i = edrixs.ed(hmat, num_evals=n, backend=...)`` returns the
``n`` lowest eigenpairs:

* ``eval_i`` is a 1D real array ordered by increasing energy.
* For the ``dense`` and ``scipy`` backends ``evec_i`` is a 2D complex array; the
  eigenvector belonging to ``eval_i[k]`` is the column ``evec_i[:, k]``.  For
  the ``petsc`` backend ``evec_i`` is a list of distributed PETSc vectors.

.. code-block:: python

    import numpy as np

    # Lowest eigenpairs of the t2g Hamiltonian (here: all of them).
    eval_i, evec_i = edrixs.ed(hmat, num_evals=len(basis), backend='dense')

.. _xas:

XAS
===
``edrixs.xas`` provides spectra as a function of the incident photon energy
``ominc`` and returns an array of shape
``(len(ominc), len(pol_type))``.  Its main arguments are ``gamma_c``,
the inverse core-hole lifetime; ``pol_type``, a list of ``(kind, angle)``
polarization channels; the incident-beam angle ``thin`` and azimuth ``phi``;
and ``temperature``, which sets Boltzmann weights over the retained initial
states (so ``num_evals`` in ``ed`` must cover every thermally populated one).
The geometry and polarization conventions are on the :ref:`conventions` page.

.. code-block:: python

    ominc = np.linspace(11200, 11230, 50)
    xas = edrixs.xas(
        eval_i, evec_i, hmat_n, trans_ops, ominc,
        gamma_c=info['gamma_c'][0], thin=30*np.pi/180, phi=0,
        pol_type=[('linear', 0)], temperature=300, backend=backend,
    )
    # xas.shape == (len(ominc), len(pol_type))

.. _rixs:

RIXS
====

RIXS reuses ``eval_i``, ``evec_i``, ``hmat_i``, ``hmat_n`` and ``trans_ops``
from the XAS setup unchanged.  In addition to ``ominc`` you supply the
energy-loss grid ``eloss``, the emitted-beam angle ``thout``, the final-state /
resolution width ``gamma_f``, and 4-tuple
``(in_kind, in_angle, out_kind, out_angle)`` polarization channels.
``edrixs.rixs`` returns an array of shape
``(len(ominc), len(eloss), len(pol_type))``.  It is very common to compute two
different emitted polarizations and sum them, since this is what happens for
RIXS with no scattered-polarization analysis.

.. code-block:: python

    eloss = np.linspace(-0.5, 6, 400)
    pol_rixs = [('linear', 0, 'linear', 0),
                ('linear', 0, 'linear', np.pi/2)]   # two outgoing channels

    rixs = edrixs.rixs(
        eval_i, evec_i, hmat_i, hmat_n, trans_ops, ominc, eloss,
        gamma_c=info['gamma_c'][0], gamma_f=0.02,
        thin=30*np.pi/180, thout=60*np.pi/180, phi=0,
        pol_type=pol_rixs, temperature=300, backend=backend,
    )
    # rixs.shape == (len(ominc), len(eloss), len(pol_type))

    rixs_map = rixs.sum(-1)          # sum unresolved outgoing polarization

See :ref:`sphx_glr_auto_examples_example_02_single_atom_RIXS.py` for the full
worked calculation, including plotting the incident-energy / energy-loss map.

.. _backend:

Backend
=======

Stages two to four -- building operators, diagonalizing, and assembling spectra
-- do not implement their own linear algebra.  They delegate it to a backend
selected with the ``backend`` keyword, so one argument takes the same script
from a toy problem to a production one:

* ``'dense'`` -- full NumPy matrices.  Use it for small problems
  (dimension :math:`\lesssim 1000`) and for pedagogy.
* ``'scipy'`` -- SciPy sparse matrices with Lanczos / Krylov solvers.  The
  default, and a good choice for single-site and small cluster models.
* ``'petsc'`` -- distributed PETSc/SLEPc sparse matrices.  Needed for the large
  Hilbert spaces of Anderson impurity models; runs in parallel when the script
  is launched with ``mpirun``.

Purely numerical knobs (Krylov dimension, solver tolerances, ...) are passed per
backend through a ``backend_kws`` dictionary, so that the physical arguments to
``ed``, ``xas`` and ``rixs`` stay backend independent.

Where to go next
================

* :ref:`conventions` -- orbital orderings, single-particle bases, and the
  geometry / polarization / broadening conventions for spectra.
* :ref:`examples` -- pedagogical scripts that build up each concept above with
  physical commentary.
* :ref:`pythontips` -- practical advice for running and inspecting edrixs
  scripts.
* :ref:`reference` -- the full API reference.
