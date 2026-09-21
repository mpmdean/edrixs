.. _scipy-backend-options:

************************
SciPy and dense keywords
************************

:doc:`Back to the backend overview <../backend>`

The ``dense`` backend uses the same options and numerical solvers as ``scipy``;
only its operator representation differs.  Options are specific to the stage
where they are supplied.

``build_op`` and ``get_ops``
============================

.. backend-options:: scipy get_ops

Here ``tol`` controls operator truncation.  It is separate from the
eigensolver tolerance accepted by ``ed``.

``ed``
======

.. backend-options:: scipy ed

``xas``
=======

.. backend-options:: scipy xas

``rixs``
========

.. backend-options:: scipy rixs
