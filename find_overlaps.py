import sys
from collections import defaultdict
from urllib.request import urlopen
from proto.BulkOrPlanetoid_pb2 import BulkOrPlanetoid

from octant_to_latlong import octant_to_latlong
from octant_to_latlong import LatLonBox

PLANET = "earth"
URL_PREFIX = f"https://kh.google.com/rt/{PLANET}/"


def urlread(url):
    with urlopen(url) as f:
        return f.read()


def read_protobuf(url):
    data = BulkOrPlanetoid()
    data.ParseFromString(urlread(url))
    return data


def read_planetoid_metadata():
    url = URL_PREFIX + "PlanetoidMetadata"
    return read_protobuf(url)


def read_bulk_metadata(path, epoch):
    url = URL_PREFIX + f"BulkMetadata/pb=!1m2!1s{path}!2u{epoch}"
    return read_protobuf(url)


def parse_path_id(path_id):
    def split_bits(x, n):
        mask = (1 << n) - 1
        return x >> n, x & mask

    path_id, level = split_bits(path_id, 2)

    path_segments = list()
    for _ in range(level + 1):
        path_id, x = split_bits(path_id, 3)
        path_segments.append(x)

    return path_segments, path_id


class NodeData(object):
    def __init__(self, bulk_path, path_id):
        path_segments, flags = parse_path_id(path_id)
        path_string = ''.join(str(x) for x in path_segments)

        self.path = bulk_path + path_string
        self.flags = flags

    def is_bulk(self):
        return (len(self.path) % 4 == 0) and (not (self.flags & 4))

    @staticmethod
    def from_bulk_data(bulk):
        bulk_path = bulk.head_node.path
        return [NodeData(bulk_path, x.path_id) for x in bulk.data]


class OverlappingOctants(object):
    def __init__(self, box):
        self.box = box
        self.list = defaultdict(list)

    def __getitem__(self, level):
        return self.list[level]

    def is_overlapping(self, node_data):
        node_box = octant_to_latlong(node_data.path)
        return LatLonBox.is_overlapping(node_box, self.box)

    def update_bulk_data(self, bulk):
        for node in NodeData.from_bulk_data(bulk):
            if self.is_overlapping(node):
                self.list[len(node.path)].append(node)


MAX_COUNT = 10

input_box = sys.argv[1:5]
input_box = LatLonBox(*(float(x) for x in input_box))
print(input_box)

overlapping_octants = OverlappingOctants(input_box)

planetoid_metadata = read_planetoid_metadata()
epoch = planetoid_metadata.data[0].epoch
bulk = read_bulk_metadata('', epoch)

overlapping_octants.update_bulk_data(bulk)

for level in range(1, 21):
    print(f"[Octant level {level}]")
    for octant in overlapping_octants[level]:
        print(octant.path)

    if len(overlapping_octants[level]) >= MAX_COUNT:
        break

    for octant in overlapping_octants[level]:
        if octant.is_bulk():
            bulk = read_bulk_metadata(octant.path, epoch)
            overlapping_octants.update_bulk_data(bulk)
