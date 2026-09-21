"""Empty option registry for the unimplemented PETSc backend contract."""

from __future__ import annotations

from .._backend_options import validate_backend_kws


OPTIONS = {
    'build_op': {},
    'get_ops': {},
    'ed': {},
    'xas': {},
    'rixs': {},
}


def validate_options(operation, backend_kws):
    """Reject options until the corresponding PETSc operation exists."""
    return validate_backend_kws('petsc', operation, backend_kws, OPTIONS)
