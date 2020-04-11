Here are some random python scripts for working with [retroplasma/earth-reverse-engineering](https://github.com/retroplasma/earth-reverse-engineering).

Requirements:

    pip install protobuf

Usage:

    python find_overlaps.py <latitude_1> <longitude_1> <latitude_2> <longitude_2>

You may keep the comma after the latitude. The script will just ignore any trailing comma.
The order of the `<latitudes>` and `<longitudes>` doesn't matter. The script will sort them automatically.

Example output:
```
> python find_overlaps.py 37.419714, -122.083275 37.420626, -122.085045

LatLonBox(north=37.420626, south=37.419714, west=-122.085045, east=-122.083275)
[Octant level 1]
2
[Octant level 2]
20
[Octant level 3]
205
[Octant level 4]
2052
[Octant level 5]
20527
[Octant level 6]
205270
[Octant level 7]
2052706
[Octant level 8]
20527061
[Octant level 9]
205270616
[Octant level 10]
2052706160
[Octant level 11]
20527061605
[Octant level 12]
205270616052
[Octant level 13]
2052706160527
[Octant level 14]
20527061605273
[Octant level 15]
205270616052735
[Octant level 16]
2052706160527351
[Octant level 17]
20527061605273514
[Octant level 18]
205270616052735141
205270616052735140
[Octant level 19]
2052706160527351416
2052706160527351417
2052706160527351415
2052706160527351414
2052706160527351405
2052706160527351407
2052706160527351406
2052706160527351404
[Octant level 20]
20527061605273514162
20527061605273514160
....
```
