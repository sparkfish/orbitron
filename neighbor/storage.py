import logging
log = logging.getLogger("fastapi")

from os import getenv
from dotenv import load_dotenv
load_dotenv()

import psycopg2
from psycopg2.extras import DictCursor


class Storage:

    def __init__(self):
        self.host = getenv("DB_HOST")
        self.user = getenv("DB_USER")
        self.password = getenv("DB_PASSWORD")
        self.database = getenv("DB_DATABASE")
        self.connection = None
        self.metersPerMile = 1609.344


    @property
    def connection_string(self):
        return f"host={self.host} user={self.user} dbname={self.database} password={self.password}"
		#return f"host={self.host} user={self.user} dbname={self.database} password={self.password} sslmode=require"


    def connect(self):
        self.connection = psycopg2.connect(
            self.connection_string,
            cursor_factory=DictCursor
        )
        self.connection.autocommit = True

    def execute(self, script, data=None):
        cursor = self.connection.cursor()
        log.debug(f"Executing:\n{script}")
        if not data:
            cursor.execute(script)
        else:
            cursor.execute(script, data)
        return cursor


    def disconnect(self):
        if self.connection:
            self.connection.close()


    def setup_tables(self):
        SQL = """
        DROP TABLE IF EXISTS PostalCodeGeodata;
        DROP TABLE IF EXISTS NeighborLocations;
        DROP TABLE IF EXISTS Sources;

        CREATE TABLE PostalCodeGeodata (
            CountryCode char(2),
            PostalCode varchar(20),
            PlaceName varchar(180),
            AdminName1 varchar(100),
            AdminCode1 varchar(20),
            AdminName2 varchar(100),
            AdminCode2 varchar(20),
            AdminName3 varchar(100),
            AdminCode3 varchar(20),
            Latitude Decimal(8,6),
            Longitude Decimal(9,6),
            Accuracy integer
        );

        CREATE TABLE NeighborLocations
        (
            Id SERIAL Primary Key,
            SourceId INTEGER NOT NULL,
            Name VARCHAR NOT NULL,
            Latitude DECIMAL(8,6) NOT NULL,
            Longitude DECIMAL(9,6) NOT NULL,
            RowData VARCHAR
        );

        CREATE TABLE Sources
        (
            Id SERIAL PRIMARY KEY,
            Name VARCHAR NOT NULL,
            UpdateUrl VARCHAR,
            UpdateDate DATE NOT NULL
        );


        """
        return self.execute(SQL)
		
    def setup_geometry(self):
        SQL = """
		
            SELECT AddGeometryColumn ('public','PostalCodeGeodata','Geometry',32611,'POINT',2); -- utm11_meters,
            SELECT AddGeometryColumn ('public','NeighborLocations','Geometry',32611,'POINT',2); -- utm11_meters,
 
            UPDATE PostalCodeGeodata SET "Geometry" = ST_Transform(ST_Centroid(ST_PointFromText('POINT(' || Longitude || ' ' || Latitude || ')', 4326)),32611);
            UPDATE NeighborLocations SET "Geometry" = ST_Transform(ST_Centroid(ST_PointFromText('POINT(' || Longitude || ' ' || Latitude || ')', 4326)),32611);
			
            CREATE INDEX idx_PostalCodeGeodata_Geometry ON PostalCodeGeodata USING gist("Geometry");
            CREATE INDEX idx_NeighborLocations_Geometry ON NeighborLocations USING gist("Geometry");
        );
        """
        return self.execute(SQL)


    def get_neighbors_by_zip(self, count, sourceType: str, postalCode: str):
        # ST_Distance isn't index-aware, so use index-aware ST_DWithin with a distanceLimit 
		#  to prune the amount of data to sort
		distanceLimit = self.metersPerMile * 200

        SQL = """
            SELECT loc.Name, loc.Latitude, loc.Longitude, loc.RowData
            FROM NeighborLocations AS loc
            JOIN PostalCodeGeodata AS zip ON ST_DWithin(loc."Geometry", zip."Geometry", %(distanceLimit)s)
            JOIN Sources AS src ON loc.SourceId = src.Id 
            WHERE zip.PostalCode = %(postalCode)s AND src.Name = %(sourceType)s
            ORDER BY ST_Distance(loc."Geometry", zip."Geometry")
            FETCH FIRST %(count)s ROWS ONLY
        """
        args_ = { "count": count, "sourceType": sourceType, "postalCode": postalCode, "distanceLimit" : distanceLimit}

        cur = self.execute(SQL, args_)
        neighbors = cur.fetchall()
        return neighbors



    def __enter__(self):
        return self


    def __exit__(self, exception_type, exception_value, tb):
        self.disconnect()
