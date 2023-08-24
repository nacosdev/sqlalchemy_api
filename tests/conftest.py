from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.applications import Starlette
from starlette.testclient import TestClient as StarletteTestClient
from typing import Generator
from sqlalchemy_api.adapters.starlette_crud import APICrud as StarletteAPICrud
from sqlalchemy_api.adapters.fastapi_crud import APICrud as FastAPIAPICrud
from tests.database.session import User, engine, TestSession, Base, Post
import pytest

# Define two applications, one with Starlette and one with FastAPI
starlette_app = Starlette()

starlette_app.mount(
    "/user",
    StarletteAPICrud(model=User, engine=engine),
)
starlette_app.mount(
    "/post",
    StarletteAPICrud(model=Post, engine=engine),
)

fastapi_app = FastAPI()
fastapi_app.include_router(FastAPIAPICrud(User, engine), prefix="/user")
fastapi_app.include_router(FastAPIAPICrud(Post, engine), prefix="/post")


@pytest.fixture(
    scope="module",
    params=[
        pytest.param((starlette_app, StarletteTestClient), id="Starlette"),
        pytest.param((fastapi_app, TestClient), id="FastAPI"),
    ],
)
def client(request) -> Generator:
    test_client = request.param[1]
    test_app = request.param[0]
    with test_client(test_app) as c:
        yield c


@pytest.fixture(scope="function")
def db_session() -> Generator:  # pragma: no cover
    Base.metadata.create_all(engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
