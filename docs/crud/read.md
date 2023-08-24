
Records are get by sending a `GET` request to the mount path of the SQLAlchemyCRUD app, you can use any of the filter operators.

### Filtering
SQLAlchemy API supports filtering records by any column. You can use the following query parameters to filter records by different operators:

Operator| Expression | Supported types 
------------ | ------------- | ------------ 
`Equal` | `<column>__op=equal` | All 
`Not equal` | `<column>__op=ne` | All 
`Is Null` | `<column>__op=is_null` | All 
`Is Not Null` | `<column>__op=is_not_null` | All 
`Greater than` | `<column>__op=gt` | Numeric, Date 
`Greater than or equal` | `<column>__op=ge` | Numeric, Date 
`Less than` | `<column>__op=lt` | Numeric, Date 
`Less than or equal` | `<column>__op=le` | Numeric, Date 
`Contains` | `<column>__op=contains` | String 
`Starts with` | `<column>__op=startswith` | String 
`Ends with` | `<column>__op=endswith` | String 

!!! note
    If no filter operator is provided, the default operator is `equal`.


### Pagination

All the data retrieved from the database is paginated, you can use the following query parameters to control the pagination:

query parameter | description | default value
------------ | ------------- | ------------
`page` | The page number to retrieve | 1
`page_size` | The number of records per page | 100

### Response

The response will be a `json` with the following structure:

```python
{   
    "total": 1,
    "page": 1,
    "records": [{}],
}
```

Where: 

- `total`: number of records for this query in the database.
- `page`: current page number.
- `records`: is a list of objects with the records.


### Examples

For the example we will assume the SQLAlchemyAPI CRUD is mounted in `http://localhost:8000/user/` using the following SQLAlchemy model definition.

```python
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    age = Column(Integer, nullable=False)
    date_of_birth = Column(Date)
    address = Column(String(100))
```


#### Filters
Get all records with age greater than 18

```bash
curl -X 'GET' \
    'http://localhost:8000/user/?age__op=gt&age=18'  \
    -H 'accept: application/json'
```

Get all record with date of birth after 2000
```bash
curl -X 'GET' \
    'http://localhost:8000/user/?date_of_birth__op=gt&date_of_birth=2000-01-01'\
    -H 'accept: application/json' 
```

Get all record with name containing "John"
```bash
curl -X 'GET' \
    'http://localhost:8000/user/?name__op=contains&name=John'\
    -H 'accept: application/json' 
```

Get all record with address starting with "Street"
```bash
curl -X 'GET' \
    'http://localhost:8000/user/?address__op=startswith&address=Street'\
    -H 'accept: application/json' 
```

Get all record with address null
```bash
curl -X 'GET' \
    'http://localhost:8000/user/?address__op=is_null'\
    -H 'accept: application/json' 
```

#### Pagination

Get the second page of records with 10 records per page
```bash
curl -X 'GET' \
    'http://localhost:8000/user/?page=2&page_size=10'\
    -H 'accept: application/json' 
```

#### Response

Example of what the response will look like with 3 records:

```json
{
    "total": 3,
    "page": 1,
    "records": [
        {
            "id": 1,
            "name": "John",
            "age": 23,
            "date_of_birth": "2000-01-01",
            "address": "Street 1"
        }
        {
            "id": 2,
            "name": "Pepe",
            "age": 33,
            "date_of_birth": "1990-01-01",
            "address": "Street 2"
        },
        {
            "id": 3,
            "name": "Math",
            "age": 43,
            "date_of_birth": "1980-01-01",
            "address": "Street 3"
        }
    ]
}
```