from abc import ABC, abstractmethod
from typing import Iterator, Optional

from openg2p_bg_task_models.models import BeneficiaryListDetails
from openg2p_bg_task_models.schemas import BeneficiarySearchResponsePayload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..schema import BeneficiaryListSummaryPayload


class RegistryInterface(ABC):
    """Transport-free registry contract.

    Implementations open their own registry session or HTTP client. Callers
    pass ``pbms_domain`` strings and beneficiary-list rows, never SQL.
    """

    @abstractmethod
    async def get_summary(
        self,
        beneficiary_list_id: str,
        bg_task_session: AsyncSession,
        formated: bool = False,
    ) -> BeneficiaryListSummaryPayload:
        raise NotImplementedError

    @abstractmethod
    def get_summary_sync(
        self, beneficiary_list_id: str, bg_task_session: Session
    ) -> BeneficiaryListSummaryPayload:
        raise NotImplementedError

    @abstractmethod
    def compute_eligibility_statistics(
        self,
        beneficiary_list_details: list[BeneficiaryListDetails],
        base_summary,
        bg_task_session: Session,
    ):
        raise NotImplementedError

    @abstractmethod
    def compute_entitlement_statistics(
        self, beneficiary_list_id: str, bg_task_session: Session
    ):
        raise NotImplementedError

    @abstractmethod
    def iter_eligible_ids(
        self,
        rules: list[tuple[str, str]],
        batch_size: int,
    ) -> Iterator[list[str]]:
        """Yield batches of registrant ids for ``(pbms_domain, set_operator)`` rules."""
        raise NotImplementedError

    @abstractmethod
    def iter_priority_ids(
        self,
        priority_domains: list[str],
        enrolled_ids: list[str],
        fallback_rules: list[tuple[str, str]],
        batch_size: int,
    ) -> Iterator[list[str]]:
        raise NotImplementedError

    @abstractmethod
    def entitlement_multipliers(
        self,
        registrant_ids: list[str],
        pbms_domain: str,
        multiplier_field: Optional[str] = None,
    ) -> dict[str, float]:
        """Return ``{registrant_id: multiplier}`` for registrants the domain matches."""
        raise NotImplementedError

    @abstractmethod
    async def search_beneficiaries(
        self,
        bg_task_session: AsyncSession,
        beneficiary_list_id: str,
        target_registry: str,
        search_domain: Optional[str],
        page: int = 1,
        page_size: int = 10,
        order_by: str = "internal_record_id asc",
    ) -> tuple[BeneficiarySearchResponsePayload, int]:
        raise NotImplementedError
