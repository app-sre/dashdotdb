"""
Services are used by the controllers to interact with the underlying Model
entities.
"""

import enum


class DataTypes(enum.Enum):
    # pylint: disable=invalid-name
    CSODataType = 1
    # pylint: disable=invalid-name
    DVODataType = 2
    # pylint: disable=invalid-name
    SLODataType = 3
