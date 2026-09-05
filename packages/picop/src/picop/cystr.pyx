# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False, nonecheck=False, cdivision=True
"""
Fast :class:`str` accessors.
"""

import sys

cdef str EMPTY_STR = sys.intern("")
