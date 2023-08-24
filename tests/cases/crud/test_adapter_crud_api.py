from tests.database.session import User, engine
from sqlalchemy import insert, select, func
from fastapi.encoders import jsonable_encoder
from datetime import date, datetime, timedelta
from tests.utils import datetostr, datetimetostr
from unittest.mock import patch
import pytest

USER_PREFIX = "/user"
POST_PREFIX = "/post"
example_user = {
    "name": "John",
    "active": True,
    "birthday": date(1990, 1, 1),
    "created_at": datetime.strptime(
        "2023-01-01T01:30:33.222222", "%Y-%m-%dT%H:%M:%S.%f"
    ),
    "updated_at": datetime.strptime(
        "2023-01-01T01:35:33.222222", "%Y-%m-%dT%H:%M:%S.%f"
    ),
    "age": 30,
    "status": "active",
}

jsonable_example_user = jsonable_encoder(example_user)


class TestCRUD:
    def test_get_by_id(self, client, db_session):
        # Insert a user
        insert_stmt = insert(User).values(**example_user)
        db_session.execute(insert_stmt)
        db_session.commit()
        inserted_user: User = db_session.execute(select(User)).scalar_one()

        response = client.get(f"{USER_PREFIX}/{inserted_user.id}")
        assert response.status_code == 200
        response_body = response.json()
        assert response_body.get("id") == inserted_user.id
        assert response_body.get("name") == inserted_user.name
        assert response_body.get("active") == inserted_user.active
        assert response_body.get("birthday") == datetostr(inserted_user.birthday)
        assert response_body.get("created_at") == datetimetostr(
            inserted_user.created_at
        )
        assert response_body.get("updated_at") == datetimetostr(
            inserted_user.updated_at
        )
        assert response_body.get("status") == inserted_user.status.value

    def test_get_many(self, client, db_session):
        db_session.execute(insert(User), [example_user, example_user])
        db_session.commit()
        response = client.get(f"{USER_PREFIX}")
        assert response.status_code == 200
        assert response.json().get("total") == 2
        assert response.json().get("records")[0] == {"id": 1, **jsonable_example_user}
        assert response.json().get("records")[1] == {"id": 2, **jsonable_example_user}

    def test_post(self, client, db_session):
        response = client.post(f"{USER_PREFIX}", json=jsonable_example_user)
        assert response.status_code == 201
        count = db_session.execute(select(func.count(User.id))).scalar()
        assert count == 1
        inserted_user = db_session.execute(select(User)).scalar_one()
        assert response.json().get("id") == inserted_user.id
        assert response.json().get("name") == inserted_user.name
        assert response.json().get("active") == inserted_user.active
        assert response.json().get("birthday") == datetostr(inserted_user.birthday)
        assert response.json().get("created_at") == datetimetostr(
            inserted_user.created_at
        )
        assert response.json().get("updated_at") == datetimetostr(
            inserted_user.updated_at
        )
        assert response.json().get("status") == inserted_user.status.value

    def test_delete(self, client, db_session):
        inserted_id = db_session.execute(
            insert(User).values(**example_user)
        ).inserted_primary_key[0]
        db_session.commit()
        response = client.delete(f"{USER_PREFIX}/{inserted_id}")
        assert response.status_code == 200
        assert response.json() == {"row_id": inserted_id}
        count = db_session.execute(select(func.count(User.id))).scalar()
        assert count == 0

    def test_put(self, client, db_session):
        inserted_id = db_session.execute(
            insert(User).values(**example_user)
        ).inserted_primary_key[0]
        db_session.commit()
        modified_user = jsonable_example_user.copy()
        modified_user["active"] = False
        modified_user["name"] = "Jane"
        modified_user["birthday"] = date(1991, 1, 1)
        modified_user["created_at"] = example_user["created_at"] + timedelta(days=1)
        modified_user["updated_at"] = example_user["updated_at"] + timedelta(days=1)
        modified_user["status"] = "inactive"
        jsonable_modified_user = jsonable_encoder(modified_user)
        response = client.put(
            f"{USER_PREFIX}/{inserted_id}", json=jsonable_modified_user
        )
        assert response.status_code == 200
        assert response.json() == {"id": inserted_id, **jsonable_modified_user}
        user_db = db_session.execute(select(User)).scalar_one()
        assert user_db.id == inserted_id
        assert user_db.name == modified_user["name"]
        assert user_db.active == modified_user["active"]
        assert user_db.birthday == modified_user["birthday"]
        assert user_db.created_at == modified_user["created_at"]
        assert user_db.updated_at == modified_user["updated_at"]
        assert user_db.status.value == modified_user["status"]


class TestCrudExceptions:
    def test_get_by_id_not_found(self, client, db_session):
        response = client.get(f"{USER_PREFIX}/1")
        assert response.status_code == 404
        assert response.json() == {"message": "Not found"}

    def test_delete_not_found(self, client, db_session):
        response = client.delete(f"{USER_PREFIX}/1")
        assert response.status_code == 404
        assert response.json() == {"message": "Not found"}

    def test_put_not_found(self, client, db_session):
        response = client.put(f"{USER_PREFIX}/1", json=jsonable_example_user)
        assert response.status_code == 404
        assert response.json() == {"message": "Not found"}

    @pytest.mark.skipif(
        engine.url.drivername == "sqlite",
        reason="sqlite doesn't validate FK constraints",
    )
    def test_post_to_relation_with_non_existing_relation(self, client, db_session):
        response = client.post(
            f"{POST_PREFIX}", json={"content": "I'm a post", "user_id": 1}
        )
        assert response.status_code == 409
        response_detail = response.json().get("detail")[0]
        assert response_detail.get("exception_type") == "IntegrityError"

    def test_unhandled_exception(self, client, db_session):
        # This test is to ensure that the exception handler is working
        with patch("sqlalchemy_api.crud.CRUDHandler.paginate", new=lambda: 1 / 0):
            response = client.get(f"{USER_PREFIX}")
            assert response.status_code == 500
            assert response.json() == {"detail": "Internal server error"}


class TestCrudValidations:
    def test_post_payload_without_required_field(self, client, db_session):
        response = client.post(f"{USER_PREFIX}", json={"name": "John"})
        assert response.status_code == 422
        response_detail = response.json().get("detail")[0]
        assert response_detail.get("type") == "missing"
        assert "birthday" in response_detail.get("loc")
        assert response_detail.get("msg") == "Field required"

    def test_required_fields_should_be_optional_when_updating(self, client, db_session):
        inserted_id = db_session.execute(
            insert(User).values(**example_user)
        ).inserted_primary_key[0]
        db_session.commit()
        response = client.put(f"{USER_PREFIX}/{inserted_id}", json={"name": "John"})
        assert response.status_code == 200
        assert response.json().get("name") == "John"

    def test_post_payload_with_invalid_format(self, client, db_session):
        response = client.post(
            f"{USER_PREFIX}", json={"name": "John", "birthday": "01/01/1991"}
        )
        assert response.status_code == 422
        response_detail = response.json().get("detail")[0]
        assert "birthday" in response_detail.get("loc")
