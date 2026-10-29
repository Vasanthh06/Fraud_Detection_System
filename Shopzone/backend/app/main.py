"""Shopzone — FastAPI entrypoint.

Serves the API under /api and the static frontend (frontend/) at /.
Single port, single command:  uvicorn app.main:app --port 8000
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import APP_NAME, CORS_ORIGINS, FRONTEND_DIR
from .fraud import load_models
from .routers import admin, auth, shop

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("shopzone")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from . import db

    db.init_db()  # create/verify schema (SQLite file or Neon Postgres)
    load_models()
    logger.info("%s ready — API + frontend on this port", APP_NAME)
    yield


app = FastAPI(title="Shopzone", version="2.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https://images.unsplash.com; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    if request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.middleware("http")
async def cache_control(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith(("/css/", "/js/")):
        response.headers["Cache-Control"] = "no-cache"   # revalidate every load
    else:
        response.headers["Cache-Control"] = "no-store"   # pages + API always fresh
    return response


@app.exception_handler(HTTPException)
async def http_error(_request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.middleware("http")
async def access_log(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api"):
        logger.info("%s %s %s", request.method, request.url.path, response.status_code)
    return response


app.include_router(auth.router)
app.include_router(shop.router)
app.include_router(admin.router)


@app.get("/api/health", include_in_schema=False)
def health():
    from .fraud import models_available

    return {"status": "ok", "app": APP_NAME, "ml_model_loaded": models_available()}


# ---- static frontend -------------------------------------------------
if (FRONTEND_DIR / "index.html").exists():
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

    PAGES = {"shop", "cart", "checkout", "login", "register", "reset", "admin", "orders", "profile", "wishlist"}

    @app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
    def index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    @app.api_route("/{page}", methods=["GET", "HEAD"], include_in_schema=False)
    def page(page: str):
        if page.startswith("api"):
            return JSONResponse(status_code=404, content={"detail": "Unknown endpoint."})
        name = page[:-5] if page.endswith(".html") else page
        if name in PAGES:
            return FileResponse(str(FRONTEND_DIR / f"{name}.html"))
        candidate = (FRONTEND_DIR / page).resolve()
        if candidate.is_file() and str(candidate).startswith(str(FRONTEND_DIR.resolve())):
            return FileResponse(str(candidate))
        return FileResponse(str(FRONTEND_DIR / "index.html"))
