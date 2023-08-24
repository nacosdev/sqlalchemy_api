Delete a record by sending a `DELETE` request with the primary key as part of the path. 


### Example

```bash
curl -X 'DELETE' \
  'http://localhost:8000/user/1' \
  -H 'accept: application/json'
```

The response will be the deleted record id, example response:
```json
{
    "id": 1
}
```
