from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from logging_middleware import GoStyleLoggingMiddleware as LoggingMiddleware

from app.routers import auth, blog
from app.config.database import create_db_and_tables


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
#                                 MOUNT ROUTERS                                #
# ---------------------------------------------------------------------------- #
app.include_router(prefix="/blog", router=blog.router)
app.include_router(prefix="/auth", router=auth.router)
