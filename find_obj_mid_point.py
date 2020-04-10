import sys
import numpy as np


def load_obj_vertices(filename):
    def iter_vertices(filename):
        with open(filename) as f:
            for line in f:
                if line.startswith("v "):
                    yield np.fromstring(line[2:], sep=' ')

    vertices = list(iter_vertices(filename))
    vertices = np.array(vertices)
    return vertices


def get_mid_point(array):
    return (array.min() + array.max()) / 2


def find_mid_point_by_lat_lon_rad(vertices):
    radiuses = np.linalg.norm(vertices, axis=1)
    latitudes = np.arcsin(vertices[:, 2] / radiuses)
    longitudes = np.arctan2(vertices[:, 1], vertices[:, 0])

    rad = get_mid_point(radiuses)
    lat = get_mid_point(latitudes)
    lon = get_mid_point(longitudes)

    x = rad * np.cos(lat) * np.cos(lon)
    y = rad * np.cos(lat) * np.sin(lon)
    z = rad * np.sin(lat)
    return np.array([x, y, z])


input_file = sys.argv[1]
vertices = load_obj_vertices(input_file)
mid_point = find_mid_point_by_lat_lon_rad(vertices)
print(mid_point)
