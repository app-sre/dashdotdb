"""
Services are used by the controllers to interact with the underlying Model
entities.
"""

import enum


class DataTypes(enum.Enum):
    CSODataType = 1
    DVODataType = 2
    SLODataType = 3
