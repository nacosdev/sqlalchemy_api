

## APICrud


### Basic example
Let's create a simple SQLAlchemy model:

```Python hl_lines="3-5 7-11 13-16 18"
from starlette.routing import Mount
from starlette.applications import Starlette
from sqlalchemy_api.adapters.starlette_crud import APICrud
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

routes = [
    Mount(
        path="/user",
        app=APICrud(model=User, engine=engine),
    ),
]

app = Starlette(routes=routes)
```

The created APICrud is an instance of Starlette, so you can mount it as a sub-application in your main Starlette app.


```Python hl_lines="1-2 20-25 27"
from starlette.routing import Mount
from starlette.applications import Starlette
from sqlalchemy_api.adapters.starlette_crud import APICrud
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

routes = [
    Mount(
        path="/user",
        app=APICrud(model=User, engine=engine),
    ),
]

app = Starlette(routes=routes)
```

If you are running this app without a previos Starlette instalation, you will also need an ASGI server and Starlette to be able to run this app, both are optional dependencies of SQLAlchemy API:

```bash
pip install sqlalchemy-api[asgi]
```

### Run it

```bash
uvicorn main:app --reload
```

All the [CRUD](/sqlalchemy_api/crud/introduction) endpoints are now available at [http://localhost:8000/user/](http://localhost:8000/user/):



### Use it

Endpoints are automatically generated for the defined model, you can use the following endpoints to interact with them:

- Create: `POST localhost:8000/user`
```bash
curl -X 'POST' \
  'http://localhost:8000/user/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "foo"
}'
```
- Get Many: `GET localhost:8000/user`
```bash
curl -X 'GET' \
  'http://localhost:8000/user/?page_size=100&page=1' \
  -H 'accept: application/json'
```
- Get One: `GET localhost:8000/user/{id}`
```bash
curl -X 'GET' \
  'http://localhost:8000/user/1' \
  -H 'accept: application/json'
```
- Update: `PUT localhost:8000/user/{id}`
```bash
curl -X 'PUT' \
  'http://localhost:8000/user/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "bar"
}'
```
- Delete: `DELETE localhost:8000/user/{id}`
```bash
curl -X 'DELETE' \
  'http://localhost:8000/user/1' \
  -H 'accept: application/json'
```