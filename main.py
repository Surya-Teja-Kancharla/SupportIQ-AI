from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.dashboard_routes import router as dashboard_router
from app.core.logging import configure_logging


configure_logging()


app = FastAPI(
    title="SupportIQ AI",
)


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
