from sqlalchemy_api.crud import CRUDHandler
from tests.database.session import User, engine
from sqlalchemy.orm import Session
from unittest.mock import patch
import json
import pytest


class TestCRUDHandler:
    @pytest.mark.asyncio
    async def test_debug_mode_disabled(self, db_session: Session):
        crud = CRUDHandler(
            model=User,
            engine=engine,
        )
        assert crud.debug is False
        with patch("sqlalchemy_api.crud.CRUDHandler.paginate", new=lambda: 1 / 0):
            res = await crud.get_many(query_params={})
            assert res.status_code == 500
            assert json.loads(res.content) == {"detail": "Internal server error"}

    @pytest.mark.asyncio
    async def test_debug_mode_enabled(self, db_session: Session):
        crud = CRUDHandler(model=User, engine=engine, debug=True)
        assert crud.debug is True
        with patch("sqlalchemy_api.crud.CRUDHandler.paginate", new=lambda: 1 / 0):
            res = await crud.get_many(query_params={})
            assert res.status_code == 500
            assert isinstance(json.loads(res.content), list)
