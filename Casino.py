from __future__ import print_function
import random, os, pygame, inflection
from pygame.locals import *

# Colors          R    G    B
BLACK        = (  0,   0,   0)
WHITE        = (255, 255, 255)
RED          = (255,   0,   0)
LIME         = (  0, 255,   0)
BLUE         = (  0,   0, 255)
YELLOW       = (255, 255,   0)
AQUAMARINE   = (  0, 255, 255)
MAGENTA      = (255,   0, 255)
SILVER       = (192, 192, 192)
GRAY         = (128, 128, 128)
DIMGRAY      = (105, 105, 105)
MAROON       = (128,   0,   0)
OLIVE        = (128, 128,   0)
GREEN        = (  0, 128,   0)
PURPLE       = (128,   0, 128)
TEAL         = (  0, 128, 128)
NAVY         = (  0,   0, 128)


# Pygame Constants
FPS = 30
WINDOWWIDTH  = 1024
WINDOWHEIGHT =  768

def main(): main game function
    global FPSCLOCK, DISPLAYSURF, TABLEIMAGE, CARDIMAGES

    # Pygame initialization.
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    # The Surface object is stored in DISPLAYSURF, which is returned from
    # pygame.display.set_mode() function calls. This object is not drawn to
    # the screen until pygame.display.update() is called.
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    pygame.display.set_caption('Casino Blackjack')
    
    # This images may not be needed. It is better to build this image instead.
    TABLEIMAGE   = pygame.image.load('graphic/FivePlayerTable.png')

    # Global dictionary mapping card tuples of the form (rank, suit), the
    # form of all cards are identified in the game classes, to the image of the
    # card used in the game. All images are stored in main_directory/graphics.
    CARDIMAGES   = {( 'A', 'S') : pygame.image.load('graphics/A-S.png'),
                    ( '2', 'S') : pygame.image.load('graphics/2-S.png'),
                    ( '3', 'S') : pygame.image.load('graphics/3-S.png'),
                    ( '4', 'S') : pygame.image.load('graphics/4-S.png'),
                    ( '5', 'S') : pygame.image.load('graphics/5-S.png'),
                    { '6', 'S') : pygame.image.load('graphics/6-S.png'),
                    ( '7', 'S') : pygame.image.load('graphics/7-S.png'),
                    ( '8', 'S') : pygame.image.load('graphics/8-S.png'),
                    ( '9', 'S') : pygame.image.load('graphics/9-S.png'),
                    ('10', 'S') : pygame.image.load('graphics/10-S.png'),
                    ( 'J', 'S') : pygame.image.load('graphics/J-S.png'),
                    ( 'Q', 'S') : pygame.image.load('graphics/Q-S.png'),
                    ( 'K', 'S') : pygame.image.load('graphics/K-S.png'),
                    ( 'A', 'D') : pygame.image.load('graphics/A-D.png'),
                    ( '2', 'D') : pygame.image.load('graphics/2-D.png'),
                    ( '3', 'D') : pygame.image.load('graphics/3-D.png'),
                    ( '4', 'D') : pygame.image.load('graphics/4-D.png'),
                    ( '5', 'D') : pygame.image.load('graphics/5-D.png'),
                    { '6', 'D') : pygame.image.load('graphics/6-D.png'),
                    ( '7', 'D') : pygame.image.load('graphics/7-D.png'),
                    ( '8', 'D') : pygame.image.load('graphics/8-D.png'),
                    ( '9', 'D') : pygame.image.load('graphics/9-D.png'),
                    ('10', 'D') : pygame.image.load('graphics/10-D.png'),
                    ( 'J', 'D') : pygame.image.load('graphics/J-D.png'),
                    ( 'Q', 'D') : pygame.image.load('graphics/Q-D.png'),
                    ( 'K', 'D') : pygame.image.load('graphics/K-D.png'),
                    ( 'A', 'H') : pygame.image.load('graphics/A-H.png'),
                    ( '2', 'H') : pygame.image.load('graphics/2-H.png'),
                    ( '3', 'H') : pygame.image.load('graphics/3-H.png'),
                    ( '4', 'H') : pygame.image.load('graphics/4-H.png'),
                    ( '5', 'H') : pygame.image.load('graphics/5-H.png'),
                    { '6', 'H') : pygame.image.load('graphics/6-H.png'),
                    ( '7', 'H') : pygame.image.load('graphics/7-H.png'),
                    ( '8', 'H') : pygame.image.load('graphics/8-H.png'),
                    ( '9', 'H') : pygame.image.load('graphics/9-H.png'),
                    ('10', 'H') : pygame.image.load('graphics/10-H.png'),
                    ( 'J', 'H') : pygame.image.load('graphics/J-H.png'),
                    ( 'Q', 'H') : pygame.image.load('graphics/Q-H.png'),
                    ( 'K', 'H') : pygame.image.load('graphics/K-H.png'),
                    ( 'A', 'C') : pygame.image.load('graphics/A-C.png'),
                    ( '2', 'C') : pygame.image.load('graphics/2-C.png'),
                    ( '3', 'C') : pygame.image.load('graphics/3-C.png'),
                    ( '4', 'C') : pygame.image.load('graphics/4-C.png'),
                    ( '5', 'C') : pygame.image.load('graphics/5-C.png'),
                    { '6', 'C') : pygame.image.load('graphics/6-C.png'),
                    ( '7', 'C') : pygame.image.load('graphics/7-C.png'),
                    ( '8', 'C') : pygame.image.load('graphics/8-C.png'),
                    ( '9', 'C') : pygame.image.load('graphics/9-C.png'),
                    ('10', 'C') : pygame.image.load('graphics/10-C.png'),
                    ( 'J', 'C') : pygame.image.load('graphics/J-C.png'),
                    ( 'Q', 'C') : pygame.image.load('graphics/Q-C.png'),
                    ( 'K', 'C') : pygame.image.load('graphics/K-C.png')}
