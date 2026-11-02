from openg2p_bg_task_models.errors import BGTaskErrorCodes, BGTaskException

from ..config import get_connection
from ..connection import RegistryConnectionError
from ..interface import RegistryInterface
from ..registers import REGISTERS


class RegistryFactory:
    """Pick a computation from the program registry and that register's connector."""

    @staticmethod
    def get_registry_class(target_registry: str) -> RegistryInterface:
        if target_registry not in REGISTERS:
            raise BGTaskException(
                code=BGTaskErrorCodes.INVALID_REQUEST,
                message=f"Unknown register '{target_registry}'.",
            )
        db_cls, dci_cls = REGISTERS[target_registry]
        try:
            connection = get_connection(
                target_registry, dci_cls.reg_type, dci_cls.reg_record_type
            )
        except RegistryConnectionError as exc:
            raise BGTaskException(
                code=BGTaskErrorCodes.INVALID_REQUEST, message=str(exc)
            ) from exc
        cls = db_cls if connection.connector == "db" else dci_cls
        return cls(connection)
