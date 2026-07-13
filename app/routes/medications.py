from collections.abc import Generator
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app import schemas
from app.services.rxnorm import (
    RXNORM_BASE_URL,
    RXNORM_TIMEOUT_SECONDS,
    IncompleteRxNormResponseError,
    MedicationNotFoundError,
    RxNormService,
    RxNormTimeoutError,
    RxNormUnavailableError,
)

router = APIRouter(prefix="/medications", tags=["Medications"])


def get_rxnorm_service() -> Generator[RxNormService, None, None]:
    with httpx.Client(
        base_url=RXNORM_BASE_URL,
        timeout=RXNORM_TIMEOUT_SECONDS,
    ) as client:
        yield RxNormService(client)


@router.get(
    "/search",
    response_model=schemas.MedicationSearchResponse,
    responses={
        404: {"description": "No exact or normalized RxNorm match"},
        502: {"description": "RxNorm failed or returned an incomplete response"},
        504: {"description": "RxNorm request timed out"},
    },
)
def search_medication(
    name: Annotated[
        str,
        Query(
            min_length=1,
            max_length=100,
            description="Medication name to search in RxNorm",
            examples=["Augmentin"],
        ),
    ],
    rxnorm_service: RxNormService = Depends(get_rxnorm_service),
) -> schemas.MedicationSearchResponse:
    drug_name = name.strip()
    if len(drug_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Medication name must contain at least 2 characters",
        )

    try:
        return rxnorm_service.search_medication(drug_name)
    except MedicationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found in RxNorm",
        )
    except RxNormTimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="RxNorm did not respond before the timeout",
        )
    except IncompleteRxNormResponseError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="RxNorm returned an incomplete response",
        )
    except RxNormUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="RxNorm is currently unavailable",
        )
