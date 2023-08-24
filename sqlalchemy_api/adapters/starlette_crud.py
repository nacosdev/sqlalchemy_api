from starlette.routing import BaseRoute, Route
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.requests import Request
from sqlalchemy_api._types import ENGINE_TYPE
from sqlalchemy_api.actions import Actions, ALL_ACTIONS
from sqlalchemy_api.crud import CRUDHandler, GenericResponse
from typing import ClassVar, List


class APICrud(Starlette):
    """
    APICrud is a Starlette application that exposes a CRUD endpoints for a SQLAlchemy
    model.

    Params:
    - `model`: SQLAlchemy model
    - `prefix`: prefix for all endpoints
    - `engine`: SQLAlchemy engine
    - `async_engine`: if True, use async engine
    - `page_size_default`: default page size
    - `page_size_max`: max page size
    - `debug`: if True, return stacktrace on error
    - `actions`: list of actions to enable, default is all
    """

    engine: ClassVar[ENGINE_TYPE]
    async_engine: ClassVar[bool]
    crud_handler: CRUDHandler

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
        - `prefix`: prefix for all endpoints
        - `async_engine`: if True, use async engine
        - `page_size_default`: default page size
        - `page_size_max`: max page size
        - `actions`: list of actions to enable, default is all
        """
        self.actions = actions
        self.crud_handler = CRUDHandler(
            model=model,
            engine=engine,
            async_engine=async_engine,
            page_size_default=page_size_default,
            page_size_max=page_size_max,
            debug=debug,
        )
        routes = self.init_routes()
        super().__init__(
            routes=routes,
        )

    def init_routes(self) -> List[BaseRoute]:
        routes: List[BaseRoute] = []

        async def get_many(request: Request) -> Response:
            return self.generic_to_starlette_response(
                await self.crud_handler.get_many(
                    query_params=dict(request.query_params)
                )
            )

        async def get(request: Request) -> Response:
            return self.generic_to_starlette_response(
                await self.crud_handler.get(
                    row_id=request.path_params["row_id"],
                )
            )

        async def post(request: Request) -> Response:
            payload = await request.json()
            return self.generic_to_starlette_response(
                await self.crud_handler.post(
                    payload=payload,
                )
            )

        async def delete(request: Request) -> Response:
            return self.generic_to_starlette_response(
                await self.crud_handler.delete(
                    row_id=request.path_params["row_id"],
                )
            )

        async def put(request: Request) -> Response:
            payload = await request.json()
            return self.generic_to_starlette_response(
                await self.crud_handler.put(
                    row_id=request.path_params["row_id"],
                    payload=payload,
                )
            )

        if Actions.GET_MANY in self.actions:
            routes.append(Route("/", get_many, methods=["GET"]))
        if Actions.GET in self.actions:
            routes.append(Route("/{row_id}", get, methods=["GET"]))
        if Actions.CREATE in self.actions:
            routes.append(Route("/", post, methods=["POST"]))
        if Actions.DELETE in self.actions:
            routes.append(Route("/{row_id}", delete, methods=["DELETE"]))
        if Actions.UPDATE in self.actions:
            routes.append(Route("/{row_id}", put, methods=["PUT"]))
        return routes

    @staticmethod
    def generic_to_starlette_response(generic_response: GenericResponse) -> Response:
        return Response(
            content=generic_response.content,
            status_code=generic_response.status_code,
            media_type=generic_response.media_type,
        )
