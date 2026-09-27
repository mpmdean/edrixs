.. _nio-siam-xas-rixs:

*******************************************
NiO Anderson impurity model XAS and RIXS
*******************************************

This example uses :func:`~edrixs.models.model_siam_2d1p` to calculate Ni
:math:`L_{2,3}`-edge XAS and RIXS for a NiO Anderson impurity model. The model
contains a correlated Ni :math:`3d` shell and one bath site representing ten
symmetry-adapted O :math:`2p` ligand spin-orbitals. Hybridization allows the
calculation to include ligand-to-metal charge-transfer configurations.

The nominal impurity occupancy is ``nd=8``. The wrapper fixes one full
bath, so the initial valence sector contains 18 electrons; the intermediate
sector contains 19 valence electrons and five core electrons. The bath has
no Coulomb interaction. Its orbitals have the same symmetry as the five
impurity orbitals, even though they represent oxygen ligand combinations.

The model parameters are specified before constructing the Hamiltonian:

* ``slater`` contains the initial three d-d integrals and the intermediate
  seven d-d and d-p integrals. Atomic multipolar integrals are scaled to 80%,
  and the monopole integrals are specified directly as
  ``F0_dd=7.803669841269841`` and ``F0_dp=8.921474285714286`` eV.
  These correspond to average interactions ``U_dd=7.3`` and ``U_dp=8.5`` eV:
  ``U_dd = F0_dd - get_F0('d', F2_dd, F4_dd)`` and
  ``U_dp = F0_dp - get_F0('dp', G1_dp, G3_dp)``. Thus the F0 values include
  the multipolar corrections and are not themselves the average interactions.
* ``Delta=4.7`` eV is the configuration-average energy cost of transferring
  one bath electron to the impurity, without crystal field, hybridization,
  or multipolar Coulomb interactions. It is not a bare shell-center splitting.
  The wrapper recovers the average interactions from ``slater`` and uses
  :func:`~edrixs.utils.CT_imp_bath` and
  :func:`~edrixs.utils.CT_imp_bath_core_hole` to set the shell centers.
* ``impurity_levels`` and ``bath_levels`` each contain five orbital energies
  ordered ``(dz2, dzx, dzy, dx2-y2, dxy)``. The mean of each set is subtracted
  before applying its CT-derived center. Each value applies to both spins.
  Cubic splittings are 0.56 eV on the impurity and 1.44 eV on the bath.
* ``hyb`` gives five matching-orbital hoppings in that same order: 2.06 eV
  for the two eg orbitals and 1.21 eV for the three t2g orbitals.
* ``v_soc`` gives initial and intermediate impurity SOC; ``c_soc`` gives core
  SOC. This example retains equal impurity SOC in both states. The second
  entry can be changed to the atomic intermediate-state value.
* ``ext_B`` applies an effective exchange field along [112], acting on spin.
  ``om_shift=857.6`` eV aligns the spectrum with the Ni L edge; the wrapper
  combines this with its internally derived core energy.

All model energies and hoppings are in eV. The seven outputs from
:func:`~edrixs.models.model_siam_2d1p` pass directly to
:func:`~edrixs.solvers.get_ops`. The subsequent diagonalization, XAS, and RIXS
steps select the SciPy backend. Temperature (300 K), photon geometry,
polarization, and lifetime broadening are supplied to the spectrum routines.

.. plot:: pyplots/nio_siam_xas_rixs.py
   :context: reset
   :include-source: True
