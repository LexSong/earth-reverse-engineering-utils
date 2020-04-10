import sys
from pathlib import Path

import numpy as np
from tqdm import tqdm

origin = np.array([float(x) for x in sys.argv[1:4]])

radius = np.linalg.norm(origin)
lat = np.arcsin(origin[2] / radius)
lon = np.arctan2(origin[1], origin[0])

sin_lat = np.sin(lat)
cos_lat = np.cos(lat)
sin_lon = np.sin(lon)
cos_lon = np.cos(lon)

Rz = np.array([[cos_lon, sin_lon, 0], [-sin_lon, cos_lon, 0], [0, 0, 1]])
Ry = np.array([[cos_lat, 0, sin_lat], [0, 1, 0], [-sin_lat, 0, cos_lat]])
R = Ry @ Rz

input_file = Path(sys.argv[4])
output_file = input_file.with_name(input_file.stem + ".2.obj")

with input_file.open() as in_, output_file.open("w") as out:
    for line in tqdm(in_):
        if line.startswith("v "):
            vertex = np.fromstring(line[2:], sep=" ")
            vertex = R @ (vertex - origin)
            line = "v {} {} {}\n".format(*vertex)

        out.write(line)
