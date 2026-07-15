from collections.abc import Generator
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app import schemas
from app.security import check_public_api_rate_limit
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
    "/suggestions",
    response_model=schemas.MedicationSuggestionsResponse,
    responses={
        502: {"description": "RxNorm failed or returned an incomplete response"},
        504: {"description": "RxNorm request timed out"},
    },
)
def suggest_medications(
    request: Request,
    search_text: Annotated[
        str,
        Query(
            alias="q",
            min_length=2,
            max_length=100,
            description="Beginning of an RxNorm medication or ingredient name",
            examples=["para"],
        ),
    ],
    limit: Annotated[int, Query(ge=1, le=10)] = 8,
    rxnorm_service: RxNormService = Depends(get_rxnorm_service),
) -> schemas.MedicationSuggestionsResponse:
    check_public_api_rate_limit(request)
    cleaned_query = search_text.strip()
    if len(cleaned_query) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Medication suggestion query must contain at least 2 characters",
        )

    try:
        suggestions = rxnorm_service.suggest_medications(cleaned_query, limit)
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

    return schemas.MedicationSuggestionsResponse(
        data=schemas.MedicationSuggestionsData(
            query=cleaned_query,
            suggestions=suggestions,
        ),
    )


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
    request: Request,
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
    check_public_api_rate_limit(request)
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
