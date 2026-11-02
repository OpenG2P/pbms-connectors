from .models import (
    BeneficiaryListSummaryDisability,
    BeneficiaryListSummaryFarmer,
    BeneficiaryListSummaryHousehold,
)


def get_models():
    return [
        BeneficiaryListSummaryFarmer,
        BeneficiaryListSummaryHousehold,
        BeneficiaryListSummaryDisability,
    ]
