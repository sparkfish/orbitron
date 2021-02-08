# Orbitron - A python-based "find near me" microservice

## Usage

To perform a search, use the `/nearest/{limit}/{SourceType}/to/{ZipCode}` i.e.: `/nearest/100/pharmacies/to/75001`.  This will perform a search against stored geodata using functionality exposed by PostGIS.

## Example
```javascript
{
        "name": "Mom & Pop's Local Pharmacy",
        "latitude": 33.435921,
        "longitude": -111.720686,
        ...
}
```

Additional data fields may be returned depending upon the contents of "rowdata" field in the database.  It may vary depending on the data source type, i.e. if the geopoint represents a store or office, it may be convinient to include a contact phone number, but for something like a national monument, it might be helpful to include a construction date or other historical details of interest.

## Dependencies

This software requires access to a postgresql server with PostGIS 2.5.1 (or compatible version), with credentials set in a configuration file named ".env".  A Sample.env file is included.
Building the postal code geodata also requires the file US.txt from geoname.org's free data at http://download.geonames.org/export/zip/ 

## Installation

Edit the file "Sample.env" to reflect your postgresql credentials, and save the updated file as ".env" in the root folder of the project.
Place US.txt in the root folder and execute `python install.py` to perform initial database setup.

## Configuration of neighbor data

The location data needs to be tied to a sourceType defined in the Orbitron.Sources table.  The "Name" field will correspond to the {sourceType} parameter of the request URL.  The script `load.py` can be used to load the neighbor data, it takes a csv file as a parameter, with columns in the following order:
`[ "SourceId", "Name", "Latitude", "Longitude" ]`

If you do not have the latitude & longitude information for the locations, but do have address information, you can run the addresses through a service such as https://www.geocod.io/ .


## Running

Ensure you have Python>=3.8 on your path and do `pip install -r requirements.txt`. To start a development server, do `uvicorn main:app --reload`.

See [http://localhost:8000/docs](http://localhost:8000/docs) for auto-generated Swagger API documentation.


## Quick start using open pharamacy location data on local development server
1.) Set up a postgresql instance with PostGIS
2.) Perform installation as indicated in "Installation" section of README.
3.) Download rxopen's pharacy location database from https://rxopen.org/api/v1/map/download/facility and place the resulting facility.csv in the project's root folder.
4.) Execute `python import-pharmacies.py`
5.) Run development server, as indicated in "Running" section.
You should now be able to issue http requests using the API endpoints against the local server, such as GET `http://localhost:8000/nearest/100/pharmacies/to/75001`

## Roadmap
- Builtin support for pagination
- administration features for "neighbor" data
- more robust logging options
