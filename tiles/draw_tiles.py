from pathlib import Path
import glob
import math
import cairo
import shutil
import lib
import statistics

def main():
    """ copy base tiles to drawn folder """
    copy_tiles()

    """ get the routes and drawn them one at a time """
    routes = lib.get_routes()
    #routes = [r for r in routes if r in ["47", "57"]]
    for route_idx, route in enumerate(routes, 1):

        multilinestring = lib.parse_multiline(route)

        # associate all lines with tiles
        tiles = {}
        for z in lib.zoom_levels:
            for linestring_idx, linestring in enumerate(multilinestring.geoms):
                keys = set()
                for coord in linestring.coords:
                    x, y = lib.deg2num(coord[1], coord[0], z)
                    key = (z, x, y)
                    keys.add(key)
                for key in keys:
                    if key not in tiles:
                        tiles[key] = []
                    tiles[key].append(linestring_idx)

        # iterate over tiles
        for key in sorted(tiles):
            z, x, y = key
            drawn_path = f"{lib.base_dir}/tiles/drawn/{z}/{x}/{y}.png"
            try:
                cim = cairo.ImageSurface.create_from_png(drawn_path)
                c = cairo.Context(cim)
            except Exception as e:
                continue

            # iterate lines
            for ls_idx in tiles[key]:
                linestring = multilinestring.geoms[ls_idx]
                points = []
                for coord in linestring.coords:
                    point = coord_to_point(coord, x, y, z)
                    points.append(point)

                c.move_to(points[0][0], points[0][1])
                distance = 0.0
                prev_pt = None
                for i, pt in enumerate(points[1:]):
                    c.line_to(pt[0], pt[1])
                    if prev_pt:
                        distance += math.dist(pt, prev_pt)
                    if distance >= 100.0 and 1 <= i <= len(points[1:]) - 1:
                        #draw_caret(cairo.Context(cim), points[i-1:i+2])
                        distance = 0.0
                    prev_pt = pt
                c.set_line_width(3.0)
                c.set_source_rgb(56/255, 120/255, 182/255)
                c.stroke()
                c.new_path()

            path = Path(drawn_path)
            path.parent.mkdir(exist_ok=True, parents=True)
            print(f"route={route} ({route_idx} of {len(routes)}), writing file={path.resolve()}")
            cim.write_to_png(drawn_path)

def draw_caret(c, points):
    """
    len(points) = 3
    diff of angle(p1 - p0) and angle(p2 - p1) <= 10
    draw north-pointing caret and rotate to mean([angle1, angle2])
    https://stackoverflow.com/questions/15994194/how-to-convert-x-y-coordinates-to-an-angle
    """

    def at_angle(p1, angle):
        center = [p1[0], p1[1]]
        radius = 15
        rad = math.pi + (angle * math.pi / 180.0)
        x = p1[0] + (radius * math.cos(rad))
        y = p1[1] + (radius * math.sin(rad))
        return (x, y)

    # get angle1
    delta_x = points[1][0] - points[0][0]
    delta_y = points[1][1] - points[0][1]
    rad = math.atan2(delta_y, delta_x)
    angle1 = rad * (180.0 / math.pi)

    # get angle2
    delta_x = points[2][0] - points[1][0]
    delta_y = points[2][1] - points[1][1]
    rad = math.atan2(delta_y, delta_x)
    angle2 = rad * (180.0 / math.pi)

    if abs(angle2 - angle1) <= 10.0:
        rotated = statistics.mean([angle1, angle2])
        # draw north pointing caret then rotate it
        c.move_to(points[1][0], points[1][1])
        c.line_to(*at_angle(points[1], 135 + rotated))
        c.move_to(points[1][0], points[1][1])
        c.line_to(*at_angle(points[1], 225 + rotated))
        c.move_to(points[1][0], points[1][1])
        c.set_line_width(3.0)
        c.set_source_rgb(56/255, 120/255, 182/255)
        c.stroke()

def copy_tiles():
    """ copy the tiles from plain to drawn """
    drawn_path = Path(f"{lib.base_dir}/tiles/drawn")
    if drawn_path.exists() and drawn_path.is_dir():
        shutil.rmtree(drawn_path.resolve())
    for filename in glob.iglob(f"{lib.base_dir}/tiles/plain/**/*.png", recursive=True):
        dest = filename.replace("plain", "drawn")
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(filename, dest)

def get_angle(lat1, long1, lat2, long2):
    """ get the angle between two coordinates """
    dLon = (long2 - long1)
    y = math.sin(dLon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
    brng = math.atan2(y, x)
    brng = math.degrees(brng)
    brng = (brng + 360) % 360
    brng = 360 - brng # count degrees clockwise - remove to make counter-clockwise
    # 0 is north
    return brng

def coord_to_point(coord, xtile, ytile, zoom):
    """ given a coordinate and z/x/y return a point """
    # https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_numbers_to_lon./lat._2
    def get_corner():
        n = 2.0 ** zoom
        lon_deg = (xtile + int(corner.endswith("right"))) / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * (ytile + int(corner.startswith("bottom"))) / n)))
        lat_deg = math.degrees(lat_rad)
        return { "lat": lat_deg, "lon": lon_deg }

    corners = { "topright"   : get_corner("topright"), 
                "topleft"    : get_corner("topleft"),
                "bottomright": get_corner("bottomright"),
                "bottomleft" : get_corner("bottomleft")
              }
    pct_x = (coord[0] - corners["topright"]["lng"]) / (corners["topleft"]["lng"] - corners["topright"]["lng"])
    pct_y = (coord[1] - corners["bottomleft"]["lat"]) / (corners["topleft"]["lat"] - corners["bottomleft"]["lat"])
    return (256 - (pct_x * 256.0), 256 - (pct_y * 256.0))

if __name__ == "__main__":
    main()
