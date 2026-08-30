.. _introduction:

**********************
Introduction to edrixs
**********************

edrixs computes X-ray absorption (XAS) and resonant inelastic X-ray scattering
(RIXS) spectra by exact diagonalization (ED) of model Hamiltonians for
correlated electrons.  A calculation is always built from the same pieces: a set
of single-particle matrices, a many-body Fock basis, a many-body Hamiltonian
obtained from the two, its low-energy eigenstates, and finally a spectrum built
from transition operators acting on those eigenstates.

This page describes the conventions that hold everywhere in edrixs and then
walks through the basic procedures for computing a ground state, an XAS
spectrum, and a RIXS spectrum.  The :ref:`pedagogical examples <examples>` work
through the same material in more physical detail.

Design conventions
==================

Separate the physical model from the numerical method
-----------------------------------------------------

edrixs is organised into three layers that you use in order:

``edrixs.models``
    ``model_1v1c``, ``model_2v1c`` and ``model_siam`` set up a physical problem
    -- one valence shell and one core shell, two valence shells and one core
    shell, or an Anderson impurity model.  Each returns a *backend-independent*
    description of the problem: the one-body matrices ``emat_i`` / ``emat_n``,
    the Coulomb tensors ``umat_i`` / ``umat_n``, compact Fock-basis
    specifications ``basis_i`` / ``basis_n``, and the Cartesian dipole matrices
    ``trans_mat``.  The ``_i`` quantities describe the initial and final states
    (no core hole); the ``_n`` quantities describe the intermediate state (one
    core hole).  These functions do not build many-body operators and do not
    diagonalize anything.

``edrixs`` solver interface
    ``build_op``, ``get_ops``, ``ed``, ``xas`` and ``rixs`` are thin,
    method-neutral wrappers.  ``build_op`` / ``get_ops`` turn single-particle
    matrices into many-body operators in the Fock basis, ``ed`` returns the
    lowest eigenpairs, and ``xas`` / ``rixs`` build the spectra.

backends
    The actual linear algebra is delegated to a backend selected with the
    ``backend`` keyword:

    * ``'dense'`` -- full NumPy matrices.  Use it for small problems
      (dimension :math:`\lesssim 1000`) and for pedagogy.
    * ``'scipy'`` -- SciPy sparse matrices with Lanczos / Krylov solvers.  The
      default, and a good choice for single-site and small cluster models.
    * ``'petsc'`` -- distributed PETSc/SLEPc sparse matrices.  Needed for the
      large Hilbert spaces of Anderson impurity models; runs in parallel when
      the script is launched with ``mpirun``.

    Purely numerical knobs (Krylov dimension, solver tolerances, ...) are passed
    per backend through a ``backend_kws`` dictionary, so that physical arguments
    stay backend independent.

The older ``ed_1v1c_py`` / ``xas_1v1c_fort`` / ... entry points are retained for
backward compatibility but are deprecated in favour of the staged interface
above.

Second quantization and the Fock basis
--------------------------------------

edrixs works in second quantization.  You first define a single-particle basis
:math:`\alpha` of spin-orbitals, then a many-body Fock basis
:math:`\lvert F \rangle` with respect to it.  A many-body Hamiltonian is
assembled from

.. math::

   \hat{H} = \sum_{ij} t_{ij}\, \hat{f}_i^{\dagger} \hat{f}_j
           + \sum_{ijlk} U_{ijlk}\, \hat{f}_i^{\dagger} \hat{f}_j^{\dagger}
             \hat{f}_k \hat{f}_l ,

where the one-body coefficients :math:`t_{ij}` are passed as ``emat`` and the
two-body coefficients :math:`U_{ijkl}` as ``umat``.  ``build_op(emat, umat,
basis, backend=...)`` evaluates :math:`\langle F_l | \hat{H} | F_r \rangle` and
returns the many-body operator in the chosen backend's representation.  Pass
``None`` for whichever term is absent.

Conventions for the Fock basis:

* **Valence orbitals come first.**  When a problem has both valence and core
  electrons, all valence spin-orbitals are indexed before all core
  spin-orbitals.
* A Fock state is a string of 1s (occupied) and 0s (empty).  It is stored as an
  integer for efficiency, with orbital 0 as the most significant bit, so
  ``"{:0{width}b}".format(state, width=norb)`` prints the occupations in orbital
  order.  (This is the reverse of Eq. (13)-(14) in the 2019 CPC paper, where the
  first orbital is the least significant bit; the basis *ordering* is unchanged,
  only the integer encoding of an individual state.)
* Bases are described compactly by :class:`~edrixs.FockBasisSpec`.  Build one
  from ``(norb, nocc)`` pairs, one pair per shell with fixed occupancy::

      basis = edrixs.FockBasisSpec.from_args(norb_v, noccu_v, norb_c, noccu_c)

  For a single shell, ``edrixs.get_fock_basis_int(norb, noccu)`` returns a
  realized integer-encoded basis directly.  ``get_ops`` and ``build_op`` accept
  either the spec or a realized basis.

Default orbital ordering and single-particle bases
--------------------------------------------------

Unless specified otherwise, edrixs uses these orderings.

* **Spin:** interleaved, ``up, dn, up, dn, ...``.
* **Complex spherical harmonics** :math:`Y_l^m`: ``m = -l, -l+1, ..., l-1, l``.
* **Real spherical harmonics** (the Wannier90 ordering):

  - ``p``:  :math:`p_x, p_y, p_z`
  - ``d``:  :math:`d_{3z^2-r^2}, d_{xz}, d_{yz}, d_{x^2-y^2}, d_{xy}`
  - ``t2g``:  :math:`d_{xz}, d_{yz}, d_{xy}`
  - ``f``:  :math:`f_{z^3}, f_{xz^2}, f_{yz^2}, f_{z(x^2-y^2)}, f_{xyz},
    f_{x(x^2-3y^2)}, f_{y(3x^2-y^2)}`

* :math:`\lvert j^2, j_z \rangle` **basis** (SOC diagonal): the
  :math:`j = l-1/2` block first, then the :math:`j = l+1/2` block, each ordered
  :math:`-j, -j+1, ..., j`.

The **default single-particle basis used to define the Fock basis** is:

* complex spherical harmonics for ``p``, ``d``, ``t2g`` and ``f`` (``p`` and
  ``t2g`` share the same complex-harmonic basis);
* the :math:`\lvert j^2, j_z \rangle` basis for ``p12``, ``p32``, ``d32``,
  ``d52``, ``f52`` and ``f72``.

Helper functions that return matrices or tensors -- ``get_umat_slater``,
``get_trans_oper``, ``cf_cubic_d``, ``cf_tetragonal_d``, ``cf_trigonal_t2g`` and
so on -- return them **in this default basis**.

.. important::

   You may choose any single-particle basis for the Fock basis, but every
   matrix and Coulomb tensor entering the Hamiltonian must be expressed in that
   *same* basis.  Transform one-body matrices with :func:`~edrixs.cb_op` and
   Coulomb tensors with :func:`~edrixs.transform_utensor`.  The recommended
   practice is to keep the default basis and only transform the extra matrices
   you supply (for example a crystal-field matrix) into it.  ``cb_op`` applies

   .. math::

      \hat{O}^{\prime} = T^{\dagger}\, \hat{O}\, T ,

   with, e.g., ``T = edrixs.tmat_c2r('d', ispin=True)`` to go from complex to
   real harmonics or ``edrixs.tmat_r2c`` for the reverse.

Eigenvalues and eigenvectors
----------------------------

``eval_i, evec_i = edrixs.ed(hmat, num_evals=n, backend=...)`` returns the
``n`` lowest eigenpairs.

* ``eval_i`` is a 1D real array ordered by increasing energy.
* For the ``dense`` and ``scipy`` backends ``evec_i`` is a 2D complex array; the
  eigenvector belonging to ``eval_i[k]`` is the column ``evec_i[:, k]``.  For
  the ``petsc`` backend ``evec_i`` is a list of distributed PETSc vectors.

All information about a state is in its eigenvector.  To label or analyze
states, build the operator of interest as a single-particle matrix, push it
through ``build_op`` into the *same* Fock basis, and take its expectation value
against the eigenvectors.  Useful choices are
:math:`\mathbf{S}^2`, :math:`\mathbf{L}^2`, :math:`\mathbf{J}^2` and orbital
occupation numbers :math:`n_{xz/yz/xy}`.

Energies, Slater integrals and parameters
-----------------------------------------

* All energies are in **eV**.
* The absolute energy of a core level is not known to the calculation.  Set the
  resonance position by hand through ``shell_level`` (or ``c_level``) and an
  offset chosen to match experiment.
* Coulomb interactions are parameterized by Slater integrals :math:`F^k`
  (and :math:`G^k` for core-valence terms).  edrixs ships Hartree-Fock values
  in ``edrixs.get_atom_data`` and provides conversions:
  ``UJ_to_UdJH``, ``UdJH_to_F0F2F4`` (``...F0F2F4F6`` for ``f`` shells) and
  ``get_F0``.  The :math:`d`-shell relations
  (``F2 = J / (3/49 + 20 \cdot 0.625/441)``, ``F4 = 0.625\,F2``,
  ``JH = (F2+F4)/14``, ``Ud = U - (4/49)(F2+F4)``) are also used for ``4d`` and
  ``5d`` as an approximation.
* Atomic Slater and SOC values are usually **scaled down** (often 70-90%) to
  approximate screening in the solid.

Spectral conventions
--------------------

* **Geometry** follows Figure 1 of Y. Wang *et al.*,
  `Comput. Phys. Commun. 243, 151 (2019)
  <https://doi.org/10.1016/j.cpc.2019.04.018>`_.  The incident and scattered
  beams are set by ``thin`` and ``thout`` and the azimuth by ``phi`` (radians),
  all relative to the sample axes.  By default the crystal-field
  :math:`x, y, z` axes coincide with the lab frame; use ``loc_axis`` (model) or
  ``scatter_axis`` (solver) to change this.
* **Polarization** is given as a list of channels.  For XAS each entry is
  ``(kind, angle)`` with ``kind`` one of ``'linear'``, ``'circular'`` or
  ``'isotropic'`` (the last for powders).  For RIXS each entry is a 4-tuple
  ``(in_kind, in_angle, out_kind, out_angle)``; sum the two outgoing channels
  when the experiment does not resolve emitted polarization.
* **Broadening** is a Lorentzian half width at half maximum.  ``gamma_c`` is the
  inverse core-hole lifetime (it dominates XAS and the incident-energy axis of
  RIXS); ``gamma_f`` is the final-state / resolution width on the RIXS
  energy-loss axis.  Either may be a scalar or an array over incident energy.
* **Temperature** (in K) sets Boltzmann weights over the retained low-energy
  initial states, so ``num_evals`` in ``ed`` must be large enough to cover all
  thermally populated states.
* Returned array shapes: ``xas`` has shape ``(len(ominc), len(pol_type))``;
  ``rixs`` has shape ``(len(ominc), len(eloss), len(pol_type))``.

Computing a ground state
========================

edrixs can be used directly as a small ED calculator.  The steps are: build the
single-particle matrices, build a Fock basis, combine them into a many-body
Hamiltonian, and diagonalize.

.. code-block:: python

    import numpy as np
    import edrixs

    # A t2g shell (l_eff = 1): 6 spin-orbitals, 2 electrons.
    norb, noccu = 6, 2
    Ud, JH = edrixs.UJ_to_UdJH(4, 1)
    F0, F2, F4 = edrixs.UdJH_to_F0F2F4(Ud, JH)

    # Single-particle ingredients, in the default (complex-harmonic) basis.
    umat = edrixs.get_umat_slater('t2g', F0, F2, F4)   # two-body tensor
    emat = edrixs.atom_hsoc('t2g', 0.2)                # one-body: SOC

    # Many-body Fock basis and Hamiltonian.
    basis = edrixs.get_fock_basis_int(norb, noccu)
    H = edrixs.build_op(emat, umat, basis, backend='dense')

    # Lowest eigenpairs (here: all of them).
    e, v = edrixs.ed(H, num_evals=len(basis), backend='dense')

To interpret the result, build angular-momentum operators the same way and take
expectation values against ``v``::

    l = 1
    orb = edrixs.get_orb_momentum(l, ispin=True)
    spin = edrixs.get_spin_momentum(l)
    opL = [edrixs.build_op(c, None, basis, backend='dense') for c in orb]
    opS = [edrixs.build_op(c, None, basis, backend='dense') for c in spin]
    L2 = sum(np.dot(o, o) for o in opL)
    S2 = sum(np.dot(o, o) for o in opS)
    L2_val = edrixs.cb_op(L2, v).diagonal().real   # gives L(L+1)
    S2_val = edrixs.cb_op(S2, v).diagonal().real   # gives S(S+1)

Crystal-field, hopping or Zeeman terms are just further contributions to
``emat``.  If you supply such a matrix in the real-harmonic basis, transform it
into the default basis first, e.g.
``cf = edrixs.cb_op(cf_real, edrixs.tmat_r2c('d', True))``.

See :ref:`sphx_glr_auto_examples_example_00_ed_calculator.py` and
:ref:`sphx_glr_auto_examples_example_01_crystal_field.py`.

Computing XAS
=============

For a spectrum you need both the initial/final state (no core hole) and the
intermediate state (one core hole).  The model constructor returns both, plus
the dipole matrices; ``get_ops`` turns them into many-body operators.

.. code-block:: python

    import numpy as np
    import edrixs

    shell_name = ('t2g', 'p32')     # valence shell, core shell
    v_noccu = 4
    backend = 'scipy'

    # Physical parameters (eV).
    Ud, JH, lam = 2.0, 0.25, 0.42
    F0_d, F2_d, F4_d = edrixs.UdJH_to_F0F2F4(Ud, JH)
    info = edrixs.get_atom_data('Ir', '5d', v_noccu, edge='L3')
    slater = ([F0_d, F2_d, F4_d],                      # initial
              [F0_d, F2_d, F4_d, 0, 0, 0, 0, 0, 0])    # with core hole

    # Extra one-body physics on the valence shell (here: valence SOC).
    imp_mat = edrixs.atom_hsoc('t2g', lam)

    # Offset that places the resonance near the experimental edge energy.
    off = 11215 - 6

    # 1. Backend-independent model.
    out = edrixs.model_1v1c(
        shell_name, v_noccu=v_noccu, shell_level=(0, -off),
        v_othermat=imp_mat, slater=slater,
    )
    emat_i, umat_i, basis_i, emat_n, umat_n, basis_n, trans_mat = out

    # 2. Many-body operators for the chosen backend.
    hmat_i, hmat_n, trans_ops = edrixs.get_ops(
        emat_i, umat_i, basis_i, emat_n, umat_n, basis_n, trans_mat,
        backend=backend,
    )

    # 3. Low-energy initial states (enough to cover the thermal population).
    eval_i, evec_i = edrixs.ed(hmat_i, num_evals=2, backend=backend)

    # 4. XAS spectrum.
    ominc = np.linspace(11200, 11230, 50)
    xas = edrixs.xas(
        eval_i, evec_i, hmat_n, trans_ops, ominc,
        gamma_c=info['gamma_c'][0], thin=30*np.pi/180, phi=0,
        pol_type=[('linear', 0)], temperature=300, backend=backend,
    )
    # xas.shape == (len(ominc), len(pol_type))

Anderson impurity models follow the same pattern with ``model_siam`` (passing
``nbath``, ``imp_mat``, ``bath_level`` and ``hyb``) and typically
``backend='petsc'``.  See
:ref:`sphx_glr_auto_examples_example_02_single_atom_RIXS.py` and
:ref:`sphx_glr_auto_examples_example_03_AIM_XAS.py`.

Computing RIXS
==============

RIXS reuses the operators and eigenstates from the XAS setup.  In addition to
``ominc`` you provide the energy-loss grid ``eloss``, the emitted-beam angle
``thout``, the final-state width ``gamma_f``, and 4-tuple polarization channels.

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

Where to go next
================

* :ref:`examples` -- pedagogical scripts that build up each concept above with
  physical commentary.
* :ref:`pythontips` -- practical advice for running and inspecting edrixs
  scripts.
* :ref:`reference` -- the full API reference.
