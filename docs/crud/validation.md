Validation and serialization of the data is done using [Pydantic v2](https://docs.pydantic.dev/latest/) models. It validates data type, required fields, default values, etc.
When a validation fails, it raises a [ValidationError](https://docs.pydantic.dev/latest/errors/validation_errors/) exception and returns
a `422` (Unprocessable Entity) response with the description in the response in the `detail` key.

### Examples

For a SQLAlchemy model with the following definition

```python
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), default="Carl Sagan")
    age = Column(Integer)
    date_of_birth = Column(Date, nullable=False)
    address = Column(String(100))
```

#### Try to create a new record with invalid field

Request to `POST` method with the following data:
```json
{
    "name": "John",
    "age": "foo",
    "date_of_birth": "2000-01-01",
    "address": "Street 1"
}
```

Will return an error like this:
```json
{
    "detail": [
        {
            "type": "int_parsing",
            "loc": [
                "age"
            ],
            "msg": "Input should be a valid integer, unable to parse string as an integer",
            "input": "foo",
            "url": "https://errors.pydantic.dev/2.0.3/v/int_parsing"
        }
    ]
}
```

#### Try to create a new record with missing required field

Request to `POST` method with the following data:
```json
{
    "name": "John",
    "age": 18,
    "address": "Street 1"
}
```
Will return an error like this:
```json
{
    "detail": [
        {
            "type": "missing",
            "loc": [
                "date_of_birth"
            ],
            "msg": "Field required",
            "input": {
                "name": "John",
                "age": 18,
                "address": "Street 1"
            },
            "url": "https://errors.pydantic.dev/2.0.3/v/missing"
        }
    ]
}
```



