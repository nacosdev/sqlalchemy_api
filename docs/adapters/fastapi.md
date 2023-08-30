### Fastapi APICrud 
`APICrud` from the FastAPI adapter will allow you to send any key word arguments that you can send to a FastAPI router, you can also import `FastAPIConfig` and `FastAPIEndpointConfig` to have a better autocompletion and documentation of the parameters you can send.
<p align="center">
  <a><img src="/sqlalchemy_api/assets/images/fastapi_adapter/autocompletion2.png" alt="autocompletion 2"></a>
</p>

### API Reference

`APICrud` from FastAPI will support all the [parameters that a base APICrud supports](/sqlalchemy_api/crud/introduction/#api-reference), plus the following ones:

Parameter | Type | Description | Default
--- | --- | --- | ---
fastapi_config | `dict | FastAPIConfig` | The fastapi extra config for each endpoint | optional

### Simple example
In this example we will:

- Create a file `main.py` with SQLAlchemy models
- Create an APICrud for the model, using the FastAPI adapter with a basic extra config
- Create a FastAPI app
- Include the APICrud in the app


#### Create it
```python 
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy_api.adapters.fastapi_crud import APICrud, FastAPIConfig, FastAPIEndpointConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_engine(
    "sqlite:///example.db",
    connect_args={"check_same_thread": False},
)

def unauthorized():
    raise HTTPException(status_code=401, detail="Unauthorized")

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

Base.metadata.create_all(engine)  # Create tables

user_crud_router = APICrud(
    User, 
    engine,
    fastapi_config=FastAPIConfig(
        all=FastAPIEndpointConfig( # This config will be applied to all endpoints
            tags=["Custom Tag"],
        ),
        post=FastAPIEndpointConfig( # This config will be applied to the CREATE endpoint
            dependencies=[Depends(unauthorized)]
    ))
)

app = FastAPI()
app.include_router(user_crud_router, prefix="/user", tags=["User"])
```
!!! info
    FastAPI adapter is an instance of [FastAPI APIRouter](https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter), so you can include it in your app as any other FastAPI router.

If you are running this app without a previos FastAPI instalation, you will also need an ASGI server and FastAPI to be able to run this app, both are optional dependencies of SQLAlchemy API:

```bash
pip install sqlalchemy-api[fastapi]
```

#### Run it

```bash
uvicorn main:app --reload
```

#### Use it

All the [CRUD](/sqlalchemy_api/crud/introduction) endpoints are now available at [http://localhost:8000/user](http://localhost:8000/user) and the OpenAPI documentation at [http://localhost:8000/docs](http://localhost:8000/docs):






