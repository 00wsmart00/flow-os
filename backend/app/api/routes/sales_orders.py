from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.api.dependencies import SessionDependency
from app.repositories.inventory import InventoryRepository
from app.repositories.sales_orders import SalesOrderRepository
from app.schemas.errors import ErrorResponse
from app.schemas.material_requirements import SalesOrderRequirementsResponse
from app.schemas.orders import SalesOrderListResponse, SalesOrderQuery, SalesOrderResponse
from app.schemas.shortage import ShortageAnalysisResponse
from app.services.sales_orders import SalesOrderService
from app.services.shortage_analysis import ShortageAnalysisService

router = APIRouter(prefix="/sales-orders", tags=["sales-orders"])


@router.get("", response_model=SalesOrderListResponse)
def list_sales_orders(
    session: SessionDependency,
    query: Annotated[SalesOrderQuery, Query()],
) -> SalesOrderListResponse:
    service = SalesOrderService(SalesOrderRepository(session))
    return service.search(query)


@router.get(
    "/{order_id}",
    response_model=SalesOrderResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Sales order not found",
        }
    },
)
def get_sales_order(
    session: SessionDependency,
    order_id: Annotated[int, Path(ge=1)],
) -> SalesOrderResponse:
    service = SalesOrderService(SalesOrderRepository(session))
    return service.get_by_id(order_id)


@router.get(
    "/{order_id}/material-requirements",
    response_model=SalesOrderRequirementsResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Sales order not found",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "Order or BOM input is incomplete or ineligible",
        },
    },
)
def get_sales_order_material_requirements(
    session: SessionDependency,
    order_id: Annotated[int, Path(ge=1)],
) -> SalesOrderRequirementsResponse:
    service = SalesOrderService(SalesOrderRepository(session))
    return service.calculate_material_requirements(order_id)


@router.get(
    "/{order_id}/shortage-analysis",
    response_model=ShortageAnalysisResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Sales order or inventory snapshot not found",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "Order, BOM, snapshot, or unit input cannot be analyzed",
        },
    },
)
def get_sales_order_shortage_analysis(
    session: SessionDependency,
    order_id: Annotated[int, Path(ge=1)],
    snapshot_id: Annotated[int, Query(ge=1)],
) -> ShortageAnalysisResponse:
    service = ShortageAnalysisService(
        SalesOrderRepository(session),
        InventoryRepository(session),
    )
    return service.analyze(order_id, snapshot_id)
