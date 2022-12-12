from pathlib import Path
import glob
from operator import itemgetter
import lib
import json

def main(test=False):
    encoding_bases = get_encoding_bases()
    if test:
        test_payload(encoding_bases)
    data = {}
    data["encoding_bases"] = encoding_bases
    data["tiles2routes"] = get_tiles2routes(encoding_bases)
    data["linestrings"] = get_linestrings()
    with open(f"{lib.base_dir}/data.js", "w") as f:
        f.write("const data = " + json.dumps(data, separators=(",", ":")) + ";")
    
def get_encoding_bases():
    """ get the highest common base for each tile level """
    tiles = {}
    for tile in lib.get_tiles():
        z = tile["z"]
        tiles[z] = tiles.get(z, [])
        tiles[z].append({ "x": str(tile["x"]), "y": str(tile["y"]) })

    encoding_bases = {}
    for z in lib.zoom_levels:
        bases = { "x": tiles[z][0]["x"], "y": tiles[z][0]["y"] }
        def rebase():
            nonlocal bases
            for tile in tiles[z]:
                for c in ["x", "y"]:
                    if not tile[c].startswith(bases[c]):
                        bases[c] = bases[c][:-1]
                        rebase()
        rebase()
        encoding_bases[z] = bases
    return encoding_bases

def test_payload(encoding_bases):
    """ test the size of the json payload given the bases """
    for encode in [False, True]:
        path = Path("{lib.base_dir}/.tmp.txt")
        with open(path.resolve(), "w") as f:
            for tile in lib.get_tiles():
                z = tile["z"]
                less = len(encoding_bases[z]["x"]) + len(encoding_bases[z]["y"])
                required_len = len(str(tile["x"]))+ len(str(tile["y"])) - 1 - int(encode) * less
                f.write("Z" * required_len)
        print(f"encoding={encode}")
        print(path.stat().st_size / 1000000, " MB")
        print(path.stat().st_size / 1000, " KB")
        path.unlink()

def get_tiles2routes(encoding_bases):
    """ set a tile lookup for routes. keys are encoded tile ids, vals are indexes of routes """

    def encode_tile(tile):
        """ get an encoded tile key, e.g. "6076779" -> "16" + "19076" + "24779" """
        x, y = itemgetter("x", "y")(encoding_bases[tile["z"]])
        tile["x"] = str(tile["x"]).replace(x, "")
        tile["y"] = str(tile["y"]).replace(y, "")
        return f"1{tile['x']}{tile['y']}"

    tiles = {}
    routes = lib.get_routes()
    for i, route in enumerate(routes, 1):
        print(f"getting tiles2routes lookup for route={route} ({i} of {len(routes)})")
        # get the linestrings and coords
        multilinestring = lib.parse_multiline(route)
        coords = []
        for linestring in multilinestring.geoms:
            coords.extend([coord for coord in linestring.coords])
        # for each coord get associated tiles
        for coord in coords:
            for z in lib.zoom_levels:
                x, y = lib.deg2num(coord[1], coord[0], z)
                tile = encode_tile({ "z": z, "x": x, "y": y })
                # add this tile as a key
                tiles[tile] = tiles.get(tile, [])
                if route not in tiles[tile]:
                    tiles[tile].append(route)
    return tiles

def get_linestrings():
    """ set a matrix of linestrings by route """
    dct = {}
    routes = lib.get_routes()
    for i, route in enumerate(routes, 1):
        print(f"getting linestrings for route={route} ({i} of {len(routes)})")
        multilinestring = lib.parse_multiline(route)
        linestrings = []
        for linestring in multilinestring.geoms:
            rd_linestring = []
            for coord in linestring.coords:
                rd_coord = (round(coord[1], 6), round(coord[0], 6))
                rd_linestring.append(rd_coord)
            linestrings.append(rd_linestring)
        dct[route] = linestrings
    return dct

if __name__ == "__main__":
    main(test=False)
