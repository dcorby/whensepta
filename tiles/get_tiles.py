import geopandas as gpd 
import numpy as np
import mercantile
from pathlib import Path
import urllib.request
import time
import lib

def main():
    # get the map bounds
    df = gpd.GeoDataFrame.from_file("philly.geojson")
    bounds = df.to_crs("epsg:4326").total_bounds
    minx, miny, maxx, maxy = bounds

    # get the tiles
    tiles = {}
    for z in lib.zoom_levels:
        if not tiles.get(z):
            tiles[z] = set()
        for x in np.arange(minx, maxx + 0.001, 0.001):
            for y in np.arange(miny, maxy + 0.001, 0.001):
                tile = mercantile.tile(x, y, z)
                tiles[z].add(tile)
    total = 0
    for z in tiles:
        total += len(tiles[z])

    count = 0
    for z in tiles:
        for i, tile in enumerate(tiles[z], 1):
            count += 1
            x, y, z = tile.x, tile.y, tile.z
            tpath = Path(f"{lib.base_dir}/tiles/plain/{z}/{x}/{y}.png")
            if tpath.is_file():
                print(f"found tile={tpath.resolve()}")
                continue
            tpath.parent.mkdir(exist_ok=True, parents=True)
            cont = False
            product = ["a", "b", "c"]
            for typ in product:
                if cont:
                    continue
                url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
                of = f"({i} of {len(tiles[z])}, {count} of {total})"
                try:
                    print(f"downloading={url} {of}")
                    urllib.request.urlretrieve(url, tpath.resolve())
                except urllib.error.HTTPError:
                    if typ == "c":
                        print("missing tile")
                    else:
                        continue
                cont = True

if __name__ == "__main__":
    main()
