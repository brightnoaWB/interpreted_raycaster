import sys
import pygame
from pygame.locals import *

def get_screen( sc, width, height ):

    # literally take a screenshot

    img = pygame.image.tostring(sc, "RGB")
    img = pygame.image.fromstring(img, (width, height), "RGB").convert()
    return img;


def fade(sc1, sc2, sc, width, height, clock, fps):

    # fade from sc1 to sc2

    bg = pygame.surface.Surface(( width, height ))
    bg.fill(( 0, 0, 0 ))
    bg.set_alpha(0)
    alpha = [True, False, False]
    timer = 0
    sec = fps
    time = sec / 2

    while True:
        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == cont.k_use:
                    return;

        if alpha[0]:
            alpha_val = (255 / time) * timer
            bg.set_alpha(alpha_val)
            if timer == time:
                timer = 0
                alpha[0] = False
                alpha[1] = True

        elif alpha[1]:
            if timer == 5:
                timer = 0
                alpha[1] = False
                alpha[2] = True

        elif alpha[2]:
            alpha_val = 255 - ((255 / time) * timer)
            bg.set_alpha(alpha_val)
            if timer == time:
                return;

        if alpha[0]:
            sc.blit(sc1, (0, 0))
        elif alpha[2]:
            sc.blit(sc2, (0, 0))

        sc.blit(bg, (0, 0))

        try:
            pygame.display.update()
        except:
            pygame.display.flip()

        timer += 1
        clock.tick( fps )

    return;


def notify_ev( width, height, sc ):

    # popup to display when facing a door

    text = "Go Through"
    font = pygame.font.SysFont( "Arial.ttf", 30 )
    text = font.render( text, True, ( 200, 200, 200 ) )

    rect_w = text.get_rect().width + 30
    rect_h = text.get_rect().height + 15

    pos_x = width / 2 - rect_w / 2
    pos_y = 2 * height / 3

    rect = ( pos_x, pos_y, rect_w, rect_h )

    pygame.draw.rect( sc, ( 0, 0, 0 ), rect )

    text_pos_x = pos_x + rect_w / 2 - text.get_rect().width / 2
    text_pos_y = pos_y + text.get_rect().height / 2
    sc.blit( text, ( text_pos_x, text_pos_y ) )

    return;
