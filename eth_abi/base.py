import functools

from .grammar import (
    BasicType,
    normalize,
    parse,
)


def parse_type_str(expected_base=None, with_arrlist=False):
    """
    Used by BaseCoder subclasses as a convenience for implementing the
    ``from_type_str`` method required by ``ABIRegistry``.  Useful if normalizing
    then parsing a basic type string with an expected base is required in that
    method.
    """
    def decorator(old_from_type_str):
        @functools.wraps(old_from_type_str)
        def new_from_type_str(cls, type_str, registry):
            normalized_type_str = normalize(type_str)
            abi_type = parse(normalized_type_str)

            type_str_repr = repr(type_str)
            if type_str != normalized_type_str:
                type_str_repr = '{} (normalized to {})'.format(
                    type_str_repr,
                    repr(normalized_type_str),
                )

            if not isinstance(abi_type, BasicType):
                raise ValueError(
                    'Cannot create {} for non-basic type {}'.format(
                        cls.__name__,
                        type_str_repr,
                    )
                )

            if expected_base is not None and abi_type.base != expected_base:
                raise ValueError(
                    'Cannot create {} for type {}: expected type with '
                    "base '{}'".format(
                        cls.__name__,
                        type_str_repr,
                        expected_base,
                    )
                )

            if not with_arrlist and abi_type.arrlist is not None:
                raise ValueError(
                    'Cannot create {} for type {}: expected type with '
                    'no array dimension list'.format(
                        cls.__name__,
                        type_str_repr,
                    )
                )
            if with_arrlist and abi_type.arrlist is None:
                raise ValueError(
                    'Cannot create {} for type {}: expected type with '
                    'array dimension list'.format(
                        cls.__name__,
                        type_str_repr,
                    )
                )

            # Perform general validation of default solidity types
            abi_type.validate()

            return old_from_type_str(cls, abi_type, registry)

        return classmethod(new_from_type_str)

    return decorator


class BaseCoder:
    is_dynamic = False

    def __init__(self, **kwargs):
        """
        Creates an encoder or decoder with the given settings kwargs.
        """
        cls = type(self)

        # Ensure no unrecognized kwargs were given
        for key, value in kwargs.items():
            if not hasattr(cls, key):
                raise AttributeError(
                    'Property {key} not found on {cls_name} class. '
                    '`{cls_name}.__init__` only accepts keyword arguments which are '
                    'present on the {cls_name} class.'.format(
                        key=key,
                        cls_name=cls.__name__,
                    )
                )
            setattr(self, key, value)

        # Validate given combination of kwargs
        self.validate()

    def validate(self):
        """
        Validates that an encoder's or decoder's settings are valid in
        combination.
        """
        pass

    @classmethod
    def from_type_str(cls, type_str, registry):  # pragma: no cover
        """
        Used by ``ABIRegistry`` to get an appropriate encoder or decoder
        instance for the given type string and type registry.
        """
        raise NotImplementedError('Must implement `from_type_str`')
