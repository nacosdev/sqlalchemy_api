from sqlalchemy_api._types import ENGINE_TYPE
from sqlalchemy_api.pydantic_utils import (
    PageSchema,
    SchemaModel,
)
from sqlalchemy_api.utils import get_column_python_type
from sqlalchemy_api.exceptions import InvalidOperator, NotFoundException
from sqlalchemy_api.exception_handlers import (
    exception_handlers,
    unhandled_exception_response,
)
from sqlalchemy_api.responses import GenericResponse, RowIDResponse, error_response
from sqlalchemy_api.filtering import (
    Filter,
    OPERATOR_ATTR_MAP,
    NULL_OPERATORS,
    IS_NULL,
)
from sqlalchemy.orm import sessionmaker as sqlsessionmaker, Session, DeclarativeBase
from sqlalchemy.sql.expression import select, delete, update, Executable, Select
from sqlalchemy.inspection import inspect
from sqlalchemy import func
from pydantic import BaseModel, create_model
from typing import Any, List, Type, Dict
import anyio


def crud_route():
    def decorator(func):
        async def wrapper(self, *args, **kwargs) -> GenericResponse:
            try:
                return await func(self, *args, **kwargs)
            except Exception as exc:
                exception_handler = exception_handlers.get(
                    type(exc), unhandled_exception_response
                )
                return exception_handler(exc, self.debug)

        return wrapper

    return decorator


class CRUDHandler:
    sessionmaker: sqlsessionmaker[Session]
    engine: ENGINE_TYPE
    async_engine: bool
    model: Type[DeclarativeBase]
    page_size_default: int
    page_size_max: int
    schema: Type[BaseModel]
    schema_relations: Type[BaseModel]
    schema_paginated: Type[BaseModel]
    schema_post: Type[BaseModel]
    schema_put: Type[BaseModel]
    schema_filters: Type[BaseModel]
    debug: bool

    def __init__(
        self,
        model,
        engine: ENGINE_TYPE,
        async_engine: bool = False,
        page_size_default: int = 100,
        page_size_max: int = 1000,
        debug: bool = False,
    ) -> None:
        self.model = model
        self.engine = engine
        self.async_engine = async_engine
        self.page_size_default = page_size_default
        self.page_size_max = page_size_max
        self.debug = debug
        self.sessionmaker = sqlsessionmaker(
            bind=self.engine, expire_on_commit=False  # type: ignore
        )
        self.primary_key_type = get_column_python_type(
            inspect(self.model).primary_key[0]
        )
        self.primary_key_names = [
            primary_key.key for primary_key in inspect(self.model).primary_key
        ]
        self.primary_key = inspect(self.model).primary_key[0]
        schema_model = SchemaModel(model=self.model)
        self.schema_base = schema_model.base()
        self.schema_with_relations = schema_model.relations()
        self.schema_paginated = schema_model.paginated()
        self.schema_post = schema_model.post()
        self.schema_put = schema_model.put()
        self.schema_relations = schema_model.relations()
        self.schema_filters = self.get_schema_filters()

    async def execute_stmt(self, stmt: Executable, session: Session) -> Any:
        if self.async_engine:
            result = await session.execute(stmt)  # type: ignore
        else:
            result = await anyio.to_thread.run_sync(session.execute, stmt)
        return result

    async def paginate(
        self, page: PageSchema, stmt: Select, session: Session
    ) -> BaseModel:
        total_stmt = select(func.count()).select_from(stmt.subquery())
        stmt = stmt.limit(page.size).offset((page.number - 1) * page.size)
        records = (await self.execute_stmt(stmt, session)).scalars().unique().all()
        total = (await self.execute_stmt(total_stmt, session)).scalar()
        return self.schema_paginated(
            total=total,
            records=records,
            page=page.number,
        )

    @crud_route()
    async def get(self, row_id: Any) -> GenericResponse:
        with self.sessionmaker() as session:
            stmt = select(self.model).where(self.primary_key == row_id)
            res = await self.execute_stmt(stmt, session)
            obj = res.scalar_one_or_none()
            if not obj:
                raise NotFoundException
            response_content = self.schema_with_relations.model_validate(
                obj
            ).model_dump_json()

            return GenericResponse(
                content=response_content,
                status_code=200,
                media_type="application/json",
            )

    @crud_route()
    async def get_many(self, query_params: Dict) -> GenericResponse:
        with self.sessionmaker() as session:
            stmt = select(self.model)
            try:
                stmt = self.apply_filters(stmt, query_params)
            except InvalidOperator as e:
                return error_response(detail=e.errors(), status_code=422)
            page = PageSchema(
                size=int(query_params.get("page_size", self.page_size_default)),
                number=int(query_params.get("page", 1)),
            )
            response_content = await self.paginate(
                page=page,
                stmt=stmt,
                session=session,
            )
            return GenericResponse(
                content=response_content.model_dump_json(),
                status_code=200,
                media_type="application/json",
            )

    @crud_route()
    async def delete(self, row_id: Any) -> GenericResponse:
        with self.sessionmaker() as session:
            stmt = delete(self.model).where(self.primary_key == row_id)
            res = await self.execute_stmt(stmt, session)
            session.commit()
            if res.rowcount == 0:
                raise NotFoundException
            id = self.primary_key_type(row_id)
            return GenericResponse(
                content=RowIDResponse(row_id=id).model_dump_json(),
                status_code=200,
                media_type="application/json",
            )

    @crud_route()
    async def post(self, payload: Dict) -> GenericResponse:
        with self.sessionmaker() as session:
            pydantic_model = self.schema_base
            formatted_payload = self.schema_post(**payload).model_dump()
            new_object = self.model(**formatted_payload)
            session.add(new_object)
            session.commit()
            session.refresh(new_object)
            response_content = pydantic_model.model_validate(
                new_object
            ).model_dump_json()
            return GenericResponse(
                content=response_content,
                status_code=201,
                media_type="application/json",
            )

    @crud_route()
    async def put(self, row_id: Any, payload: Dict) -> GenericResponse:
        with self.sessionmaker() as session:
            formatted_payload = self.schema_put(**payload).model_dump(
                exclude_unset=True
            )
            update_stmt = (
                update(self.model)
                .where(self.primary_key == row_id)
                .values(**formatted_payload)
            )
            res = await self.execute_stmt(update_stmt, session)
            session.commit()
            if res.rowcount == 0:
                raise NotFoundException

            updated_object = (
                await self.execute_stmt(
                    select(self.model).where(self.primary_key == row_id), session
                )
            ).scalar_one()

            response_content = self.schema_base.model_validate(
                updated_object
            ).model_dump_json()

            return GenericResponse(
                content=response_content,
                status_code=200,
                media_type="application/json",
            )

    def get_schema_filters(self) -> Type[BaseModel]:
        filters = self.get_filters()
        filters_schema_fields = {}
        for filter in filters:
            filters_schema_fields[filter.name] = (filter.type, None)
        FiltersSchema = create_model(
            "FiltersSchema", **filters_schema_fields  # type: ignore
        )
        return FiltersSchema

    def get_filters(self) -> List[Filter]:
        filters: List[Filter] = []
        for column in self.model.__table__.columns:
            name = column.name
            python_type = get_column_python_type(column, only_type=True)
            default = column.default
            nullable = column.nullable
            description = column.comment
            column = column
            filters.append(
                Filter(
                    name=name,
                    type_=python_type,
                    default=default,
                    nullable=nullable,
                    description=description,
                    column=column,
                )
            )
        return filters

    def apply_filters(self, stmt: Select, query_params: Dict) -> Select:
        filters = self.get_filters()
        filters_dict = {}
        FiltersSchema = self.schema_filters
        for filter in filters:
            if filter.name in query_params:
                filters_dict[filter.name] = query_params[filter.name]

        # format and validate filters dict, with the help of pydantic schemas
        formatted_filters = FiltersSchema(**filters_dict).model_dump(
            exclude_unset=True, exclude_none=True
        )

        for filter in filters:
            query_operator: str = query_params.get(filter.operator_name, "equal")
            if query_operator in NULL_OPERATORS:
                if query_operator == IS_NULL:
                    stmt = stmt.filter(filter.column.is_(None))
                else:
                    stmt = stmt.filter(filter.column.is_not(None))
                continue

            if query_operator not in filter.operators:
                raise InvalidOperator(
                    query_operator, filter.type, filter.name, filter.operators
                )

            operator = OPERATOR_ATTR_MAP[query_operator]
            if filter.name in formatted_filters:
                operator_applier = getattr(filter.column, operator)
                stmt = stmt.filter(operator_applier(formatted_filters[filter.name]))
        return stmt
