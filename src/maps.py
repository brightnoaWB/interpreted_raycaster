import pygame
from pygame.locals import *

import os, os.path

#
## Color codes
#
cl_wall = ( 255, 100, 0 )
cl_floor = ( 150, 200, 50 )
cl_door = ( 100, 100, 200 )

#####

def rot_center(image, angle):

    #rotate an image while keeping its center and size

    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()

    return rot_image;

class Map( object ):

    def __init__( self, grid, win_width, win_height ):

        self.grid = grid
        self.grid_vis = [  ]

        for y in range( len( self.grid ) ):
            buffer_list = list(  )

            for x in range( len( self.grid[ 0 ] ) ):
                buffer_list.append( -1 )

            self.grid_vis.append( buffer_list )

        self.w = 150
        self.mini_cont = pygame.Rect((  win_width - self.w - 15,   \
                                        15,                              \
                                        self.w,                                             \
                                        self.w                                              ))
        self.slot_w = self.w / 5

        self.w_full = win_height - 50
        self.full_cont = pygame.Rect((  win_width / 2 - self.w_full / 2,  \
                                        25,                  \
                                        self.w_full,                            \
                                        self.w_full                             ))

        self.slot_w_full = self.w_full / max( len(self.grid), len( self.grid[ 0 ] ) )


        size_m = ( int( self.slot_w ), int( self.slot_w ) )
        size_f = ( int( self.slot_w_full ), int( self.slot_w_full ) )

        self.arrow = pygame.image.load( "map_arrow.png" )

        size = int( 4 * self.slot_w / 5 )
        self.arrow_mini = pygame.transform.scale( self.arrow, ( size, size ) )
        self.arrow_mini_c = self.arrow_mini.get_rect().center

        size = int( 4 * self.slot_w_full / 5 )
        self.arrow_full = pygame.transform.scale( self.arrow, ( size, size ) )
        self.arrow_full_c = self.arrow_full.get_rect().center


        self.door = pygame.image.load( "map_door.png" )
        self.door_mini = pygame.transform.scale( self.door, size_m )
        self.door_full = pygame.transform.scale( self.door, size_f )


    def reveal(self, pl_pos):

        x = ((pl_pos[0] - 64 // 2) // 64)
        y = ((pl_pos[1] - 64 // 2) // 64)

        for i in range(3):
            x_1 = x - 1 + i
            for j in range(3):
                y_1 = y - 1 + j
                try:
                    self.grid_vis[y_1][x_1] = self.grid[y_1][x_1]
                except:
                    pass;


    def draw_mini(self, pl_pos, v_ang, sc):

        x = (pl_pos[0] - 64 // 2) // 64
        y = (pl_pos[1] - 64 // 2) // 64

        arrow = rot_center(self.arrow_mini, v_ang)
        blit_arrow = False
        elem = -1

        for i in range(5):
            x_1 = x - 2 + i

            for j in range(5):
                y_1 = y - 2 + j

                rect = pygame.Rect((    self.mini_cont.x + i * self.slot_w, \
                                        self.mini_cont.y + j * self.slot_w, \
                                        self.slot_w,                        \
                                        self.slot_w                         ))


                cl = ( 0, 0, 0 )

                if x_1 >= 0 and x_1 < len(self.grid[0]):
                    if y_1 >= 0 and y_1 < len(self.grid):

                        val = self.grid_vis[y_1][x_1]
                        elem = -1

                        if val == -1:
                            cl = ( 0, 0, 0 )

                        elif val == 0 or val == -2:
                            cl = cl_floor

                        elif val == 1:
                            cl = cl_wall

                        elif val == 2:
                            cl = cl_door
                            elem = self.door_mini

                        blit_arrow = False
                        if x_1 == x:
                            if y_1 == y:
                                blit_arrow = True

                pygame.draw.rect( sc, cl, rect )

                if not isinstance( elem, int ):
                    if cl != ( 0, 0, 0 ):
                        sc.blit( elem, ( rect.x, rect.y ) )

                if blit_arrow:
                    arrow_x = self.mini_cont.x + i * self.slot_w + self.slot_w / 2 - arrow.get_rect().width / 2
                    arrow_y = self.mini_cont.y + j * self.slot_w + self.slot_w / 2 - arrow.get_rect().height / 2
                    sc.blit( arrow, ( arrow_x, arrow_y ) )

        return;


    def draw_full(self, pl_pos, v_ang, sc):

        x = (pl_pos[0] - 64 // 2) // 64
        y = (pl_pos[1] - 64 // 2) // 64

        iter_x = len( self.grid[ 0 ] )
        iter_y = len( self.grid )

        arrow = rot_center(self.arrow_full, v_ang)
        blit_arrow = False

        for i in range(iter_x):

            for j in range(iter_y):

                rect = pygame.Rect((    self.full_cont.x + i * self.slot_w_full, \
                                        self.full_cont.y + j * self.slot_w_full, \
                                        self.slot_w_full,                        \
                                        self.slot_w_full                         ))


                cl = ( 0, 0, 0 )
                elem = -1

                val = self.grid_vis[j][i]

                if val == -1:
                    cl = ( 0, 0, 0 )

                elif val == 0 or val == -2:
                    cl = cl_floor

                elif val == 1:
                    cl = cl_wall

                elif val == 2:
                    cl = cl_door
                    elem = self.door_full

                blit_arrow = False
                if i == x:
                    if j == y:
                        blit_arrow = True

                pygame.draw.rect( sc, cl, rect )

                if not isinstance( elem, int ):
                    sc.blit( elem, ( rect.x, rect.y ) )

                if blit_arrow:
                    arrow_x = self.full_cont.x + i * self.slot_w_full + self.slot_w_full / 2 - arrow.get_rect().width / 2
                    arrow_y = self.full_cont.y + j * self.slot_w_full + self.slot_w_full / 2 - arrow.get_rect().height / 2
                    sc.blit(arrow, ( arrow_x, arrow_y ) )

        return;

