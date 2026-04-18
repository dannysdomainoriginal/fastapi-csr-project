from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logging_middleware import GoStyleLoggingMiddleware
from contextlib import asynccontextmanager

from app.routers import blog
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
app.add_middleware(GoStyleLoggingMiddleware)

# ---------------------------------------------------------------------------- #
#                                 MOUNT ROUTERS                                #
# ---------------------------------------------------------------------------- #
app.include_router(prefix="/blog", router=blog.router)
