===============================
edrixs
===============================

|ci| |conda| |pypi| |docs| |doi| |binder|

.. |ci| image:: https://github.com/EDRIXS/edrixs/actions/workflows/ci-test.yml/badge.svg?branch=master&event=push
   :target: https://github.com/EDRIXS/edrixs/actions/workflows/ci-test.yml?query=branch%3Amaster+event%3Apush
   :alt: CI status

.. |conda| image:: https://img.shields.io/conda/vn/conda-forge/edrixs.svg
   :target: https://anaconda.org/conda-forge/edrixs
   :alt: Conda-forge version

.. |pypi| image:: https://img.shields.io/pypi/v/edrixs.svg
   :target: https://pypi.org/project/edrixs/
   :alt: PyPI version

.. |docs| image:: https://img.shields.io/badge/docs-online-blue.svg
   :target: https://edrixs.github.io/edrixs/
   :alt: Documentation

.. |doi| image:: https://img.shields.io/badge/DOI-10.1016%2Fj.cpc.2019.04.018-blue.svg
   :target: https://doi.org/10.1016/j.cpc.2019.04.018
   :alt: Paper DOI

.. |binder| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/edrixs/edrixs.git/master?urlpath=lab
   :alt: Launch Binder

EDRIXS is an open source toolkit for simulating XAS and RIXS spectra based on exact diagonalization of model Hamiltonians.
It was started as part of the `COMSCOPE project <https://www.bnl.gov/comscope/>`_ in the
Center for Computational Material Spectroscopy and Design, Brookhaven National Laboratory and is now maintained and
developed in collaboration between the `Condensed Matter Physics and Materials Science Division <https://www.bnl.gov/cmpmsd/>`_
and the `National Syncrotron Light Source II <https://www.bnl.gov/nsls2/>`_.

* Free software: GNU General Public License Version 3
* Documentation: https://edrixs.github.io/edrixs.
* Launch a `MyBinder Session <https://mybinder.org/v2/gh/edrixs/edrixs.git/master?urlpath=lab>`_ to try the code.

Features
--------

* ED solver
* XAS spectra
* RIXS spectra

How to cite
-----------
If you are using the EDRIXS code to do some studies and would like to publish your great works, it would be really appreciated if you can cite the following paper:

``EDRIXS: An open source toolkit for simulating spectra of resonant inelastic x-ray scattering, Y.L. Wang, G. Fabbris, M.P.M. Dean and G. Kotliar``, `Computer Physics Communications,243, 151 (2019) <https://doi.org/10.1016/j.cpc.2019.04.018>`_, `arXiv:1812.05735 <https://arxiv.org/abs/1812.05735/>`_.


Usage
-----
For Linux and macOS, we recommend installing the released edrixs package with
Mamba in a separate environment:

  .. code-block:: bash

     mamba create --name edrixs_env -c conda-forge --strict-channel-priority \
         edrixs matplotlib
     conda activate edrixs_env

For Windows, we recommend Docker. See https://edrixs.github.io/edrixs for the
complete installation, verification, requirements, and Docker instructions.
