from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.errors import register_exception_handlers
from app.routers import auth, me

app = FastAPI(
    title="Auth API",
    version="1.0.0",
    description="v1 auth + profile contract",
)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(me.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Locked contract form: authenticated by default, login opts out explicitly.
    openapi_schema["security"] = [{"bearerAuth": []}]
    # GET /me inherits the top-level default; drop its auto-injected per-op
    # security so the artifact shows inheritance, not a duplicated override.
    openapi_schema["paths"]["/me"]["get"].pop("security", None)
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
