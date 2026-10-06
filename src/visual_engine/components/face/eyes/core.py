"""Backward-compatible ocular API facade.

Implementation is owned by focused domain modules. Keep this surface stable for
legacy callers while preventing new logic from accumulating here.
"""
from .definitions import *
from .geometry_builder import *
