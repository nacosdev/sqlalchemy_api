from fastapi import Request, Path, Depends, Query, Response
from fastapi.routing import APIRouter, BaseRoute
from sqlalchemy_api.crud import CRUDHandler, GenericResponse
from sqlalchemy_api._types import ENGINE_TYPE
from sqlalchemy_api.pydantic_utils import PageSchema
from sqlalchemy_api.actions import Actions, ALL_ACTIONS
from sqlalchemy_api.filtering import Filter
from inspect import Parameter, Signature
from typing import List, Callable


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

    def __init__(
        self,
        model,
        engine: ENGINE_TYPE,
        async_engine: bool = False,
        page_size_default: int = 100,
        page_size_max: int = 1000,
        debug: bool = False,
        actions: List[Actions] = ALL_ACTIONS,
    ):
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

        async def get(request: Request, row_id: int = Path(...)):
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

        async def delete(request: Request, row_id: int = Path(...)):
            res = await self.crud_handler.delete(row_id=row_id)
            return self.generic_to_fastapi_response(res)

        PutSchema = self.crud_handler.schema_put

        async def put(
            request: Request, schema: PutSchema, row_id: int = Path(...)  # type: ignore
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
            )
        if Actions.GET in self.actions:
            router.add_api_route(
                path="/{row_id}",
                endpoint=get,
                methods=["GET"],
                response_model=self.crud_handler.schema_relations,
            )

        if Actions.CREATE in self.actions:
            router.add_api_route(
                path="",
                endpoint=post,
                methods=["POST"],
                response_model=self.crud_handler.schema_base,
            )

        if Actions.DELETE in self.actions:
            router.add_api_route(
                path="/{row_id}",
                endpoint=delete,
                methods=["DELETE"],
                # response_model=self.crud_handler.pydantic_model
            )

        if Actions.UPDATE in self.actions:
            router.add_api_route(
                path="/{row_id}",
                endpoint=put,
                methods=["PUT"],
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
