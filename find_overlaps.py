import sys
from collections import defaultdict
from urllib.request import urlopen

from octant_to_latlong import LatLonBox
from octant_to_latlong import octant_to_latlong
from proto.rocktree_pb2 import BulkMetadata
from proto.rocktree_pb2 import PlanetoidMetadata

PLANET = "earth"
URL_PREFIX = f"https://kh.google.com/rt/{PLANET}/"


def urlread(url):
    with urlopen(url) as f:
        return f.read()


def read_planetoid_metadata():
    url = URL_PREFIX + "PlanetoidMetadata"
    metadata = PlanetoidMetadata()
    metadata.ParseFromString(urlread(url))
    return metadata


def read_bulk_metadata(path, epoch):
    url = URL_PREFIX + f"BulkMetadata/pb=!1m2!1s{path}!2u{epoch}"
    metadata = BulkMetadata()
    metadata.ParseFromString(urlread(url))
    return metadata


def parse_path_and_flags(data):
    def split_bits(x, n):
        mask = (1 << n) - 1
        return x >> n, x & mask

    data, level = split_bits(data, 2)

    path_segments = list()
    for _ in range(level + 1):
        data, x = split_bits(data, 3)
        path_segments.append(x)

    path = "".join(str(x) for x in path_segments)
    return path, data


class Octant:
    def __init__(self, head_node_key, node_data):
        self.head_node_key = head_node_key
        self.node_data = node_data

        path, flags = parse_path_and_flags(self.node_data.path_and_flags)
        self.path = self.head_node_key.path + path
        self.flags = flags

        self.epoch = self.node_data.bulk_metadata_epoch
        if self.epoch == 0:
            self.epoch = self.head_node_key.epoch

        self.level = len(self.path)
        self.bbox = octant_to_latlong(self.path)

    @property
    def is_leaf(self):
        return bool(self.flags & 4)


def find_overlaps(bbox, max_octants_per_level):
    planetoid_metadata = read_planetoid_metadata()
    root_epoch = planetoid_metadata.root_node_metadata.epoch

    overlapping_octants = defaultdict(list)

    def update_overlapping_octants(path, head_node_epoch):
        bulk = read_bulk_metadata(path, head_node_epoch)
        for node_data in bulk.node_metadata:
            octant = Octant(bulk.head_node_key, node_data)
            if octant.bbox.overlaps_with(bbox):
                overlapping_octants[octant.level].append(octant)

    update_overlapping_octants("", root_epoch)
    for level in range(1, 21):
        if len(overlapping_octants[level]) >= max_octants_per_level:
            break
        if level % 4 == 0:
            for octant in overlapping_octants[level]:
                if not octant.is_leaf:
                    update_overlapping_octants(octant.path, octant.epoch)

    return overlapping_octants


def args_to_bbox(args):
    args = [float(x.rstrip(",")) for x in args]
    bottom, top = sorted([args[0], args[2]])
    left, right = sorted([args[1], args[3]])
    return LatLonBox(north=top, south=bottom, west=left, east=right)


if __name__ == "__main__":
    bbox = args_to_bbox(sys.argv[1:5])
    print(bbox)

    overlapping_octants = find_overlaps(bbox, max_octants_per_level=10)
    for level in sorted(overlapping_octants):
        print(f"[Octant level {level}]")
        for octant in overlapping_octants[level]:
            print(octant.path)
