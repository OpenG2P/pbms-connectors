from openg2p_bg_task_models.errors import BGTaskErrorCodes, BGTaskException

from ..computations import FarmerDB, FarmerDCI, HouseholdDB, HouseholdDCI
from ..config import RegistryAdapterSettings
from ..interface import RegistryInterface
from ..models import G2PRegistryType

_CLASSES = {
    (G2PRegistryType.FARMER.value, "db"): FarmerDB,
    (G2PRegistryType.FARMER.value, "dci"): FarmerDCI,
    (G2PRegistryType.HOUSEHOLD.value, "db"): HouseholdDB,
    (G2PRegistryType.HOUSEHOLD.value, "dci"): HouseholdDCI,
}


class RegistryFactory:
    """Pick a computation from the program registry and the deployment connector."""

    @staticmethod
    def get_registry_class(target_registry: str) -> RegistryInterface:
        connector = RegistryAdapterSettings.get_config().connector
        cls = _CLASSES.get((target_registry, connector))
        if cls is None:
            raise BGTaskException(code=BGTaskErrorCodes.INVALID_REQUEST)
        return cls()
