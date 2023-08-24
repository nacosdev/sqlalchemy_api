from typing import Container, Type, List, Optional
from pydantic import BaseModel, create_model, ConfigDict
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm import RelationshipDirection, DeclarativeBase
from sqlalchemy_api.utils import get_column_python_type
from sqlalchemy.sql.elements import NamedColumn
from sqlalchemy.inspection import inspect
from typing_extensions import TypeAlias
import typing as t


class PageSchema(BaseModel):
    size: int
    number: int


class PaginatedSchema(BaseModel):
    total: int
    page: int
    records: t.List[t.Any]


def paginate_schema(schema: TypeAlias) -> t.Type[BaseModel]:
    """
    Paginate a model and return a pydantic schema
    """
    pydantic_model = create_model(
        f"Paginated{schema.__name__}",
        total=(int, ...),
        page=(int, ...),
        records=(t.List[schema], ...),
    )
    return pydantic_model


model_config = ConfigDict(from_attributes=True)


def sqlalchemy_to_pydantic(
    db_model: Type,
    exclude: Optional[Container[str]] = None,
    config: ConfigDict = model_config,
    schema_name: Optional[str] = None,
    include_relations=False,
    exclude_relation_models: Optional[List[Type]] = None,
    all_optional=False,
) -> Type[BaseModel]:
    """
    Convert a SQLAlchemy model to a Pydantic model
    Params:
    - `db_model`: SQLAlchemy model
    - `exclude`: list of columns to exclude
    - `config`: Pydantic config
    - `schema_name`: name of the Pydantic model
    - `include_relations`: if True, include relations
    - `exclude_relation_models`: list of models to exclude from relations
    - `all_optional`: if True, all fields are optional
    """
    if exclude_relation_models is None:
        exclude_relation_models = []
    if exclude is None:
        exclude = []
    mapper = inspect(db_model)
    fields = {}
    if schema_name is None:
        schema_name = db_model.__name__
    for attr in mapper.attrs:
        if isinstance(attr, ColumnProperty):
            if attr.columns:
                name = attr.key
                if name in exclude:
                    continue
                column: NamedColumn = attr.columns[0]
                python_type = get_column_python_type(column)
                if all_optional:
                    default = None
                elif column.nullable:
                    default = None
                else:
                    default = ...
                fields[name] = (python_type, default)

    if include_relations:
        exclude_relation_models.append(db_model)
        for rela in mapper.relationships:
            if rela.entity.entity in exclude_relation_models:  # pragma: no cover
                continue

            child_model = sqlalchemy_to_pydantic(
                rela.entity.entity,
                schema_name=f"{schema_name}{rela.key}",
                exclude_relation_models=exclude_relation_models,
            )
            direction: RelationshipDirection = rela.direction
            if direction == RelationshipDirection.MANYTOONE:
                fields[rela.key] = (Optional[child_model], None)  # type: ignore
            elif direction in [
                RelationshipDirection.ONETOMANY,
                RelationshipDirection.MANYTOMANY,
            ]:
                if not rela.uselist:
                    fields[rela.key] = (Optional[child_model], None)  # type: ignore
                else:
                    fields[rela.key] = (
                        Optional[List[child_model]],  # type: ignore
                        None,
                    )

    pydantic_model = create_model(
        schema_name, __config__=config, **fields  # type: ignore
    )
    return pydantic_model


class SchemaModel:
    model: Type[DeclarativeBase]
    primary_key_names: Optional[List[str]]

    def __init__(self, model: Type[DeclarativeBase]):
        self.model = model
        self.primary_key_names = [
            primary_key.key for primary_key in inspect(self.model).primary_key
        ]

    def base(self) -> Type[BaseModel]:
        return sqlalchemy_to_pydantic(self.model)

    def relations(self) -> Type[BaseModel]:
        return sqlalchemy_to_pydantic(
            self.model,
            schema_name=f"{self.model.__name__}Relations",
            include_relations=True,
        )

    def put(self) -> Type[BaseModel]:
        return sqlalchemy_to_pydantic(
            self.model,
            exclude=self.primary_key_names,
            schema_name=f"{self.model.__name__}Update",
            all_optional=True,
        )

    def post(self) -> Type[BaseModel]:
        return sqlalchemy_to_pydantic(
            self.model,
            exclude=self.primary_key_names,
            schema_name=f"{self.model.__name__}Create",
        )

    def paginated(self) -> Type[BaseModel]:
        paginated_model = paginate_schema(self.relations())
        return paginated_model
