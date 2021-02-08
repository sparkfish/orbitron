import logging
log = logging.getLogger("fastapi")

import sys

from os import getenv
from dotenv import load_dotenv
load_dotenv()

import psycopg2
import psycopg2.extras as extras
import datetime

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
        return f"host={self.host} user={self.user} dbname={self.database} password={self.password} sslmode=require"


    def connect(self):
        self.connection = psycopg2.connect(
            self.connection_string,
            cursor_factory=extras.RealDictCursor
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

    def execute_batch_zipgeodata_insert(self, dataframe, page_size=150):    
        nump = dataframe.to_numpy()

        tpls = [tuple(x) for x in nump]
    
        sql = """
        INSERT INTO Orbitron.PostalCodeGeodata
        (PostalCode,Latitude,Longitude) 
        VALUES(%s,%s,%s)"""
        cursor = self.connection.cursor()
        try:
            extras.execute_batch(cursor, sql, tpls, page_size)
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as err:
            self.show_psycopg2_exception(err)
            cursor.close()

    def execute_batch_neighborlocation_insert(self, dataframe, page_size=150):
        nump = dataframe.to_numpy()

        tpls = [tuple(x) for x in nump]

        sql = """
        INSERT INTO Orbitron.NeighborLocations
        (SourceId, Name, Latitude, Longitude, RowData) 
        VALUES(%s,%s,%s,%s,%s)"""
        cursor = self.connection.cursor()
        try:
            extras.execute_batch(cursor, sql, tpls, page_size)
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as err:
            self.show_psycopg2_exception(err)
            cursor.close()

    def disconnect(self):
        if self.connection:
            self.connection.close()


    def setup_tables(self):
        SQL = """
        DROP SCHEMA IF EXISTS Orbitron CASCADE;

        CREATE SCHEMA Orbitron;

        DROP TABLE IF EXISTS PostalCodeGeodata;
        DROP TABLE IF EXISTS NeighborLocations;
        DROP TABLE IF EXISTS Sources;

        CREATE TABLE Orbitron.PostalCodeGeodata (
            PostalCode varchar(20) NOT NULL,
            Latitude Decimal(8,6) NOT NULL,
            Longitude Decimal(9,6) NOT NULL
        );
		
        CREATE TABLE Orbitron.Sources
        (
            Id SERIAL PRIMARY KEY,
            Name VARCHAR NOT NULL,
            UpdateUrl VARCHAR,
            UpdateDate DATE NOT NULL
        );

        CREATE TABLE Orbitron.NeighborLocations
        (
            Id SERIAL PRIMARY KEY,
            SourceId INTEGER NOT NULL,
            Name VARCHAR NOT NULL,
            Latitude DECIMAL(8,6) NOT NULL,
            Longitude DECIMAL(9,6) NOT NULL,
            RowData VARCHAR,
			CONSTRAINT fk_NeighborLocations_Sources
                FOREIGN KEY(SourceId) 
	                REFERENCES Orbitron.Sources(Id)
        );

        """

        return self.execute(SQL)

    def setup_postalcode_geometry(self):
        SQL = """
		
            SELECT AddGeometryColumn ('orbitron','postalcodegeodata','Geometry',32611,'POINT',2); -- utm11_meters,
            
            UPDATE Orbitron.PostalCodeGeodata SET "Geometry" = ST_Transform(ST_Centroid(ST_PointFromText('POINT(' || Longitude || ' ' || Latitude || ')', 4326)),32611);
            
            CREATE INDEX idx_PostalCodeGeodata_Geometry ON Orbitron.PostalCodeGeodata USING gist("Geometry");
            
        """
        return self.execute(SQL)

    def setup_neighbor_geometry(self):
        SQL = """
            ALTER TABLE Orbitron.NeighborLocations DROP COLUMN IF EXISTS "Geometry";
            SELECT AddGeometryColumn ('orbitron','neighborlocations','Geometry',32611,'POINT',2); -- utm11_meters,
 
            UPDATE Orbitron.NeighborLocations SET "Geometry" = ST_Transform(ST_Centroid(ST_PointFromText('POINT(' || Longitude || ' ' || Latitude || ')', 4326)),32611);
			
            CREATE INDEX idx_NeighborLocations_Geometry ON Orbitron.NeighborLocations USING gist("Geometry");
    
        """   
        return self.execute(SQL)

    def insert_source(self, sourceName):
        SQL = """
            INSERT INTO Orbitron.Sources(Name, UpdateDate) VALUES (%(name)s, %(updateDate)s) RETURNING Id
        """
        result = self.execute(SQL, {'name': sourceName, 'updateDate': datetime.datetime.today()})
        id = result.fetchone()["id"]
        return id

    def get_neighbors_by_zip(self, count: int, sourceType: str, postalCode: str, distanceLimitInMiles: int):
        # ST_Distance isn't index-aware, so use index-aware ST_DWithin with a distanceLimit 
        #  to prune the amount of data to sort
        distanceLimit = self.metersPerMile * distanceLimitInMiles

        SQL = """
            SELECT loc.Name, loc.Latitude, loc.Longitude, loc.RowData
            FROM Orbitron.NeighborLocations AS loc
            JOIN Orbitron.PostalCodeGeodata AS zip ON ST_DWithin(loc."Geometry", zip."Geometry", %(distanceLimit)s)
            JOIN Orbitron.Sources AS src ON loc.SourceId = src.Id 
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


    def show_psycopg2_exception(self, err):
        # get details about the exception
        err_type, err_obj, traceback = sys.exc_info()    
        # get the line number when exception occured
        line_n = traceback.tb_lineno    

        log.error(f"psycopg2 ERROR: {err} on line number: {line_n}")
        log.error(f"psycopg2 traceback: {traceback} -- type: {err_type}")
        log.error(f"psycopg2 error object: {err_obj}")

        