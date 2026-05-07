from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import JSONResponse

from infrastructure.database.metadata import create_db_and_tables
from presentation.exception_handlers import register_exception_handlers
from presentation.limiter import limiter
from presentation.routers.admin.router import admin_router
from presentation.routers.auth.router import auth_router
from presentation.routers.launcher.router import launcher_router
from presentation.routers.user.router import user_router
from presentation.routers.wardrobe.router import wardrobe_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(status_code=429, content={"detail": str(exc.detail), "code": "RateLimitExceeded"})


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # List of origins allowed to make requests
    allow_credentials=True,  # Allow cookies/auth headers in cross-origin requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

register_exception_handlers(app)


@app.get("/health")
async def health():
    return {"status": "operational"}


app.include_router(auth_router, prefix="/v1")
app.include_router(user_router, prefix="/v1")
app.include_router(wardrobe_router, prefix="/v1")
app.include_router(launcher_router, prefix="/v1")
app.include_router(admin_router, prefix="/v1")
