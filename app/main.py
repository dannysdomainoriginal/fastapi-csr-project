import time
import dotenv

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from logging_middleware import GoStyleLoggingMiddleware as LoggingMiddleware

from app.routers import auth, blog, issues
from contextlib import asynccontextmanager
from app.config.database import create_db_and_tables

dotenv.load_dotenv()


# ---------------------------------------------------------------------------- #
#                                PRE START SETUP                               #
# ---------------------------------------------------------------------------- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

# ---------------------------------------------------------------------------- #
#                             APP LEVEL MIDDLEWARES                            #
# ---------------------------------------------------------------------------- #
app.add_middleware(CORSMiddleware)
app.add_middleware(LoggingMiddleware)


# ---------------------------------------------------------------------------- #
#                               CUSTOM MIDDLEWARE                              #
# ---------------------------------------------------------------------------- #
@app.middleware("http")
async def timing_middleware(req: Request, call_next):
    start = time.perf_counter()
    response: Response = await call_next(req)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.4f}s"
    return response


# ---------------------------------------------------------------------------- #
#                                 MOUNT ROUTERS                                #
# ---------------------------------------------------------------------------- #
app.include_router(prefix="/blog", router=blog.router)
app.include_router(prefix="/auth", router=auth.router)
app.include_router(prefix="/issues", router=issues.router)
