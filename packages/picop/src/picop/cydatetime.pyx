# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
"""
datetime.h helpers (imports DateTime C-API on load).
"""

from cpython.datetime cimport import_datetime

import_datetime()
