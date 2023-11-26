import openrouteservice
from openrouteservice import convert
from openrouteservice.directions import directions
import os


client = openrouteservice.Client(key=os.environ.get("ORS_KEY"))


def get_directions(start_coords, end_coords):
    return directions(client, (start_coords, end_coords))


def get_decoded_directions(start_coords, end_coords):
    dirs = get_directions(start_coords, end_coords)
    return convert.decode_polyline(dirs['routes'][0]['geometry'])


def decode_geometry(geometry):
    return convert.decode_polyline(geometry)


def get_reversed_polyline_directions(coords):
    return [list(reversed(point)) for point in coords]
