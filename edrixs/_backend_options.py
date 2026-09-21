"""Shared definitions and validation for backend-specific options."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from difflib import get_close_matches
from math import isfinite
from numbers import Integral, Real


@dataclass(frozen=True)
class DynamicDefault:
    """A context-dependent default displayed in the backend documentation."""

    description: str


@dataclass(frozen=True)
class OptionSpec:
    """Description and validation rule for one ``backend_kws`` option."""

    default: object
    description: str
    validator: Callable[[object, str], None] | None = None


def default_text(spec):
    """Return the user-facing representation of an option default."""
    if isinstance(spec.default, DynamicDefault):
        return spec.default.description
    return repr(spec.default)


def validate_backend_kws(backend, operation, backend_kws, registry):
    """Validate, copy, and return options for one backend operation."""
    if backend_kws is None:
        options = {}
    elif not isinstance(backend_kws, Mapping):
        raise TypeError("backend_kws must be a mapping or None")
    else:
        options = dict(backend_kws)

    nonstring = [key for key in options if not isinstance(key, str)]
    if nonstring:
        raise TypeError(
            "backend_kws keys must be strings; got {}".format(
                ", ".join(repr(key) for key in nonstring)
            )
        )

    if operation not in registry:
        raise ValueError(
            "Unknown {} backend operation {!r}".format(backend, operation)
        )

    specifications = registry[operation]
    unknown = sorted(set(options) - set(specifications))
    if unknown:
        raise TypeError(_unknown_options_message(
            backend, operation, unknown, specifications, registry
        ))

    for name, value in options.items():
        validator = specifications[name].validator
        if validator is not None:
            validator(value, "backend_kws[{!r}]".format(name))
    return options


def _unknown_options_message(
        backend, operation, unknown, specifications, registry):
    noun = "option" if len(unknown) == 1 else "options"
    message = "Unknown backend_kws {} for {}.{}: {}.".format(
        noun,
        backend,
        operation,
        ", ".join(repr(name) for name in unknown),
    )

    hints = []
    allowed = sorted(specifications)
    for name in unknown:
        matches = get_close_matches(name, allowed, n=1, cutoff=0.6)
        if matches:
            hints.append("{!r} -> {!r}".format(name, matches[0]))
            continue

        other_operations = sorted(
            candidate_operation
            for candidate_operation, candidate_options in registry.items()
            if candidate_operation != operation and name in candidate_options
        )
        if other_operations:
            hints.append(
                "{!r} is valid for {}.{}".format(
                    name, backend, "/".join(other_operations)
                )
            )

    if hints:
        message += " Suggestions: {}.".format("; ".join(hints))
    message += " Allowed options: {}.".format(
        ", ".join(allowed) if allowed else "none"
    )
    return message


def positive_integer(value, label):
    """Require an integer greater than zero."""
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError("{} must be a positive integer".format(label))
    if value < 1:
        raise ValueError("{} must be a positive integer".format(label))


def optional_positive_integer(value, label):
    """Require ``None`` or an integer greater than zero."""
    if value is not None:
        positive_integer(value, label)


def positive_real(value, label):
    """Require a real number greater than zero."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError("{} must be a positive real number".format(label))
    if not isfinite(value) or value <= 0:
        raise ValueError("{} must be a positive real number".format(label))


def nonnegative_real(value, label):
    """Require a real number greater than or equal to zero."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError("{} must be a nonnegative real number".format(label))
    if not isfinite(value) or value < 0:
        raise ValueError("{} must be a nonnegative real number".format(label))


def boolean(value, label):
    """Require a Boolean value without accepting integers as booleans."""
    if not isinstance(value, bool):
        raise TypeError("{} must be a bool".format(label))


def integer_choice(*choices):
    """Return a validator requiring one of the supplied integer choices."""
    choices = tuple(choices)

    def validate(value, label):
        if isinstance(value, bool) or not isinstance(value, Integral):
            raise TypeError("{} must be an integer".format(label))
        if value not in choices:
            raise ValueError(
                "{} must be one of {}".format(label, choices)
            )

    return validate


def communicator(value, label):
    """Require the subset of the mpi4py communicator protocol EDRIXS uses."""
    required = ('Get_rank', 'Get_size', 'Barrier', 'bcast', 'py2f')
    missing = [method for method in required if not hasattr(value, method)]
    if missing:
        raise TypeError(
            "{} must be an mpi4py communicator; missing {}".format(
                label, ", ".join(missing)
            )
        )
