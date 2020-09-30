###
# Floorcasting and raytracing algorithm/code by raytomely
# https://itch.io/profile/raytomely
###

import pygame,sys
from math import *
from pygame.locals import *
from PIL import Image

import maps as maps
import scr as scr

def check_event(player_pos, event_pos, grid_width):

    # checks if player is on a tile that has an event
    # not in events because it's only applicable in dungeons

    if player_pos[0] >= event_pos[0] and player_pos[0] <= event_pos[0] + grid_width:
        if player_pos[1] >= event_pos[1] and player_pos[1] <= event_pos[1] + grid_width:
            return True;

    return False;

def check_oob( player_pos, v_ang, grid, grid_width ):

    # checks if the player is out of bounds

    x_min = 0
    y_min = 0
    x_max = len( grid[0] ) * grid_width
    y_max = len( grid ) * grid_width

    # avoids OoR error
    margin = grid_width + 33

    if player_pos[0] + margin >= x_max:
        if v_ang == 0:
            return False;

    elif player_pos[0] - margin <= x_min:
        if v_ang == 180:
            return False;

    # y dir
    if player_pos[1] + margin >= y_max:
        if v_ang == 270:
            return False;

    elif player_pos[1] - margin <= y_min:
        if v_ang == 90:
            return False;

    return True;

class Door( object ):

    # a class for doors

    def __init__(self, xpos, ypos):
        self.xpos = xpos * 64
        self.ypos = ypos * 64
        self.active = True

    def check_event(self, player_pos, view_angle, can_move):

        # doors visually glitch if put on a horizontal wall
        # otherwise they behave normally

        if not can_move:

            # looking horizontally

            if view_angle == 0 or view_angle == 180:
                mult = 1
                if view_angle == 180:
                    mult = -1

                # always check for y coords first
                if player_pos[1] == self.ypos + (64 // 2):
                    if player_pos[0] + (64 * mult) > self.xpos:
                        if player_pos[0] + (64 * mult) < self.xpos + 64:
                            self.active = True
                            return True;

            # looking vertically

            if view_angle == 90 or view_angle == 270:
                mult = 1
                if view_angle == 90:
                    mult = -1

                if player_pos[ 0 ] == self.xpos + ( 64 // 2 ):
                    if player_pos[ 1 ] + ( 64 * mult ) > self.ypos:
                        if player_pos[ 1 ] + ( 64 * mult ) < self.ypos + 64:
                            self.active = True
                            return True;

        self.active = False
        return False;

    def action(self, player_pos, view_angle):

        direction = None

        if view_angle == 0 or view_angle == 180:
            direction = 0
            mult = 1
            if view_angle == 180:
                mult = -1

        else:
            direction = 1
            mult = 1
            if view_angle == 90:
                mult = -1

        # displace the player based on the orientation of the door
        if direction == 0:
            pl_x = player_pos[ 0 ] + 2 * 64 * mult
            pl_y = player_pos[ 1 ]
        else:
            pl_x = player_pos[ 0 ]
            pl_y = player_pos[ 1 ] + 2 * 64 * mult

        return [ pl_x, pl_y ];


def init_doors( grid ):

    # loops through the grid and
    # returns a list of all doors

    ev = list()

    for y in range( len( grid ) ):
        for x in range( len( grid[ 0 ] ) ):

            if grid[y][x] == 2:
                ev.append( Door( x, y ) )

    return ev;


def get_pos( grid_pos ):

    # just converts grid coords into "actual" coords

    return grid_pos * 64 + 64 // 2;


def set_spos( grid ):

    # loop throught the grid and
    # set the starting position

    for y in range( len( grid ) ):
        for x in range( len( grid[ 0 ] ) ):

            # check if the slot is denoted as a spos (RED):
            if grid[y][x] == -2:
                return [ get_pos(x), get_pos(y) ];


def make_grid( map_img ):

    # creates a grid from an image

    cl_door = ( 0, 0, 255 )
    cl_spos = ( 255, 0, 0 )
    cl_wall = ( 0, 0, 0 )

    grid_image = Image.open( map_img )
    grid_image = grid_image.convert( "RGB" )

    w = grid_image.size[ 0 ]
    h = grid_image.size[ 1 ]

    # make an empty grid
    #
    grid = list()

    for y in range( 0, h ):
        buffer_list = list()

        for x in range( 0, w ):
            buffer_list.append( -1 )

        grid.append( buffer_list )

    # edit grid to match the image
    #
    for y in range( 0, h ):
        row = ""

        for x in range( 0, w ):

            val = 0
            RGB = grid_image.getpixel(( x, y ))

            # wall (BLACK)
            if RGB == cl_wall:
                val = 1

            # Door (BLUE)
            elif RGB == cl_door:
                val = 2

            # starting pos (RED)
            elif RGB == cl_spos:
                val = -2

            #else:
            #    val = 0

            grid[y][x] = val

    return grid;


# This is the raycaster

def raycaster():

    pygame.init()

    # default vars
    # feel free to change

    BLACK = ( 0, 0, 0 )
    WHITE = ( 225, 225, 225 )
    BLUE = ( 0, 0, 200 )
    GREY = ( 100, 100, 100 )

    WIDTH, HEIGHT = ( 1024, 576 )
    screen = pygame.display.set_mode(( WIDTH, HEIGHT ))

    clock = pygame.time.Clock()
    FPS = 30

    # init the grid
    grid = make_grid( "grid.png" )
    map_ = maps.Map( grid, WIDTH, HEIGHT )

    # load another image as texture2 if you'd like
    # the texture to change
    texture2 = pygame.image.load( "wall.png" )
    texture = pygame.image.load( "wall.png" )

    current_texture = texture
    current_texture_num = 0

    texture_door = pygame.image.load( "door.png" )

    ground=pygame.Surface((WIDTH, HEIGHT // 2)).convert();ground.fill(( 0, 100, 0 ))

    x_limit=len(grid[0])
    y_limit=len(grid)

    can_move = True

    #put resolution value to 1 for a clear display but it will be too slow
    resolution = 5

    wall_hit=0

    #field of view (FOV)
    fov = 75 # def 60
    half_fov=fov/2

    # change this if you want
    view_angle = 0

    grid_height = 64
    grid_width = 64
    wall_height = 64
    wall_width = 64
    player_height = 32

    player_pos = set_spos( grid )

    draw_line = False
    draw_fog = False
    draw_shadow = False

    #Dimension of the Projection Plane
    projection_plane=[WIDTH, HEIGHT]

    #Center of the Projection Plane
    plane_center=HEIGHT//2 #[WIDTH/2, HEIGHT/2]

    #distance from player to projection plane
    to_plane_dist=int((WIDTH/2)/tan(radians(fov/2)))

    #Angle between subsequent rays
    angle_increment=fov/WIDTH

    #angle of the casted ray
    ray_angle=view_angle+(fov/2)

    # must be int. divisible by const.GRID_WIDTH
    # ms 8 fov 60
    move_speed = 8

    x_move=int(move_speed*cos(radians(view_angle)))
    y_move=-int(move_speed*sin(radians(view_angle)))

    # must be int. divisible by 90
    rotation_speed = 6

    #pygame.key.set_repeat(400, 30)
    pygame.key.set_repeat( 400, 600 )

    timer = 0

    # moving forward;
    # rotating left, right
    # rotating 180 deg
    rotating = [False, False, False, False]
    rotating_check = False

    # 0: distance traveled;
    # 1, 2: degrees rotated
    rotating_deg = [0, 0, 0]

    doors = init_doors( grid )

    eff = False
    facing_door = False

    while True:

        if not rotating[0] and not rotating[1] and not rotating[2] and not rotating[3]:
            rotating_check = False
        else:
            rotating_check = True

        # check for events on the map
        if not rotating_check:

            facing_door = False

            for event in doors:
                if event.check_event(player_pos, view_angle, can_move):
                    facing_door = True
                    break;

            # reveal the map
            map_.reveal( player_pos )


        # controls
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    draw_fog = not draw_fog

                if event.key == pygame.K_2:
                    draw_shadow = not draw_shadow

                if event.key == pygame.K_3:
                    draw_line = not draw_line

        #Movement controls
        keys = pygame.key.get_pressed()

        if not rotating_check:
            if keys[ K_UP ]:
                rotating[0] = True
            elif keys[ K_DOWN ]:
                rotating[3] = True

            if keys[ K_LEFT ]:
                rotating[1] = True
            if keys[ K_RIGHT ]:
                rotating[2] = True

            if keys[ K_RETURN ]:

                for door in doors:

                    if door.active:

                        sc1 = scr.get_screen( screen, WIDTH, HEIGHT )
                        player_pos = door.action( player_pos, view_angle )

                        eff = True
                        break;

            if keys[ K_m ]:
                draw_map = True
            else:
                draw_map = False


        # movement
        if rotating[0]:

            if can_move:
                player_pos[0] += x_move
                player_pos[1] += y_move

            rotating_deg[0] += 1
            if rotating_deg[0] >= (grid_width // move_speed):
                rotating_deg[0] = 0
                rotating[0] = False

        if rotating[1]:

            view_angle += rotation_speed
            if view_angle > 359:
                view_angle -= 360

            x_move = int(move_speed * cos(radians(view_angle)))
            y_move = -int(move_speed * sin(radians(view_angle)))

            rotating_deg[1] += 1
            if rotating_deg[1] >= (90 // rotation_speed):
                rotating_deg[1] = 0
                rotating[1] = False

        if rotating[2]:

            view_angle -= rotation_speed
            if view_angle < 0:
                view_angle += 360

            x_move = int(move_speed * cos(radians(view_angle)))
            y_move = -int(move_speed * sin(radians(view_angle)))

            rotating_deg[2] += 1
            if rotating_deg[2] >= (90 // rotation_speed):
                rotating_deg[2] = 0
                rotating[2] = False

        if rotating[3]:

            view_angle += 2 * rotation_speed
            if view_angle > 359:
                view_angle -= 360

            x_move = int(move_speed * cos(radians(view_angle)))
            y_move = -int(move_speed * sin(radians(view_angle)))

            rotating_deg[1] += 1
            if rotating_deg[1] >= (180 // (2 * rotation_speed)):
                rotating_deg[1] = 0
                rotating[3] = False


        #print(view_angle)
        #print("X: " + str(player_pos[0]) + " Y: " + str(player_pos[1]) + " ANG: " + str(view_angle) + " Moved by: " + str(x_move) + "|" + str(y_move))


        """
        here start raycasting
        """

        screen.fill(( 100, 100, 200 ))
        screen.blit( ground, (0, HEIGHT // 2))

        #angle of the first casted ray
        ray_angle = view_angle + fov / 2


        for x in range(0,WIDTH,resolution):

            if ray_angle < 0:
                ray_angle += 360

            if ray_angle > 359:
                ray_angle -= 360

            if ray_angle == 0:
                ray_angle += 0.01

            #tx and ty used to correct tangent direction
            if ray_angle >= 0 and ray_angle <= 90:
                tx = 1
                ty = -1

            elif ray_angle >= 91 and ray_angle <= 180:
                tx = 1
                ty = 1

            elif ray_angle >= 181 and ray_angle <= 270:
                tx = -1
                ty = 1

            elif ray_angle >= 271 and ray_angle <= 360:
                tx = -1
                ty = -1

            wall_hit = 0
            hor_wall_dist = ver_wall_dist = 100000

            #(y_side)whether ray hit part of the block above the line,or the block below the line
            if ray_angle >= 0 and ray_angle <= 180:
                y_side = -1
                signed_y = -1
            else:
                y_side = grid_height
                signed_y = 1

            #(x_side)whether ray hit left part of the block of the line,or the block right of the line
            if ray_angle >= 90 and ray_angle <= 270:
                x_side = -1
                signed_x = -1
            else:
                x_side = grid_width
                signed_x = 1

            #tangante of the casted ray angle
            tan_angle = tan(radians(ray_angle))

            #first horizontal y step
            y_step = (player_pos[1] // grid_height) * (grid_height) + y_side

            #first horizontal x step (+0.4 to correct wall position)
            x_step = (player_pos[0] + abs(player_pos[1] - y_step) / tan_angle * tx) + 0.4
            ray_x = x_step
            ray_y = y_step
            ray_pos = [int(ray_y // grid_height), int(ray_x // grid_width)]

            #if there is a wall there
            if ray_pos[0] >= 0 and ray_pos[0] < y_limit and  ray_pos[1] >= 0 and ray_pos[1] < x_limit:

                if grid[ray_pos[0]][ray_pos[1]] > 0:

                    wall_texture = grid[ray_pos[0]][ray_pos[1]]

                    #finding distance to horizontal wall
                    hor_wall_dist = int(sqrt((player_pos[0] - ray_x) ** 2 + (player_pos[1] - ray_y) ** 2))
                    wall_hit = 1

                else:

                    #from now horizontal x_step and y_step will remind the same for the rest of the casted ray
                    x_step = (grid_height/tan_angle*tx)
                    y_step = grid_height*signed_y
                    ray_x += x_step
                    ray_y += y_step
                    ray_pos = [int(ray_y//grid_height), int(ray_x//grid_width)]

                    if ray_pos[0] >= 0 and ray_pos[0] < y_limit and ray_pos[1] >= 0 and ray_pos[1] < x_limit:

                        if grid[ray_pos[0]][ray_pos[1]] > 0:

                            #finding distance to horizontal wall
                            wall_texture = grid[ray_pos[0]][ray_pos[1]]
                            hor_wall_dist = int(sqrt((player_pos[0]-ray_x)**2+(player_pos[1]-ray_y)**2))
                            wall_hit=1

                        else:

                            while True:

                                #remember that horizontal x_step and y_step will remind the same for the rest of the casted ray
                                ray_x += x_step
                                ray_y += y_step
                                ray_pos=[int(ray_y//grid_height), int(ray_x//grid_width)]

                                if ray_pos[0] >= 0 and ray_pos[0] < y_limit and ray_pos[1] >= 0 and ray_pos[1] < x_limit:

                                    if grid[ray_pos[0]][ray_pos[1]] > 0:
                                        #finding distance to horizontal wall
                                        wall_texture = grid[ray_pos[0]][ray_pos[1]]
                                        hor_wall_dist = int(sqrt((player_pos[0]-ray_x)**2+(player_pos[1]-ray_y)**2))
                                        wall_hit=1
                                        break
                                else:
                                    break

            hor_wall_pos = ray_x

            #first vertical x step
            x_step = (player_pos[0]//grid_width)*(grid_width)+x_side

            #first vertical y step
            y_step = (player_pos[1]+abs(player_pos[0]-x_step)*tan_angle*ty)
            ray_x = x_step
            ray_y = y_step
            ray_pos = [int(ray_y//grid_height),int(ray_x//grid_width)]

            #if there is a wall there
            if ray_pos[0] >= 0 and ray_pos[0] < y_limit and ray_pos[1] >= 0 and ray_pos[1] < x_limit:

                if grid[ray_pos[0]][ray_pos[1]] > 0:
                    #finding distance to vertical wall
                    wall_texture = grid[ray_pos[0]][ray_pos[1]]
                    ver_wall_dist = int(sqrt((player_pos[0]-ray_x)**2+(player_pos[1]-ray_y)**2))
                    wall_hit=1

                else:
                    #from now verticaal x_step and y_step will remind the same for the rest of the casted ray
                    x_step = grid_width*signed_x
                    y_step = (grid_width*tan_angle*ty)
                    ray_x += x_step
                    ray_y += y_step
                    ray_pos=[int(ray_y//grid_height),int(ray_x//grid_width)]

                    if ray_pos[0] >= 0 and ray_pos[0] < y_limit and ray_pos[1] >= 0 and ray_pos[1] < x_limit:

                        if grid[ray_pos[0]][ray_pos[1]] > 0:
                            #finding distance to vertical wall
                            wall_texture = grid[ray_pos[0]][ray_pos[1]]
                            ver_wall_dist = int(sqrt((player_pos[0]-ray_x)**2+(player_pos[1]-ray_y)**2))
                            wall_hit = 1

                        else:

                            while True:

                                #remember that vertical x_step and y_step will remind the same for the rest of the casted ray
                                ray_x += x_step
                                ray_y += y_step
                                ray_pos = [int(ray_y//grid_height),int(ray_x//grid_width)]

                                if ray_pos[0] >= 0 and ray_pos[0] < y_limit and ray_pos[1] >= 0 and ray_pos[1] < x_limit:

                                    if grid[ray_pos[0]][ray_pos[1]] > 0:
                                        #finding distance to horizontal wall
                                        wall_texture = grid[ray_pos[0]][ray_pos[1]]
                                        ver_wall_dist = int(sqrt((player_pos[0]-ray_x)**2+(player_pos[1]-ray_y)**2))
                                        wall_hit=1
                                        break

                                else:
                                    break

            ver_wall_pos = ray_y


            if wall_hit:

                #chosing the closer distance
                wall_dist = min(hor_wall_dist, ver_wall_dist)

                if wall_dist == hor_wall_dist:
                    wall_side = 1

                elif wall_dist == ver_wall_dist:
                    wall_side = 2

                """
                chosing color for non-textured wall
                if wall_dist==hor_wall_dist:color=WHITE
                elif wall_dist==ver_wall_dist:color=GREY
                """

                #to find the texture position with precision
                if wall_side == 1:
                    wall_pos = int(hor_wall_pos)

                elif wall_side == 2:
                    wall_pos = int(ver_wall_pos)

                #finding the texture position
                texture_pos = int(wall_pos % wall_width)

                #invert the texture position for correction(-0.1 is to avoid error)
                if wall_side == 1 and y_side == grid_height \
                or wall_side == 2 and x_side == -1:
                    texture_pos = int((wall_width-0.1) - texture_pos)

                #beta is the angle of the ray that is being cast relative to the viewing angle
                beta = radians(view_angle - ray_angle)
                cos_beta = cos(beta)

                #removing fish-eye effect
                wall_dist = (wall_dist * cos_beta)


                #Extract the part-column from the texture using the subsurface method:

                # Determine the texture

                # walls
                column = current_texture.subsurface( texture_pos, 0, 1, wall_height )

                # doors
                if wall_texture == 2:
                    column = texture_door.subsurface( texture_pos, 0, 1, wall_height )

                #finding the height of the projected wall slice
                slice_height = int(wall_height / wall_dist * to_plane_dist)

                #Scale it to the height at which we're going to draw it using transform.scale
                if column:
                    try:
                        column = pygame.transform.scale(column, (resolution, slice_height))
                    except:
                        column = pygame.transform.scale(column, (resolution, slice_height // 2))
                    #the top position where the wall slice should be drawn
                    slice_y = plane_center - (slice_height // 2)

                #shading(making shadow or fog)
                # FOG

                # shadow = pygame.Surface((0, 0))
                if draw_fog:
                    alpha = int(wall_dist * 0.25)
                    if alpha > 255:
                        alpha = 255

                    shadow = pygame.Surface((resolution, slice_height)).convert_alpha()
                    shadow.fill((255, 255, 255, alpha))

                #now floor-casting and ceilings
                cos_angle = cos(radians(ray_angle))
                sin_angle = -sin(radians(ray_angle))

                #begining of floor
                wall_bottom = slice_y + slice_height

                #begining of ceilings
                wall_top = slice_y

                while wall_bottom < HEIGHT:

                    wall_bottom += resolution
                    wall_top -= resolution

                    #(row at floor point-row of center)
                    row = wall_bottom - plane_center

                    #straight distance from player to the intersection with the floor
                    straight_p_dist = (player_height / row * to_plane_dist)

                    #true distance from player to floor
                    to_floor_dist = (straight_p_dist / cos_beta)

                    #coordinates (x,y) of the floor
                    ray_x = int(player_pos[0] + (to_floor_dist * cos_angle))
                    ray_y = int(player_pos[1] + (to_floor_dist * sin_angle))

                    #the texture position
                    floor_x = (ray_x % wall_width)
                    floor_y = (ray_y % wall_height)

                    #shading(making shadow or fog)
                    # FLOOR SHADOW
                    # heavy on performance

                    if draw_shadow:
                        alpha2 = int(to_floor_dist * 0.25)
                        if alpha2 > 255:
                            alpha=255

                        shadow2=pygame.Surface((resolution, resolution)).convert_alpha()
                        shadow2.fill((255, 255, 255, alpha2))
                        screen.blit(shadow2, (x, wall_bottom))


                    # the floor, very janky
                    #screen.blit(texture,(x,wall_bottom),(floor_x,floor_y,resolution,resolution))

                    # the ceiling, very janky
                    #screen.blit(texture,(x,wall_top),(floor_x,floor_y,resolution,resolution))

                #drawing everything

                # lines
                if draw_line:
                    pygame.draw.line(screen, WHITE, [x, slice_y], [x,slice_y+slice_height], resolution )

                screen.blit(column, (x, slice_y))

                if draw_fog:
                    screen.blit(shadow, (x, slice_y))

            ray_angle -= angle_increment * resolution


        # show popup if facing a door
        if facing_door:
            if not rotating_check:
                scr.notify_ev( WIDTH, HEIGHT, screen )

        # draw the correct map
        if draw_map:
            map_.draw_full( player_pos, view_angle, screen )
        else:
            map_.draw_mini( player_pos, view_angle, screen )

        # restrict player movement if appropriate
        can_move = True

        try:
            if wall_dist <= 33:
                can_move = False
            else:
                can_move = check_oob( player_pos, view_angle, grid, grid_width )
        except:
            pass;

        #screen.fill(BLUE)
        #screen.blit(ground,(0,HEIGHT // 2))


        # fade in/out when passing through a door
        if eff:
            sc2 = scr.get_screen( screen, WIDTH, HEIGHT )
            scr.fade(sc1, sc2, screen, WIDTH, HEIGHT, clock, FPS)
            eff = False

        # update screen, tick the timer
        try:
            pygame.display.update()
        except:
            pygame.display.flip()

        timer += 1

        clock.tick( FPS )

    return;

raycaster()
