## CRUD

SQLAlchemy API will provide the resources to create, read, update and delete your 
SQLAlchemy models, by using starndar API REST endpoints.

### Endpoints

Path | Method | Description
------------ | ------------- | ------------
`/` | `POST`  | Create new record
`/` | `GET`  | Get all records
`/{row_id}` | `GET`  | Get record by primary key
`/{row_id}` | `PUT`  | Update record by primary key
`/{row_id}` | `DELETE`  | Delete record by primary key

### APICrud

Each [adapter](/sqlalchemy_api/adapters/introduction) will provide an `APICrud` class that will be used to mount the CRUD endpoints. The `APICrud` class will receive the SQLAlchemy model and the SQLAlchemy engine as parameters.

```python 
from sqlalchemy_api.adapters.<adapter>_crud import APICrud
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

app = APICrud(User, engine)
```

### API reference

`APICrud` can be configured with the following parameters:
    
```python   
def __init__(
    self,
    model,
    engine: Union[Engine, AsyncEngine],
    async_engine: bool = False,
    page_size_default: int = 100,
    page_size_max: int = 1000,
    debug: bool = False,
)
```

Parameter | Type | Description | Default
--- | --- | --- | ---
model | DeclarativeBase | The SQLAlchemy model to be used | required
engine | Union[Engine, AsyncEngine] | The SQLAlchemy engine to be used | required
async_engine | bool | Whether the engine is async or not | False
page_size_default | int | The default page size to be used | 100
page_size_max | int | The maximum page size that can be used | 1000
debug | bool | Whether to enable debug mode or not* | False

!!! info
    `debug=True` will return the raw unhandled exceptions traceback in the response body. This is useful for debugging, but should not be used in production.