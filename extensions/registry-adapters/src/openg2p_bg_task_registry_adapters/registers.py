"""Every register the adapters serve, mapped to its (DB, DCI) computations.

Each register also needs a block in the wrapper chart's values.yaml and
questions.own.yaml; test/test_register_config.py keeps them in step.
"""

from .computations import (
    DisabilityDB,
    DisabilityDCI,
    FarmerDB,
    FarmerDCI,
    HouseholdDB,
    HouseholdDCI,
)
from .models import G2PRegistryType

REGISTERS = {
    G2PRegistryType.FARMER.value: (FarmerDB, FarmerDCI),
    G2PRegistryType.HOUSEHOLD.value: (HouseholdDB, HouseholdDCI),
    G2PRegistryType.DISABILITY.value: (DisabilityDB, DisabilityDCI),
}
