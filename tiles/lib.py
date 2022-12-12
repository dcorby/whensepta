import glob
from pathlib import Path
import geopandas as gpd
import math
import shapely

base_dir = "/root/dev/septa"
zoom_levels = [15, 16, 17]

def get_tiles(orig=False):
    pathnames = list(glob.iglob(f"{base_dir}/{'orig_' if orig else ''}tiles/**/*.png", recursive=True))
    tiles = []
    for pathname in pathnames:
        tmp = pathname.replace(".png", "").split("/")[-3:]
        tile = { "z": int(tmp[0]), "x": int(tmp[1]), "y": int(tmp[2]) }
        tiles.append(tile)
    return tiles
    
def get_routes():
    df = gpd.read_file(f"{base_dir}/routes/routes.geojson")
    routes = [x for x in list(df.lineabbr.unique()) if x not in ["316"]]
    return routes

# shapely.ops.linemerge
# https://gis.stackexchange.com/questions/415648/is-there-a-way-to-sort-points-in-a-multilinestring-such-that-they-seem-more-li
def parse_multiline(route):
    df = gpd.read_file(f"{base_dir}/routes/routes.geojson")
    row = df.loc[df["lineabbr"] == route]
    multilinestrings = [x for x in row["geometry"]]
    if len(multilinestrings) != 1:
        raise Exception("zero or multiple multilinestrings found")
    linestrings = shapely.ops.linemerge(multilinestrings[0])
    return linestrings

# this duplicates mercantile.tile()
def deg2num(lat_deg, lon_deg, zoom):
    """ given lat/lon and zoom, get xtile and ytile """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


