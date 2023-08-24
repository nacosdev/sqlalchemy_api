from tests.database.session import Base, User, engine, TestSession
from sqlalchemy import insert
from fastapi.encoders import jsonable_encoder
from datetime import date, datetime, timedelta
from tests.utils import datetostr, strtodate, datetimetostr, strtodatetime

PREFIX = "/user"
example_user = {
    "name": "John",
    "active": True,
    "birthday": date(1990, 1, 1),
    "created_at": datetime.now(),
    "updated_at": datetime.now(),
    "age": 30,
    "status": "active",
}
json_example_user = jsonable_encoder(example_user)


class TestNullOperators:
    def setup_method(self):
        Base.metadata.create_all(engine)
        # Create testing users
        null_age_user = {**example_user.copy(), "age": None, "name": "null_age_user"}
        not_null_age_user = {
            **example_user.copy(),
            "age": 30,
            "name": "not_null_age_user",
        }
        with TestSession() as db_session:
            db_session.execute(insert(User), [null_age_user, not_null_age_user])
            db_session.commit()

    def teardown_method(self):
        Base.metadata.drop_all(engine)

    def test_is_null_operator(self, client):
        response = client.get(f"{PREFIX}", params={"age__op": "is_null"})
        assert response.status_code == 200
        assert response.json().get("total") == 1
        assert response.json().get("records")[0].get("name") == "null_age_user"
        assert response.json().get("records")[0].get("age") is None

    def test_is_not_null_operator(self, client):
        response = client.get(f"{PREFIX}", params={"age__op": "is_not_null"})
        assert response.status_code == 200
        assert response.json().get("total") == 1
        assert response.json().get("records")[0].get("name") == "not_null_age_user"
        assert response.json().get("records")[0].get("age") == 30


class TestIntegerOperators:
    def setup_method(self):
        Base.metadata.create_all(engine)

        # Create testing users
        with TestSession() as db_session:
            for x in range(30):
                new_user = example_user.copy()
                new_user["age"] = x
                db_session.execute(insert(User).values(new_user))

            db_session.commit()

    def teardown_method(self):
        Base.metadata.drop_all(engine)

    def test_integer_equal_operator(self, client):
        response = client.get(f"{PREFIX}", params={"age": 15, "age__op": "equal"})
        assert response.status_code == 200
        assert response.json().get("total") == 1
        assert response.json().get("records")[0].get("age") == 15

    def test_integer_lt_operator(self, client):
        response = client.get(f"{PREFIX}", params={"age": 15, "age__op": "lt"})
        assert response.status_code == 200
        assert response.json().get("total") == 15
        ages = [item.get("age") for item in response.json().get("records")]
        assert all(age < 15 for age in ages)

    def test_integer_le_operator(self, client):
        response = client.get(f"{PREFIX}", params={"age": 15, "age__op": "le"})
        assert response.status_code == 200
        assert response.json().get("total") == 16
        ages = [item.get("age") for item in response.json().get("records")]
        assert all(age <= 15 for age in ages)

    def test_integer_gt_operator(self, client):
        response = client.get(f"{PREFIX}", params={"age": 15, "age__op": "gt"})
        assert response.status_code == 200
        assert response.json().get("total") == 14
        ages = [item.get("age") for item in response.json().get("records")]
        assert all(age > 15 for age in ages)

    def test_integer_ge_operator(self, client):
        response = client.get(f"{PREFIX}", params={"age": 15, "age__op": "ge"})
        assert response.status_code == 200
        assert response.json().get("total") == 15
        ages = [item.get("age") for item in response.json().get("records")]
        assert all(age >= 15 for age in ages)

    def test_integer_ne_operator(self, client):
        response = client.get(f"{PREFIX}", params={"age": 15, "age__op": "ne"})
        assert response.status_code == 200
        assert response.json().get("total") == 29
        ages = [item.get("age") for item in response.json().get("records")]
        assert all(age != 15 for age in ages)


class TestDateOperators:
    def setup_method(self):
        Base.metadata.create_all(engine)
        # create test users

        with TestSession() as db_session:
            start_date = date(1990, 1, 1)
            end_date = date(1990, 1, 30)
            while start_date <= end_date:
                new_user = example_user.copy()
                new_user["birthday"] = start_date
                db_session.execute(insert(User).values(new_user))
                start_date += timedelta(days=1)
            db_session.commit()

    def teardown_method(self):
        Base.metadata.drop_all(engine)

    def test_date_equal_operator(self, client):
        response = client.get(
            f"{PREFIX}", params={"birthday": datetostr(date(1990, 1, 1))}
        )
        assert response.status_code == 200
        assert response.json().get("total") == 1
        assert response.json().get("records")[0].get("birthday") == datetostr(
            date(1990, 1, 1)
        )

    def test_date_lt_operator(self, client):
        response = client.get(
            f"{PREFIX}",
            params={"birthday": datetostr(date(1990, 1, 15)), "birthday__op": "lt"},
        )
        assert response.status_code == 200
        assert response.json().get("total") == 14
        birthdays = [item.get("birthday") for item in response.json().get("records")]
        assert all([strtodate(birthday) < date(1990, 1, 15) for birthday in birthdays])

    def test_date_le_operator(self, client):
        response = client.get(
            f"{PREFIX}",
            params={"birthday": datetostr(date(1990, 1, 15)), "birthday__op": "le"},
        )
        assert response.status_code == 200
        assert response.json().get("total") == 15
        birthdays = [item.get("birthday") for item in response.json().get("records")]
        assert all([strtodate(birthday) <= date(1990, 1, 15) for birthday in birthdays])

    def test_date_gt_operator(self, client):
        response = client.get(
            f"{PREFIX}",
            params={"birthday": datetostr(date(1990, 1, 15)), "birthday__op": "gt"},
        )
        assert response.status_code == 200
        assert response.json().get("total") == 15
        birthdays = [item.get("birthday") for item in response.json().get("records")]
        assert all([strtodate(birthday) >= date(1990, 1, 15) for birthday in birthdays])

    def test_date_ge_operator(self, client):
        response = client.get(
            f"{PREFIX}",
            params={"birthday": datetostr(date(1990, 1, 15)), "birthday__op": "ge"},
        )
        assert response.status_code == 200
        assert response.json().get("total") == 16
        birthdays = [item.get("birthday") for item in response.json().get("records")]
        assert all([strtodate(birthday) >= date(1990, 1, 15) for birthday in birthdays])

    def test_date_ne_operator(self, client):
        response = client.get(
            f"{PREFIX}",
            params={"birthday": datetostr(date(1990, 1, 15)), "birthday__op": "ne"},
        )
        assert response.status_code == 200
        assert response.json().get("total") == 29
        birthdays = [item.get("birthday") for item in response.json().get("records")]
        assert all([strtodate(birthday) != date(1990, 1, 15) for birthday in birthdays])


class TestDatetimeOperators:
    def setup_method(self):
        Base.metadata.create_all(engine)
        # create test users
        with TestSession() as db_session:
            start_date = datetime.now()
            self.first_date = start_date
            end_date = start_date + timedelta(days=31)
            while start_date < end_date:
                new_user = example_user.copy()
                new_user["created_at"] = start_date
                db_session.execute(insert(User).values(new_user))
                start_date += timedelta(days=1)
            db_session.commit()

    def teardown_method(self):
        Base.metadata.drop_all(engine)

    def test_datetime_equal_operator(self, client):
        start_date = self.first_date
        response = client.get(
            f"{PREFIX}",
            params={"created_at": datetimetostr(start_date), "created_at__op": "equal"},
        )
        assert response.status_code == 200
        assert response.json().get("total") == 1
        created_ats = [
            item.get("created_at") for item in response.json().get("records")
        ]
        assert all(
            [strtodatetime(created_at) == start_date for created_at in created_ats]
        )

    def test_datetime_lt_operator(self, client):
        start_date = self.first_date

        response = client.get(
            f"{PREFIX}",
            params={
                "created_at": datetimetostr(start_date + timedelta(days=15)),
                "created_at__op": "lt",
            },
        )

        assert response.status_code == 200
        assert response.json().get("total") == 15
        created_ats = [
            item.get("created_at") for item in response.json().get("records")
        ]
        assert all(
            [
                strtodatetime(created_at) < start_date + timedelta(days=15)
                for created_at in created_ats
            ]
        )

    def test_datetime_le_operator(self, client):
        start_date = self.first_date

        response = client.get(
            f"{PREFIX}",
            params={
                "created_at": datetimetostr(start_date + timedelta(days=15)),
                "created_at__op": "le",
            },
        )

        assert response.status_code == 200
        assert response.json().get("total") == 16
        created_ats = [
            item.get("created_at") for item in response.json().get("records")
        ]
        assert all(
            [
                strtodatetime(created_at) <= start_date + timedelta(days=15)
                for created_at in created_ats
            ]
        )

    def test_datetime_gt_operator(self, client):
        start_date = self.first_date
        response = client.get(
            f"{PREFIX}",
            params={
                "created_at": datetimetostr(start_date + timedelta(days=15)),
                "created_at__op": "gt",
            },
        )
        assert response.status_code == 200
        assert response.json().get("total") == 15
        created_ats = [
            item.get("created_at") for item in response.json().get("records")
        ]
        assert all(
            [
                strtodatetime(created_at) > start_date + timedelta(days=15)
                for created_at in created_ats
            ]
        )

    def test_datetime_ge_operator(self, client):
        start_date = self.first_date
        response = client.get(
            f"{PREFIX}",
            params={
                "created_at": datetimetostr(start_date + timedelta(days=15)),
                "created_at__op": "ge",
            },
        )
        assert response.status_code == 200
        assert response.json().get("total") == 16
        created_ats = [
            item.get("created_at") for item in response.json().get("records")
        ]
        assert all(
            [
                strtodatetime(created_at) >= start_date + timedelta(days=15)
                for created_at in created_ats
            ]
        )

    def test_datetime_ne_operator(self, client):
        start_date = self.first_date
        response = client.get(
            f"{PREFIX}",
            params={
                "created_at": datetimetostr(start_date + timedelta(days=15)),
                "created_at__op": "ne",
            },
        )
        assert response.status_code == 200
        assert response.json().get("total") == 30
        created_ats = [
            item.get("created_at") for item in response.json().get("records")
        ]
        assert all(
            [
                strtodatetime(created_at) != start_date + timedelta(days=15)
                for created_at in created_ats
            ]
        )


class TestStringOperators:
    def setup_method(self):
        Base.metadata.create_all(engine)
        # create test users
        with TestSession() as db_session:
            for name in ["John", "Noha", "Oliver", "Isabella"]:
                new_user = example_user.copy()
                new_user["name"] = name
                db_session.execute(insert(User).values(new_user))
            db_session.commit()

    def teardown_method(self):
        Base.metadata.drop_all(engine)

    def test_string_equal_operator(self, client):
        response = client.get(f"{PREFIX}", params={"name": "John", "name__op": "equal"})
        assert response.status_code == 200
        assert response.json().get("total") == 1
        assert response.json().get("records")[0].get("name") == "John"

    def test_string_contains_operator(self, client):
        response = client.get(
            f"{PREFIX}", params={"name": "oh", "name__op": "contains"}
        )
        assert response.status_code == 200
        assert response.json().get("total") == 2, "should return 2 users: John and Noha"
        names = [item.get("name") for item in response.json().get("records")]
        assert "John" in names
        assert "Noha" in names

    def test_string_startswith_operator(self, client):
        response = client.get(
            f"{PREFIX}", params={"name": "Isa", "name__op": "startswith"}
        )
        assert response.status_code == 200
        assert response.json().get("total") == 1, "should return 1 user: Isabella"
        assert response.json().get("records")[0].get("name") == "Isabella"

    def test_string_endswith_operator(self, client):
        response = client.get(
            f"{PREFIX}", params={"name": "ver", "name__op": "endswith"}
        )
        assert response.status_code == 200
        assert response.json().get("total") == 1, "should return 1 user: Oliver"
        assert response.json().get("records")[0].get("name") == "Oliver"


class TestInvalidOperator:
    def setup_method(self):
        Base.metadata.create_all(engine)

    def teardown_method(self):
        Base.metadata.drop_all(engine)

    def test_invalid_operator(self, client):
        response = client.get(
            f"{PREFIX}", params={"name": "John", "name__op": "invalid"}
        )
        assert response.status_code == 422
