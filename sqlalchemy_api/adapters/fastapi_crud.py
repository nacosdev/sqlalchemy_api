from fastapi import Request, Path, Depends, Query, Response
from fastapi.types import IncEx
from fastapi.routing import APIRouter, BaseRoute, APIRoute
from sqlalchemy_api.crud import CRUDHandler, GenericResponse
from sqlalchemy_api._types import ENGINE_TYPE
from sqlalchemy_api.pydantic_utils import PageSchema
from sqlalchemy_api.actions import Actions, ALL_ACTIONS
from sqlalchemy_api.filtering import Filter
from inspect import Parameter, Signature
from fastapi import params
from typing import (
    List,
    Callable,
    TypedDict,
    Any,
    Dict,
    Set,
    Sequence,
    Optional,
    Union,
    Type,
)
from enum import Enum


class FastAPIEndpointConfig(TypedDict):
    response_model: Any
    status_code: Optional[int]
    tags: Optional[List[Union[str, Enum]]]
    dependencies: Optional[Sequence[params.Depends]]
    summary: Optional[str]
    description: Optional[str]
    response_description: str
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]]
    deprecated: Optional[bool]
    methods: Optional[Union[Set[str], List[str]]]
    operation_id: Optional[str]
    response_model_include: Optional[IncEx]
    response_model_exclude: Optional[IncEx]
    response_model_by_alias: bool
    response_model_exclude_unset: bool
    response_model_exclude_defaults: bool
    response_model_exclude_none: bool
    include_in_schema: bool
    name: Optional[str]
    route_class_override: Optional[Type[APIRoute]]
    callbacks: Optional[List[BaseRoute]]
    openapi_extra: Optional[Dict[str, Any]]


class FastAPIConfig(TypedDict):
    all: Optional[FastAPIEndpointConfig]
    get: Optional[FastAPIEndpointConfig]
    get_many: Optional[FastAPIEndpointConfig]
    post: Optional[FastAPIEndpointConfig]
    put: Optional[FastAPIEndpointConfig]
    delete: Optional[FastAPIEndpointConfig]


class APICrud(APIRouter):
    """
    - `model`: SQLAlchemy model
    - `engine`: SQLAlchemy engine
    - `async_engine`: if True, use async engine
    - `page_size_default`: default page size
    - `page_size_max`: max page size
    - `debug`: if True, return stacktrace on error
    - `actions`: list of actions to enable, default is all
    """

    crud_handler: CRUDHandler
    actions: List[Actions]
    fastapi_config: Union[Dict,FastAPIConfig]

    def __init__(
        self,
        model,
        engine: ENGINE_TYPE,
        async_engine: bool = False,
        page_size_default: int = 100,
        page_size_max: int = 1000,
        debug: bool = False,
        actions: List[Actions] = ALL_ACTIONS,
        fastapi_config: Optional[Union[Dict,FastAPIConfig]] = None,
    ):
        self.fastapi_config = fastapi_config or {}
        """
        - `model`: SQLAlchemy model
        - `engine`: SQLAlchemy engine
        - `async_engine`: if True, use async engine
        - `page_size_default`: default page size
        - `page_size_max`: max page size
        - `actions`: list of actions to enable, default is all
        """

        self.crud_handler = CRUDHandler(
            model=model,
            engine=engine,
            async_engine=async_engine,
            page_size_default=page_size_default,
            page_size_max=page_size_max,
            debug=debug,
        )
        self.actions = actions
        routes = self.init_routes()
        super().__init__(routes=routes)

    def init_routes(self) -> List[BaseRoute]:
        router = APIRouter()
        row_id_type = self.crud_handler.primary_key_type

        async def get(
            request: Request, row_id: row_id_type = Path(...)  # type: ignore
        ):
            res = await self.crud_handler.get(row_id=row_id)
            return self.generic_to_fastapi_response(res)

        async def get_many(
            request: Request,
            page: PageSchema = Depends(self.get_page_dependency()),
            filters=Depends(self.get_filters_dependency()),
        ):
            res = await self.crud_handler.get_many(
                query_params=dict(request.query_params)
            )
            return self.generic_to_fastapi_response(res)

        postSchema = self.crud_handler.schema_post

        async def post(request: Request, schema: postSchema):  # type: ignore
            payload = await request.json()
            res = await self.crud_handler.post(payload=payload)
            return self.generic_to_fastapi_response(res)

        async def delete(
            request: Request, row_id: row_id_type = Path(...)  # type: ignore
        ):
            res = await self.crud_handler.delete(row_id=row_id)
            return self.generic_to_fastapi_response(res)

        PutSchema = self.crud_handler.schema_put

        async def put(
            request: Request,
            schema: PutSchema,  # type: ignore
            row_id: row_id_type = Path(...),  # type: ignore
        ):
            payload = await request.json()
            res = await self.crud_handler.put(row_id=row_id, payload=payload)
            return self.generic_to_fastapi_response(res)

        if Actions.GET_MANY in self.actions:
            router.add_api_route(
                path="",
                endpoint=get_many,
                methods=["GET"],
                response_model=self.crud_handler.schema_paginated,
                **self.fastapi_config.get("all", {}),  # type: ignore
                **self.fastapi_config.get("get_many", {}),  # type: ignore
            )
        if Actions.GET in self.actions:
            router.add_api_route(
                path="/{row_id}",
                endpoint=get,
                methods=["GET"],
                response_model=self.crud_handler.schema_relations,
                **self.fastapi_config.get("all", {}),  # type: ignore
                **self.fastapi_config.get("get", {}),  # type: ignore
            )

        if Actions.CREATE in self.actions:
            router.add_api_route(
                path="",
                endpoint=post,
                methods=["POST"],
                response_model=self.crud_handler.schema_base,
                **self.fastapi_config.get("all", {}),  # type: ignore
                **self.fastapi_config.get("post", {}),  # type: ignore
            )

        if Actions.DELETE in self.actions:
            router.add_api_route(
                path="/{row_id}",
                endpoint=delete,
                methods=["DELETE"],
                **self.fastapi_config.get("all", {}),  # type: ignore
                **self.fastapi_config.get("delete", {}),  # type: ignore
            )

        if Actions.UPDATE in self.actions:
            router.add_api_route(
                path="/{row_id}",
                endpoint=put,
                methods=["PUT"],
                **self.fastapi_config.get("all", {}),  # type: ignore
                **self.fastapi_config.get("put", {}),  # type: ignore
                # response_model=self.crud_handler.pydantic_model
            )
        return router.routes

    def get_page_dependency(self) -> Callable:
        default_size = self.crud_handler.page_size_default
        max_size = self.crud_handler.page_size_max

        def page_dependency(
            page_size: int = Query(
                default_size,
                ge=1,
                le=max_size,
                description=f"Number of records per page, max {max_size}",
            ),
            page: int = Query(1, ge=1, description="Page number"),
        ):
            return PageSchema(size=page_size, number=page)

        return page_dependency

    def get_filters_dependency(self):
        filters: List[Filter] = self.crud_handler.get_filters()
        formatted_filters = {}
        for filter in filters:
            formatted_filters[filter.name] = Query(int)

        def filters_dependency(**kwargs):
            ...

        parameters = []
        for filter in filters:
            parameters.append(
                Parameter(
                    name=filter.name,
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=filter.type,
                    default=Query(None, description=filter.description),
                )
            )

        for filter in filters:
            operators = filter.operators
            if operators:
                parameters.append(
                    Parameter(
                        name=filter.operator_name,
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=Query(
                            None,
                            description=f"operators for `{filter.name}`",
                            enum=operators,
                        ),
                    )
                )

        filters_dependency.__signature__ = Signature(parameters=parameters)
        return filters_dependency

    @staticmethod
    def generic_to_fastapi_response(generic_response: GenericResponse) -> Response:
        return Response(
            content=generic_response.content,
            status_code=generic_response.status_code,
            media_type=generic_response.media_type,
        )
