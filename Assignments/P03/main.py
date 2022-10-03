import json
from rich import pretty
import psycopg2
from random import randint

north = []
south = []
east = []
west = []

with open('my_us_box.geojson', "r") as f:
    points = json.load(f)
    points = points["features"][1]['geometry']['coordinates']

for point in points:
    if(int(point[1]) in range(52, 58)):
        north.append(point)
        continue
    if(int(point[1]) in range(17,21)):
        south.append(point)
        continue
    if(int(point[0]) in range(-132, -127)):
        west.append(point)
        continue
    else:
        east.append(point)

pairs = []
if(len(west) >= len(east)):
    for point in range(len(east)):
        pairs.append([west[point], east[point]])
    remainingWE = west[len(east):]
else:
    for point in range(len(west)):
        pairs.append([west[point], east[point]])
    remainingWE = east[len(west):]

if(len(north) >= len(south)):
    for point in range(len(south)):
        pairs.append([north[point], south[point]])
    remainingNS = north[len(south):]
else:
    for point in range(len(north)):
        pairs.append([north[point], south[point]])
    remainingNS = south[len(north):]

if(len(remainingWE) >= len(remainingNS)):
    for point in range(len(remainingNS)):
        pairs.append([remainingNS[point], remainingWE[point]])
        remaining = [remainingWE[len(remainingNS):], 'WE']
else:
    for point in range(len(remainingWE)):
        pairs.append([remainingNS[point], remainingWE[point]])
        remaining = [remainingNS[len(remainingWE):], 'NS']

switch = []

if(remaining[-1] == 'NS'):
    coor = pairs[:len(remaining[0])]
    for points in range(len(coor[0][0])):
        switch.append(pairs[points][points - 1])
        pairs[points] = ([coor[points][points], remaining[0][points]])    
else:
    coor = pairs[-len(remaining[0]) // 2:]
    for points in range(len(coor[0][0])):
        switch.append(pairs[points][points - 1])
        pairs[points] = ([coor[points][points], remaining[0][points]])
pairs.append(switch)

"""          MAKE SQL TABLE of MISSILE TRAJECTORIES       """
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

drop_table = "DROP TABLE  IF EXISTS missile_trajectories;"

create_table = """CREATE TABLE public.missile_trajectories (
    id NUMERIC PRIMARY KEY,
    altitude NUMERIC NOT NULL,
    speed NUMERIC NOT NULL,
    degree DECIMAL(11,8) NOT NULL,
    start_longitude DECIMAL(11,8) NOT NULL,
    start_latitude DECIMAL(11,8) NOT NULL,
    end_longitude DECIMAL(11,8) NOT NULL,
    end_latitude DECIMAL(11,8) NOT NULL,
    geom GEOMETRY);"""

if __name__ == "__main__":
    
    with DatabaseCursor('.config.json') as cur:
        cur.execute(create_extension)
        cur.execute(drop_table)
        cur.execute(create_table)

        #Fill table with missile trajectories based on coordinate pairs
        count = 0
        Lines = []
        for pair in pairs:
                ids = count
                altitude = randint(10, 30) * 1000
                speed = randint(1, 9) * 111
                degree = 1 / (10 ** randint(0, 8))
                start_lon = pair[0][0]
                start_lat = pair[0][1]
                end_lon = pair[1][0]
                end_lat = pair[1][1]
                line = f"""SELECT ST_AsGEOJSON(ST_LineInterpolatePoints('LINESTRING({start_lon} {start_lat}, {end_lon} {end_lat})',0.01))"""
                cur.execute(line)
                geom = cur.fetchall()[0][0]

                sql = f"""INSERT INTO public.missile_trajectories VALUES ({ids}, {altitude}, {speed}, {degree},\
                {start_lon}, {start_lat}, {end_lon}, {end_lat}, '{geom}');"""

                cur.execute(sql)
                count += 1

        cur.execute("""SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(ST_AsGeoJSON(t.*)::json)
            )
            FROM public.missile_trajectories
            as t(id, name, geom);""")

        trajectories = cur.fetchall()
    with open('my_missile_trajectories.geojson', "w") as f:
        json.dump(trajectories[0][0], f)
                


