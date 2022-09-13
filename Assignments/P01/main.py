#Author :    Allyson Warren
#Title  :    Project 1- Querying PostgreSQL Database with FastAPI
#Date   :    9/8/2022 
#Description:   
#This program takes csv data about volcanoes and imports the information into a 
# PostgreSQL database with some cleaning and arranging to adjust the structure.
# After importing the data, FastAPI is used to create a localhost API to 
# perform three different types of queries on the data: findAll, findOne, and findClosest.
# find_All shows every volcano and its data to the user. find_One finds a volcano 
# that meets the given specifications defined by the user. This can be the name of 
# a country, a volcano's hazardness, whether it's active, and more. The route will show the 
# user the first volcano that meets the user's specifications. find_Closest takes a given set of 
# latitude and longitude lines and will display the volcano closest to the given coordinates. The
# coordinates are found using the extension PostGIS within PosgreSQL to compare the geometry of
# the given longitude and latitude coordinates with the geometry of each volcano.

import psycopg2
import json
import csv

# Libraries for FastAPI
from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


'#########################################################################################'
'                                  Database Implementation                                '
'#########################################################################################'

def is_integer(n):
    try:
        int(n)
    except ValueError:
        return False
    return True


def is_float(n):
    try:
        float(n)
    except ValueError:
        return False
    return True


class DatabaseCursor(object):
    """https://stackoverflow.com/questions/32812463/setting-schema-for-all-queries-of-a-connection-in-psycopg2-getting-race-conditi
    https://stackoverflow.com/questions/1984325/explaining-pythons-enter-and-exit
    """

    def __init__(self, conn_config_file):
        with open(conn_config_file) as config_file:
            self.conn_config = json.load(config_file)

    def __enter__(self):
        self.conn = psycopg2.connect(
            "dbname='"
            + self.conn_config["dbname"]
            + "' "
            + "user='"
            + self.conn_config["user"]
            + "' "
            + "host='"
            + self.conn_config["host"]
            + "' "
            + "password='"
            + self.conn_config["password"]
            + "' "
            + "port="
            + self.conn_config["port"]
            + " "
        )
        self.cur = self.conn.cursor()
        self.cur.execute("SET search_path TO " + self.conn_config["schema"])

        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        # some logic to commit/rollback
        self.conn.commit()
        self.conn.close()


#create_extension = """CREATE EXTENSION postgis;"""

create_extension = """DROP EXTENSION postgis CASCADE; 
SET search_path to public; 
CREATE EXTENSION postgis;"""

alter_db = """ALTER DATABASE Project01 SET search_path=public;
"""

drop_table = "DROP TABLE  IF EXISTS volcanoes;"

create_table = """CREATE TABLE public.volcanoes (
    id NUMERIC PRIMARY KEY,
    volcanoid NUMERIC NOT NULL,
    name VARCHAR(127) NOT NULL,
    country VARCHAR(64) NOT NULL,
    region VARCHAR(64) NOT NULL,
    subregion VARCHAR(64) NOT NULL,
    latitude DECIMAL(11,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    pei NUMERIC NOT NULL,
    h_active BOOL,
    vei_holoce VARCHAR(32),
    hazard NUMERIC(1),
    classified VARCHAR(32),
    risk NUMERIC(1),
    field_14 varchar(10),
    field_15 varchar(10),
    location GEOMETRY(POINT,4326));"""


load_table = """COPY public.volcanoes(
        volcanoid,name,country,region,subregion,latitude,
        longitude,pei,h_active,vei_holoce,hazard,classified,
        risk,field_14,field_15,location) FROM 'Assignments/P01/volcano.csv';
        """

alter_table = """ALTER TABLE public.volcanoes ADD COLUMN location GEOMETRY(POINT, 4326);
"""

drop_cols = """ALTER TABLE public.volcanoes DROP COLUMN field_14;
ALTER TABLE public.volcanoes DROP COLUMN field_15;"""

# update_location = """UPDATE public.volcanoes
# SET location = ST_SetSRID(ST_MakePoint(longitude,latitude), 4326);"""

# """
# -- select ST_AsEWKT(location,1) from public.volcanoes
# -- WHERE volcanoid = 210010;


'#########################################################################################'
'                                      API INFO                                           '
'#########################################################################################'

description = """## API for Finding Data About Volcanoes Across the World Stored in a PostgreSQL Database.
This API searches a database containing volcanic data and can be used to perform three different
types of queries: find_All, find_One, and find_Closest. find_All shows every volcano and its data to
the user. find_One finds a volcano that meets the given specifications defined by the user. This can be
the name of a country, a volcano's hazardness, whether it's active, and more. The route will show the
user the first volcano that meets the user's specifications. find_Closest takes a given set of 
latitude and longitude lines and will display the volcano closest to the given coordinates. For more
information about volcanoes see: [Global Distribution of Volcanism](https://www.preventionweb.net/english/hyogo/gar/2015/en/bgdocs/risk-section/GVMd.%20Global%20Volcanic%20Hazards%20and%20Risk%20Country%20volcanic%20hazard%20and%20risk%20profiles..pdf)"""

app = FastAPI(
    title="Project 1: Volcano Data API",
    description=description,
    version="0.0.1",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

'#########################################################################################'
'                                       ROUTES                                            '
'#########################################################################################'

@app.get("/")
async def docs_redirect():
    """Api's base route that displays the information created above in the ApiInfo section."""
    return RedirectResponse(url="/docs")


@app.get("/find_All/")
async def findAll():
    """
    ### Description:
        Get all of the volcanoes and their information from the database. 
        Display it all in tuple form.
    ### Params:
        None
    ### Returns:
        list : list containing a tuple for each volcano and its data
    ## Examples:
    [http://127.0.0.1:8080/find_All/](http://127.0.0.1:8080/find_All/)
    ### Results:
    """
    with DatabaseCursor('.config.json') as cur:

        #Get everything from the database
        cur.execute("SELECT * FROM volcanoes;")
        return cur.fetchall()


@app.get("/find_One/")
async def findOne(
    id: int = None, 
    volcanoid: int = None, 
    name: str = None, 
    country: str = None, 
    region: str = None, 
    subregion: str = None, 
    lat: float = None,
    lon: float = None,
    pei: int = None, 
    h_active: bool = None, 
    vei: str = None, 
    hazard: int = None,
    classified: str = Query(None, enum=["U-HR", "U-HHR", "U-NHHR", "Unknown"]), 
    risk: int = None,  
    ):
    """
    ### Description:
        Get a particular volcano's information based on which column to search for.
        The user can narrow their search by searching for particular parts of multiple
        columns. Giving no parameters will return the first volcano in the database.
        Giving a parameter that does not exist within the provided column will return
        a message saying that no volcano exists with the given specifications.

    ### Optional Params:
        id          :   A particular row to get from the database 

        volcanoid   :   The volcano's unique number

        name        :   Name of a particular volcano

        country     :   Which country the volcano resides in

        region      :   What region the volcano is in. Ex: Middle East and Indian Ocean

        subregion   :   What subregion the volcano is at. Ex: Indian Ocean | New Ireland | etc.

        latitude    :   Latitude coordinate of where the volcano is located

        longitude   :   Longitude coordinate of where the volcano is located

        pei         :   The Population Exposure Index of a volcano. Scales from 1-10

        latitude    :   Latitude coordinates of a Given Volcano. Must be exact

        longitude   :   Longitude coordinates of a Given Volcano. Must be exact

        h_active    :   Whether the Volcano is Active or Not. True or False

        vei         :   The Volcanic Explositivity Index. Can be unknown, an integer, unconfirmed, etc.

        hazard      :   The Volcano Hazard Index. Integer Range from 0-3 with 3 being most hazard

        classified  :   Hazard level of classified volcanoessssss
                        U-HR   = Unclassified with Holocene Record
                        U-NHHR = Unclassified No Historic or Holocene Record
                        U-HHR  = Unclassified with Historic and Holocene record
                        Unknown   = unknown classification of given volcano

        risk        :   Risk Level Risk defined through a combination of hazard, exposure and vulnerability
                        Integer Ranging from 0-3 with 3 being at high risk
        
    ### Returns:
        tuple : volcano with their information that fits the search requirements 
                or an error specifying no match

    ## Examples:
    [http://127.0.0.1:8080/find_One/](http://127.0.0.1:8080/find_One/)

    [http://127.0.0.1:8080/find_One/?country=Italy](http://127.0.0.1:8080/find_One/?country=Italy)

    [http://127.0.0.1:8080/find_One/?country=Italy&h_active=true](http://127.0.0.1:8080/find_One/?country=Italy&h_active=true)

    [http://127.0.0.1:8080/find_One/?region=Antarctica&h_active=true&pei=1](http://127.0.0.1:8080/find_One/?region=Antarctica&h_active=true&pei=1)

    ### Results:
    """

    #Get everything that. . .
    get_vol = f"""SELECT * FROM public.volcanoes WHERE"""

    #An ID was specified
    if(id is not None):
        get_vol += f""" id = '{id}'  AND"""

    #A volcanoid was specified
    if(volcanoid is not None):
        get_vol += f""" volcanoid = '{volcanoid}'  AND"""

    #The name of a volcano was given
    if(name is not None):
        get_vol += f""" name = '{name}'  AND"""
        
    #The name of a specific country was given
    if(country is not None):
        get_vol += f""" country = '{country}'  AND"""

    #The name of a specific region was given
    if(region is not None):
        get_vol += f""" region = '{region}'  AND"""
            
    #The name of a given subregion is provided
    if(subregion is not None):
        get_vol += f""" subregion = '{subregion}'  AND"""

    #Latitude coordinates provided
    if(lat is not None):
        get_vol += f""" latitude = '{lat}'  AND"""

    #Longitude coordinates provided
    if(lon is not None):
        get_vol += f""" longitude = '{lon}'  AND"""

    #Given a population exposure index value
    if(pei is not None):
        get_vol += f""" pei = '{pei}'  AND"""
    
    #The volcano should be active or inactive
    if(h_active is not None):
        get_vol += f""" h_active = '{h_active}'  AND"""

    #The volcano explositivity index is given
    if(vei is not None):
        get_vol += f""" vei_holoce = '{vei}'  AND"""
            
    #A specific hazard level was given
    if(hazard is not None):
        get_vol += f""" hazard = '{hazard}'  AND"""

    #A specific classification was given
    if(classified is not None):
        get_vol += f""" classified = '{classified}'  AND"""
            
    #A specific risk level was specified
    if(risk is not None):
        get_vol += f""" risk = '{risk}'  AND"""

    #Find the first volcano with the above's specifications: 
    #If all are none return first found volcano
    get_vol = get_vol[:-5] + " LIMIT 1;"
    

    with DatabaseCursor('.config.json') as cur:
        #Get Column Names
        cur.execute("SELECT * FROM volcanoes")
        cols = [desc[0] for desc in cur.description]

        #Get first volcano that matches parameters
        vols = cur.execute(get_vol)
        vols = cur.fetchall()

    if(vols != []):
        vols = [zip(cols, vols[i]) for i in range(len(vols))]
        return vols
    else:
        return {"Error": "No volcano has the given specifications."}

@app.get("/find_Many/")
async def findMany(
    id: int = None, 
    volcanoid: int = None, 
    name: str = None, 
    country: str = None, 
    region: str = None, 
    subregion: str = None, 
    lat: float = None,
    lon: float = None,
    pei: int = None, 
    h_active: bool = None, 
    vei: str = None, 
    hazard: int = None,
    classified: str = Query(None, enum=["U-HR", "U-HHR", "U-NHHR", "Unknown"]), 
    risk: int = None,  
    ):
    """
    ### Description:
        Get a particular volcano's information based on which column to search for.
        The user can narrow their search by searching for particular parts of multiple
        columns. Giving no parameters will return the first volcano in the database.
        Giving a parameter that does not exist within the provided column will return
        a message saying that no volcano exists with the given specifications.

    ### Optional Params:
        id          :   A particular row to get from the database 

        volcanoid   :   The volcano's unique number

        name        :   Name of a particular volcano

        country     :   Which country the volcano resides in

        region      :   What region the volcano is in. Ex: Middle East and Indian Ocean

        subregion   :   What subregion the volcano is at. Ex: Indian Ocean | New Ireland | etc.

        latitude    :   Latitude coordinate of where the volcano is located

        longitude   :   Longitude coordinate of where the volcano is located

        pei         :   The Population Exposure Index of a volcano. Scales from 1-10

        latitude    :   Latitude coordinates of a Given Volcano. Must be exact

        longitude   :   Longitude coordinates of a Given Volcano. Must be exact

        h_active    :   Whether the Volcano is Active or Not. True or False

        vei         :   The Volcanic Explositivity Index. Can be unknown, an integer, unconfirmed, etc.

        hazard      :   The Volcano Hazard Index. Integer Range from 0-3 with 3 being most hazard

        classified  :   Hazard level of classified volcanoessssss
                        U-HR   = Unclassified with Holocene Record
                        U-NHHR = Unclassified No Historic or Holocene Record
                        U-HHR  = Unclassified with Historic and Holocene record
                        Unknown   = unknown classification of given volcano

        risk        :   Risk Level Risk defined through a combination of hazard, exposure and vulnerability
                        Integer Ranging from 0-3 with 3 being at high risk
        
    ### Returns:
        tuple : volcano with their information that fits the search requirements 
                or an error specifying no match

    ## Examples:
    [http://127.0.0.1:8080/find_Many/](http://127.0.0.1:8080/find_Many/)

    [http://127.0.0.1:8080/find_Many/?country=Italy](http://127.0.0.1:8080/find_Many/?country=Italy)

    [http://127.0.0.1:8080/find_Many/?country=Italy&h_active=true](http://127.0.0.1:8080/find_Many/?country=Italy&h_active=true)

    [http://127.0.0.1:8080/find_Many/?region=Antarctica&h_active=true&pei=1](http://127.0.0.1:8080/find_Many/?region=Antarctica&h_active=true&pei=1)

    ### Results:
    """

    #Get everything that. . .
    get_vol = f"""SELECT * FROM public.volcanoes WHERE"""

    #An ID was specified
    if(id is not None): 
        get_vol += f""" id = '{id}'  AND"""

    #A volcanoid was specified
    if(volcanoid is not None):
        get_vol += f""" volcanoid = '{volcanoid}'  AND"""

    #The name of a volcano was given
    if(name is not None):
        get_vol += f""" name = '{name}'  AND"""
        
    #The name of a specific country was given
    if(country is not None):
        get_vol += f""" country = '{country}'  AND"""

    #The name of a specific region was given
    if(region is not None):
        get_vol += f""" region = '{region}'  AND"""
            
    #The name of a given subregion is provided
    if(subregion is not None):
        get_vol += f""" subregion = '{subregion}'  AND"""

    #Latitude coordinates provided
    if(lat is not None):
        get_vol += f""" latitude = '{lat}'  AND"""

    #Longitude coordinates provided
    if(lon is not None):
        get_vol += f""" longitude = '{lon}'  AND"""

    #Given a population exposure index value
    if(pei is not None):
        get_vol += f""" pei = '{pei}'  AND"""
    
    #The volcano should be active or inactive
    if(h_active is not None):
        get_vol += f""" h_active = '{h_active}'  AND"""

    #The volcano explositivity index is given
    if(vei is not None):
        get_vol += f""" vei_holoce = '{vei}'  AND"""
            
    #A specific hazard level was given
    if(hazard is not None):
        get_vol += f""" hazard = '{hazard}'  AND"""

    #A specific classification was given
    if(classified is not None):
        get_vol += f""" classified = '{classified}'  AND"""
            
    #A specific risk level was specified
    if(risk is not None):
        get_vol += f""" risk = '{risk}'  AND"""

    #Find the first volcano with the above's specifications: 
    #If all are none return first found volcano
    get_vol = get_vol[:-5] + ";"
    

    with DatabaseCursor('.config.json') as cur:
        #Get Column Names
        cur.execute("SELECT * FROM volcanoes")
        cols = [desc[0] for desc in cur.description]

        #Get first volcano that matches parameters
        vols = cur.execute(get_vol)
        vols = cur.fetchall()

    if(vols != []):
        vols = [zip(cols, vols[i]) for i in range(len(vols))]
        return vols
    else:
        return {"Error": "No volcano has the given specifications."}

@app.get("/find_Closest/")
async def findClosest(long: float = 0, lat: float = 0):
    """
    ### Description:
        Find the volcano closest to a given set of longitude and latitude
        coordinates. The x value for this represents longitude and the y
        value is for latitude. To find the closest volcano, we use 
        postgis to compare the geometry of our spatial data with the
        coordinates given.

    ### Params:
        lat     :   latitude coordinate of a specified point

        long    :   longitude coordinate of a specified point

    ### Returns:
        tuple : the volcano's information of the closest volcano to the given point

    ## Examples:
    [http://127.0.0.1:8080/find_Closest/](http://127.0.0.1:8080/find_Closest/)

    [http://127.0.0.1:8080/find_Closest/?lat=.2&long=-5.5](http://127.0.0.1:8080/find_Closest/?lat=.2&long=-5.5)

    ### Results:
    """

    #Query the database based on how close each volcano 
    #is to the given coordinates. The first row is the closest volcano.
    closest_vol = f"""SELECT * FROM volcanoes 
    ORDER BY location <-> 'SRID=4326;POINT({long} {lat})'::geometry 
    LIMIT 1;"""
    
    with DatabaseCursor('.config.json') as cur:

        #Get the names of all of the columns for easier readability
        cur.execute("SELECT * FROM volcanoes")
        cols = [desc[0] for desc in cur.description]

        #Get the closest volcano compared to the given coordinates
        vols = cur.execute(closest_vol)
        vols = cur.fetchall()[0]

    if(vols != []):
        vols = zip(cols, vols)
        return vols
    else:
        return {"Error": "The coordinates provided do not meet the requirements."}


'#########################################################################################'
'                                       MAIN                                              '
'#########################################################################################'

if __name__ == "__main__":
    
    #Importing the csv data into the database and cleaning up the data as well

    # with DatabaseCursor('.config.json') as cur:
    #     cur.execute(create_extension)
    #     cur.execute(drop_table)
    #     cur.execute(create_table)

    #     with open("volcano.csv", newline="") as csvfile:
    #         data = list(csv.reader(csvfile, delimiter=","))
    #         counter = 1
    #         for row in data[1:]:
    #             newRow = []
    #             newRow.append(str(counter))
    #             colCount = 1
    #             for col in row:
    #                 if col == '':
    #                     col = "0"

    #                 if "'" in col:
    #                     col = col.replace("'", "`")

    #                 if not is_float(col) and not is_integer(col):
    #                     col = "'" + col + "'"

    #                 #This is to have the activity of the volcano be a boolean. 
    #                 # For some reason postgreSQL did not like 0 and 1
    #                 if colCount == 9:
    #                     if(col == '0'):
    #                         col = 'false'
    #                     else:
    #                         col = 'true'

    #                 if colCount == 12:
    #                     if(col == "'NULL'"):
    #                         col = "'Unknown'"
                           

    #                 newRow.append(col)
    #                 colCount += 1
    #             row = ", ".join(newRow)
    #             sql = f"INSERT INTO public.volcanoes VALUES ({row});"
    #             counter += 1

    #             cur.execute(sql)

    #     cur.execute(drop_cols)
        #sql = "select * from public.volcanoes;"
        #cur.execute(sql)

        #print(cur.fetchall())

    #Run the FastAPI as localhost  
    uvicorn.run("main:app", host="127.0.0.1", port=8080, log_level="debug", reload=True)