# interpreted_raycaster
Takes an NxN image as input and generates a map which is later used for raycasting.

![raycaster](https://github.com/eksd3/interpreted_raycaster/blob/master/images/ss.png)

### Dependencies
Depends on Pygame and PIL (pillow) for extracting the pixel's RGB values.

### Map color values
The RGB codes for the map elements are:
(255, 255, 255) - Floor
(0, 0, 0) - Wall
(0, 0, 255) - Door
(255, 0, 0) - Starting position

### Controls
Arrow keys to move.
1, 2 and 3 to toggle rendering fog, shadow and debug lines on the walls, respectively.
q and w to change resolution.
M key shows the full map.
Enter passes through a door.
