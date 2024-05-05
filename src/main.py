from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.currency.router import router as currency_router
from src.exchange_rate.router import router as exchange_rate_router
from src.exchange.router import router as exchange_router

from src.settings import app as app_settings


app = FastAPI(**app_settings.fastapi_app_configs())

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origins,
    allow_origin_regex=app_settings.cors_origins_regex,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PATCH"),
    allow_headers=app_settings.cors_headers,
)


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(currency_router, tags=["currency"])
app.include_router(exchange_rate_router, tags=["exchange rates"])
app.include_router(exchange_router, tags=["exchange"])
