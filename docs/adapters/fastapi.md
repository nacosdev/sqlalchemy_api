
### Simple example

- Create a file `main.py` with SQLAlchemy models:

```python hl_lines="3-4 6 8-11 13-16 18"
from fastapi import FastAPI
from sqlalchemy_api.adapters.fastapi_crud import APICrud
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_engine(
    "sqlite:///example.db",
    connect_args={"check_same_thread": False},
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

Base.metadata.create_all(engine)  # Create tables

user_crud_router = APICrud(User, engine)

app = FastAPI()
app.include_router(user_crud_router, prefix="/user", tags=["User"])
```

FastAPI adapter is an instance of APIRouter, so you can include it in your app as any other FastAPI router.

```python hl_lines="1-2 20 22-23"
from fastapi import FastAPI
from sqlalchemy_api.adapters.fastapi_crud import APICrud
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_engine(
    "sqlite:///example.db",
    connect_args={"check_same_thread": False},
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

Base.metadata.create_all(engine)  # Create tables

user_crud_router = APICrud(User, engine)

app = FastAPI()
app.include_router(user_crud_router, prefix="/user", tags=["User"])
```
If you are running this app without a previos FastAPI instalation, you will also need an ASGI server and FastAPI to be able to run this app, both are optional dependencies of SQLAlchemy API:

```bash
pip install sqlalchemy-api[fastapi]
```

- Run the app:

```bash
uvicorn main:app --reload
```


All the [CRUD](/sqlalchemy_api/crud/introduction) endpoints are now available at [http://localhost:8000/user](http://localhost:8000/user) and the OpenAPI documentation at [http://localhost:8000/docs](http://localhost:8000/docs):




