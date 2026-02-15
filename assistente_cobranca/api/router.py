from fastapi import APIRouter

from assistente_cobranca.api.routes.debtors import router as debtors_router
from assistente_cobranca.api.routes.invoices import router as invoices_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(debtors_router)
api_router.include_router(invoices_router)

