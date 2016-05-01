# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

from __future__ import absolute_import, division, print_function

from cryptography.hazmat.backends.multibackend import MultiBackend

_default_backend = None


def _available_backends():
    import cryptography.hazmat.backends.openssl.backend
    return [ cryptography.hazmat.backends.openssl.backend ]


def default_backend():
    global _default_backend

    if _default_backend is None:
        _default_backend = MultiBackend(_available_backends())

    return _default_backend
