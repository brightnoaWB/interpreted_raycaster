# interpreted_raycaster
Takes an NxN image as input and generates a map which is later used for raycasting.

Depends on PIL (pillow) for extracting the pixel's RGB values.

The RGB codes for the map elements are:
(255, 255, 255) - Floor
(0, 0, 0) - Wall
(0, 0, 255) - Door
(255, 0, 0) - Starting position

M key shows the full map.
Enter passes through a door.
