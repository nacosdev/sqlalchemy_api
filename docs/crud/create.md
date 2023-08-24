For the example we will use the following SQLAlchemy model definition.

```python
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    age = Column(Integer, nullable=False)
    date_of_birth = Column(Date)
    address = Column(String(100))
```


Records are created by sending a `POST` request with a `json` in the payload using the name of the columns as keys, example values:
```json
{
    "name": "John",
    "age": 18,
    "date_of_birth": "2000-01-01",
    "address": "Street 1"
}
```
Example request:

```bash
curl -X 'POST' \
  'http://<hostname>/<mount_path>/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "John",
    "age": 18,
    "date_of_birth": "2000-01-01",
    "address": "Street 1"
}'
```
This request will return the created record in `json` format, example response:
```json
{
    "id": 1,
    "name": "John",
    "age": 18,
    "date_of_birth": "2000-01-01",
    "address": "Street 1"
}
```
