from pprint import pprint
import openrouteservice
from openrouteservice import convert
from openrouteservice.directions import directions
from openrouteservice.isochrones import isochrones
import os


client = openrouteservice.Client(base_url='http://localhost:8080/ors')


def get_directions(start_coords, end_coords, _profile='driving-car'):
    dirs = directions(client, (start_coords, end_coords), profile=_profile)
    return dirs


def get_decoded_directions(start_coords, end_coords):
    dirs = get_directions(start_coords, end_coords)
    return convert.decode_polyline(dirs['routes'][0]['geometry'])


def decode_geometry(geometry):
    return convert.decode_polyline(geometry)


def get_reversed_polyline_directions(coords):
    return [list(reversed(point)) for point in coords]


def get_isochrones(coords, _profile='driving-car', _range=60):
    return isochrones(client, coords, profile=_profile, range=[_range])

