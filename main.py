from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.dashboard_routes import router as dashboard_router
from app.api.manual_review_routes import router as manual_review_router
from app.api.monitoring_routes import router as monitoring_router
from app.core.logging import configure_logging


configure_logging()


app = FastAPI(
    title="SupportIQ AI",
)

app.include_router(manual_review_router)
app.include_router(monitoring_router)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

app.include_router(dashboard_router)


def main() -> None:
    print("SupportIQ AI initialized.")


if __name__ == "__main__":
    main()
