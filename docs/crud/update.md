Update a record by sending a `PUT` request with the primary key as part of the path and a `json` in the payload with the name of the columns that you want to update as keys.



### Examples

For the example we will assume the SQLAlchemyAPI CRUD is mounted in `http://localhost:8000/user/` using the following SQLAlchemy model definition.

```python
class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column()
    date_of_birth: Mapped[date] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
```


#### Update

Update a record by using the following payload:

```json
{
    "address": "Street 2"
}
```
Request to update a record with primary key `1`:

```bash
curl -X 'PUT' \
  'http://localhost:8000/user/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "address": "Street 2"
}'
```

The response will be the updated record, example response:
```json
{
    "id": 1,
    "name": "John",
    "age": 18,
    "date_of_birth": "2000-01-01",
    "address": "Street 2"
}
```