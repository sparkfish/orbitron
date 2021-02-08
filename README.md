# Orbitron - A python-based "find near me" microservice

## Usage

To perform a search, use the `/nearest/{limit}/{SourceType}/to/{ZipCode}` i.e.: `/nearest/100/pharmacies/to/75001`.  This will perform a search against stored geodata using functionality exposed by PostGIS.

## Example
```javascript
{
        "name": "Mom & Pop's Local Pharmacy",
        "latitude": 33.435921,
        "longitude": -111.720686,
        "rowdata": "{\"phone\": \"555-555-5555\", \"address\": \"123 Any St.\", \"city\": \"PHOENIX\", \"state\": \"AZ\", \"zip\": \"85004\"}"
}
```

Types of contents of "rowdata" field may vary depending on the data source type, i.e. if the entity were a national monument, it might not make sense to include a phone number as shown in the above example, but might be helpful to include a construction date.



## Running

Ensure you have Python>=3.8 on your path and do `pip install -r requirements.txt`. To start a development server, do `uvicorn main:app --reload`.

See [http://localhost:8000/docs](http://localhost:8000/docs) for auto-generated Swagger API documentation.
