.. _conventions:

***********
Conventions
***********

This page collects the fixed conventions that edrixs assumes unless you say
otherwise: the orbital orderings and single-particle bases in which matrices and
tensors are returned, and the geometry, polarization and broadening conventions
used to build spectra.  The :ref:`introduction` describes the interface that
relies on them, and the :ref:`pedagogical examples <examples>` work through the
same material in more physical detail.

Default orbital ordering and single-particle bases
==================================================

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

Spectral conventions
====================

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
