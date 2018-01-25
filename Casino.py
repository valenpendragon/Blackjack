from __future__ import print_function

import collections
import copy
import os
import pdb
import random
import string
import sys

from lib import CardShoe, CasinoTable, Dealer, Player, Textbox

import inflection
import pygame
from pygame.locals import *
from pygame.transform import scale

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
PERU         = (205, 133,  63)
SADDLEBROWN  = (139,  69,  19)

BGCOLOR   = DIMGRAY
TEXTCOLOR = WHITE
ELIMINATIONCOLOR   = RED
ELIMINATIONBGCOLOR = WHITE
BUTTONOUTLINE   = BLACK
BUTTONTEXTCOLOR = BLACK

# Pygame Constants. All of these values are in pixels
FPS = 30
WINDOWWIDTH        = 1024  # Width of game window
WINDOWHEIGHT       =  768  # Height of game window
WINCENTERX         = int(WINDOWWIDTH / 2)    # X coordinate of window's center
WINCENTERY         = int(WINDOWHEIGHT / 2)   # Y coordinate of winwow's center
CARDWIDTH          =   30  # Width of a card image
CARDSPACING        =    4  # Spacing between cards (both axes)
CARDHEIGHT         =   60  # Height of a card image
LINESPACING12      =   15  # Spacing between 12pt text Rect objects
LINESPACING18      =   25  # Spacing between 18pt text Rect objects
TABLEWIDTH         =  700  # width of playing table
TABLEHEIGHT        =  400  # height of playing table
TABLERIM           =   40  # width of band around table
STATIONWIDTH       =  250  # width of dealer's station
STATIONHEIGHT      =   60  # height of dealer's station
MAXPLAYERS         =    3  # board space limits players to 3
SCOREWIDTH         =  200  # width of all players' score text
BUTTONWIDTH        =  100  # width of action buttons
BUTTONHEIGHT       =   50  # height of action buttons
BUTTONSPACING      =   75  # Spacing between action buttons
OUTLINEWIDTH       =    5  # width of the outlines of butttons
STATUSBLOCKWIDTH   =  400  # width of the status block (upper left corner)
STATUSBLOCKHEIGHT  =  145  # height of the status block (upper left corner)
PHASEBLOCKWIDTH    =  100  # width of round phase block (upper right corner)
PHASEBLOCKHEIGHT   =  100  # height of round phase block (upper right corner)


# These four items are the edges of printable area in game window.
LEFTMARGIN    =   10                    
RIGHTMARGIN   = WINDOWWIDTH - LEFTMARGIN
TOPMARGIN     =   10
BOTTOMMARGIN  = WINDOWHEIGHT - TOPMARGIN

# These three constants define the printable area for the players on the casino
# table. A player's regular hand will appear along these margins. The split
# hand will appear above it.
TABLELEFTMARGIN   = WINCENTERX - int(TABLEWIDTH / 2) + (TABLERIM + CARDWIDTH)
TABLEBOTTOMMARGIN = WINCENTERY + int(TABLEHEIGHT / 2) - (TABLERIM + CARDWIDTH)
TABLERIGHTMARGIN  = WINCENTERX + int(TABLEWIDTH / 2) - (TABLERIM + CARDWIDTH)

# This constant adjusts the position of player output in the center of the
# table.
CENTEROUTPUT  =  100

# Y position in front of dealer's where Dealer's cards are dealt. Orignally,
# This was a flat value, but now, it needs to be a formula that adjusts for
# size of the table and the station itself. It is adjusted from the center
# of the table. Half the table height gets it to the edge of the table. Next,
# we adjust for half the height of the station itself.
# These two constants control where the Dealer's station prints and where the
# dealer's cards are printed relative to it. The Y coordinate of the top
# of the station uses a formula of adjustments to get it centered on the edge
# of the table, regardless of shape. The X coordinate of the left edge is
# half the length of the station from the center line of the table.
# DEALERSCARDS is adjusted to a distance of CARDSPACING below the station.
DEALERSTATIONTOP  = WINCENTERY - int(TABLEHEIGHT / 2) - int(STATIONHEIGHT / 2)
DEALERSTATIONLEFT = WINCENTERX - int(STATIONWIDTH / 2)
DEALERSCARDS      = DEALERSTATIONTOP + STATIONHEIGHT + CARDSPACING

# This tuple is used to find take the highest skill level of the user's
# players and generate a tuple of the tables at which they will allowed to
# play in the game. The number of rounds a player must complete at a table
# of their current skill level to increase it below that.
SKILLS  = ('starter', 'normal', 'special', 'high')
STARTER = 50
NORMAL  = 75
SPECIAL = 100


# Bank for 'starter' players
STARTINGBANK = 50000

# This is the number of milliseconds that the game pauses as it scrolls
# instruction text on screen.
SCROLLSPEED = 1200

# These positions get used so often, it is necessary to have a couple of handy
# constants for them.
TABLESEATS    = ('left', 'middle', 'right')
TABLESEATSALL = ('left', 'middle', 'right', 'dealer')
# This tuple stores all of the keys used in the Table object dictionary
# attribute results (tableObj.results). This is used in the dealer's turn
# to iterate through all of the possible hand options.
HANDLIST = ('left reg', 'left split', 'middle reg', 'middle split', 'right reg', 'right split', 'dealer reg')


def main(): # main game function
    global FPSCLOCK, DISPLAYSURF, CARDIMAGES, BLANKCARD, BASICFONT, SCOREFONT
    global DATAFONT, INSTRUCTFONT, PROMPTFONT
    global listPlayers, listDealers, tableChoice, tableObj

    # Pygame initialization.
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    # The Surface object is stored in DISPLAYSURF, which is returned from
    # pygame.display.set_mode() function calls. This object is not drawn to
    # the screen until pygame.display.update() is called.
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    pygame.display.set_caption('Casino Blackjack')
    DISPLAYSURF.fill(BGCOLOR)

    # The next stanza sets the default text font for the game to GNU Free Serif
    # TTF. If it is not found in etc, it defaults to freesansbold.ttf which is
    # part of Pygame. 12pt and 14pt fonts use LINESPACING12 to separate lines.
    try:
        BASICFONT = pygame.font.Font('etc/FreeSerif.ttf', 12)
    except:
        # FreeSans.ttf could not be found or could not be used.
        BASICFONT = pygame.font.Font('freesansbold.ttf', 12)        

    # The next stanza sets the SCOREFONT for the game to GNU Free Serif Italics
    # TTF. If it is not found in etc, it defaults to freesansbold.ttf which is
    # part of Pygame. 12pt and 14pt fonts use LINESPACING12 to separate lines.
    try:
        SCOREFONT = pygame.font.Font('etc/FreeSerifItalic.ttf', 12)
    except:
        # FreeSerif.ttf could not be found or could not be used.
        SCOREFONT = pygame.font.Font('freesansbold.ttf', 12)
    
    # The next stanza sets the DATAFONT for the game to GNU Free Monotype TTF.
    # If it is not found in etc, it defaults to freesansbold.ttf which is
    # part of Pygame. 12pt and 14pt fonts use LINESPACING12 to separate lines.
    try:
        DATAFONT = pygame.font.Font('etc/FreeMono.ttf', 14)
    except:
        # FreeMono.ttf could not be found or could not be used.
        DATAFONT = pygame.font.Font('freesansbold.ttf', 14)        

    # The next stanza sets INSTRUCTFONT, used for instructions. It is an
    # 18pt font instead of a 12pt or 14pt font. It is setup the same way
    # as the previous fonts. It uses LINESPACING18 for specing.
    try:
        INSTRUCTFONT = pygame.font.Font('etc/FreeSerifBold.ttf', 18)
    except:
        # FreeMonoBold.ttf could not be found or could not be used.
        INSTRUCTFONT = pygame.font.Font('freesansbold.ttf', 18)

    # The next stanza sets PROMPTFONT, which is used for Textbox prompts. It is
    # a 14pt font. It uses LINESPACING18 for specing.
    try:
        PROMPTFONT = pygame.font.Font('etc/FreeSerif.ttf', 14)
    except:
        # FreeMonoBold.ttf could not be found or could not be used.
        PROMPTFONT = pygame.font.Font('freesansbold.ttf', 14)

    # Next, we need to build the BLANKCARD and CARDIMAGES dictionaries.
    # We need to initialize the dictionaries that store card images and
    # their respecitive surfaces. The first is BLANKCARD, a single layer dict
    # object that contains the mapping as follows:
    # 'image    : loaded graphics file of a blank card
    # 'surface' : a surface object made from the file and scaled to 45x70
    #             pixels
    # 'rect'    : a rect object large enough to display the Surface object
    #
    # CARDIMAGES is a two layer nested ordered dictionary. The first layer maps
    # a card, a tuple of (rank, suit) generated by CardShoe class, to a nested
    # dictionary that maps the following items together with the card:
    # (card) --> {'image'        : loaded graphics file of the tuple (card)
    #             'scaled image' : image scaled to card width/height
    #             'surface'      : a surface object created from the scaled
    #                              scaled image
    #             'rect'         : a rect object large enough to display the
    #                              Surface object}
    # BLANKCARD is the simpler process, but it lays out the steps in building
    # the full nested dictionary, CARDIMAGES.
    BLANKCARD = {}
    BLANKCARD['image']     = pygame.image.load('graphics/Blank.png')
    BLANKCARD['surface']   = BLANKCARD['image'].convert()
    BLANKCARD['rect']      = BLANKCARD['surface'].get_rect()
    BLANKCARD['rect']      = BLANKCARD['rect'].inflate(CARDWIDTH, CARDHEIGHT)
    
    # The first step to import the images and map them to their respective
    # 'cards'. The rest can be done with a iterables. Note: CARDIMAGES is an
    # ordered dict since that makes it easier to test changes. It also puts
    # all of the cards in order for diagnostic printouts

    CARDIMAGES   = collections.OrderedDict()
    CARDIMAGES[( 'A', 'S')] = { 'image' : pygame.image.load('graphics/A-S.png') }
    CARDIMAGES[( '2', 'S')] = { 'image' : pygame.image.load('graphics/2-S.png') }
    CARDIMAGES[( '3', 'S')] = { 'image' : pygame.image.load('graphics/3-S.png') }
    CARDIMAGES[( '4', 'S')] = { 'image' : pygame.image.load('graphics/4-S.png') }
    CARDIMAGES[( '5', 'S')] = { 'image' : pygame.image.load('graphics/5-S.png') }
    CARDIMAGES[( '6', 'S')] = { 'image' : pygame.image.load('graphics/6-S.png') }
    CARDIMAGES[( '7', 'S')] = { 'image' : pygame.image.load('graphics/7-S.png') }
    CARDIMAGES[( '8', 'S')] = { 'image' : pygame.image.load('graphics/8-S.png') }
    CARDIMAGES[( '9', 'S')] = { 'image' : pygame.image.load('graphics/9-S.png') }
    CARDIMAGES[('10', 'S')] = { 'image' : pygame.image.load('graphics/10-S.png') }
    CARDIMAGES[( 'J', 'S')] = { 'image' : pygame.image.load('graphics/J-S.png') }
    CARDIMAGES[( 'Q', 'S')] = { 'image' : pygame.image.load('graphics/Q-S.png') }
    CARDIMAGES[( 'K', 'S')] = { 'image' : pygame.image.load('graphics/K-S.png') }
    CARDIMAGES[( 'A', 'D')] = { 'image' : pygame.image.load('graphics/A-D.png') }
    CARDIMAGES[( '2', 'D')] = { 'image' : pygame.image.load('graphics/2-D.png') }
    CARDIMAGES[( '3', 'D')] = { 'image' : pygame.image.load('graphics/3-D.png') }
    CARDIMAGES[( '4', 'D')] = { 'image' : pygame.image.load('graphics/4-D.png') }
    CARDIMAGES[( '5', 'D')] = { 'image' : pygame.image.load('graphics/5-D.png') }
    CARDIMAGES[( '6', 'D')] = { 'image' : pygame.image.load('graphics/6-D.png') }
    CARDIMAGES[( '7', 'D')] = { 'image' : pygame.image.load('graphics/7-D.png') }
    CARDIMAGES[( '8', 'D')] = { 'image' : pygame.image.load('graphics/8-D.png') }
    CARDIMAGES[( '9', 'D')] = { 'image' : pygame.image.load('graphics/9-D.png') }
    CARDIMAGES[('10', 'D')] = { 'image' : pygame.image.load('graphics/10-D.png') }
    CARDIMAGES[( 'J', 'D')] = { 'image' : pygame.image.load('graphics/J-D.png') }
    CARDIMAGES[( 'Q', 'D')] = { 'image' : pygame.image.load('graphics/Q-D.png') }
    CARDIMAGES[( 'K', 'D')] = { 'image' : pygame.image.load('graphics/K-D.png') }
    CARDIMAGES[( 'A', 'H')] = { 'image' : pygame.image.load('graphics/A-H.png') }
    CARDIMAGES[( '2', 'H')] = { 'image' : pygame.image.load('graphics/2-H.png') }
    CARDIMAGES[( '3', 'H')] = { 'image' : pygame.image.load('graphics/3-H.png') }
    CARDIMAGES[( '4', 'H')] = { 'image' : pygame.image.load('graphics/4-H.png') }
    CARDIMAGES[( '5', 'H')] = { 'image' : pygame.image.load('graphics/5-H.png') }
    CARDIMAGES[( '6', 'H')] = { 'image' : pygame.image.load('graphics/6-H.png') }
    CARDIMAGES[( '7', 'H')] = { 'image' : pygame.image.load('graphics/7-H.png') }
    CARDIMAGES[( '8', 'H')] = { 'image' : pygame.image.load('graphics/8-H.png') }
    CARDIMAGES[( '9', 'H')] = { 'image' : pygame.image.load('graphics/9-H.png') }
    CARDIMAGES[('10', 'H')] = { 'image' : pygame.image.load('graphics/10-H.png') }
    CARDIMAGES[( 'J', 'H')] = { 'image' : pygame.image.load('graphics/J-H.png') }
    CARDIMAGES[( 'Q', 'H')] = { 'image' : pygame.image.load('graphics/Q-H.png') }
    CARDIMAGES[( 'K', 'H')] = { 'image' : pygame.image.load('graphics/K-H.png') }
    CARDIMAGES[( 'A', 'C')] = { 'image' : pygame.image.load('graphics/A-C.png') }
    CARDIMAGES[( '2', 'C')] = { 'image' : pygame.image.load('graphics/2-C.png') }
    CARDIMAGES[( '3', 'C')] = { 'image' : pygame.image.load('graphics/3-C.png') }
    CARDIMAGES[( '4', 'C')] = { 'image' : pygame.image.load('graphics/4-C.png') }
    CARDIMAGES[( '5', 'C')] = { 'image' : pygame.image.load('graphics/5-C.png') }
    CARDIMAGES[( '6', 'C')] = { 'image' : pygame.image.load('graphics/6-C.png') }
    CARDIMAGES[( '7', 'C')] = { 'image' : pygame.image.load('graphics/7-C.png') }
    CARDIMAGES[( '8', 'C')] = { 'image' : pygame.image.load('graphics/8-C.png') }
    CARDIMAGES[( '9', 'C')] = { 'image' : pygame.image.load('graphics/9-C.png') }
    CARDIMAGES[('10', 'C')] = { 'image' : pygame.image.load('graphics/10-C.png') }
    CARDIMAGES[( 'J', 'C')] = { 'image' : pygame.image.load('graphics/J-C.png') }
    CARDIMAGES[( 'Q', 'C')] = { 'image' : pygame.image.load('graphics/Q-C.png') }
    CARDIMAGES[( 'K', 'C')] = { 'image' : pygame.image.load('graphics/K-C.png') }
    # Step two is to iterate through the cards (dict keys) and create the
    # surfaces and rects we need to display the cards on screen. The inflate()
    # method ensures all cards are the same size.
    for card in CARDIMAGES.iterkeys():
        tempSurf = CARDIMAGES[card]['image'].convert()
        CARDIMAGES[card]['scaled image'] = pygame.transform.scale(CARDIMAGES[card]['image'], (CARDWIDTH, CARDHEIGHT))
        CARDIMAGES[card]['surface'] = CARDIMAGES[card]['scaled image'].convert()
        CARDIMAGES[card]['rect']    = CARDIMAGES[card]['surface'].get_rect()
    # Diagnostic print to see if these cards were setup correctly.
    # cardImagesDiagnosticPrint()
    # print("main: CARDIMAGES = {}.".format(CARDIMAGES))
    # pressSpaceToContinue()

    listDealers = generateDealerList()

    # Now, we need to see if a saved game exists. If so, it will import it
    # into listPlayers, a list of player objects. Players include a name
    # ranking (starter, normal, special event, or high roller. If there are
    # no saved game(s), we call the function that creates new players.
    # If creating players fails, then the game bails out.
    listPlayers = []
    tempListPlayers = findPlayers()
    if tempListPlayers != None:
        listPlayers = copy.deepcopy(tempListPlayers)
    if listPlayers == []:
        print("main: No saved data could be found.")
        createPlayers()
        if listPlayers == []:
            terminate()

    # print("main: Player list is {}".format(listPlayers))
    # Now, we need to creat a list of the highest level of table that at
    # which the user's players may play Blackjack at the Casino. The order
    # of the skill levels is starter ---> normal ---> special event ---> high
    # roller.
    tablesPermitted = getTableSkillList(listPlayers)
    # print("main: tablePermitted set to {}".format(tablesPermitted))
    listDealers = filterDealers(tablesPermitted, listDealers)
    # print("main: Dealer list after filtering: {}".format(listDealers))
    
    # Initialize tableChoice and call offerTableChoice to get the user's
    # choice of dealer. The while loop ensures we actually get a name that
    # matches a dealer. Capitalization does not matter.
    tableChoice = {}
    print("main: tableChoice is {0}".format(tableChoice))
    while tableChoice == {}:
        offerTableChoices(listDealers)
        print("main: tableChoice is {0}".format(tableChoice))
        # Now, we need to look at the Dealer the user chose. If the ante is
        # too high for at least one of the players, we need to warn them
        # that the player(s) must be removed or face elimination as the game
        # starts up. Then, we give them an option to reconsider.
        # Clear the screen:
        DISPLAYSURF.fill(BLACK)
        pygame.display.update()
        posX = LEFTMARGIN
        posY = WINCENTERY
        if tableChoice == {}:
            # The player hit enter with an invalid dealer's name.
            instText = "Dealer's name was not a valid choice. Please try again."
            instSurf = INSTRUCTFONT.render(instText, True, TEXTCOLOR)
            instRect = instSurf.get_rect(center = (WINCENTERX, WINCENTERY))
            DISPLAYSURF.fill(BLACK)
            DISPLAYSURF.blit(instSurf, instRect)
            pressSpaceToContinue()
        else: # Player picked a valid choice.
            # tableProblems is a counter of the list of problems found after
            # checking the player banks against the table minimum ante.
            tableProblems = 0
            tableMin = tableChoice['table bets'][0]
            for i in range(0, len(listPlayers)):
                playerName = listPlayers[i]['name']
                playerBank = listPlayers[i]['bank']
                dealerName = tableChoice['name']
                if playerBank < tableMin:
                    tableProblems += 1
                    warningTextFirst  = "{0} cannot meet the table minimum of {1} to ante up.".format(playerName, tableMin)
                    warningTextSecond = "This player should be withdrawn to prevent elimination."
                    warningSurfFirst  = INSTRUCTFONT.render(warningTextFirst, True, TEXTCOLOR)
                    warningSurfSecond = INSTRUCTFONT.render(warningTextSecond, True, TEXTCOLOR)
                    warningRectFirst  = warningSurfFirst.get_rect(topleft = (posX, posY))
                    posY += LINESPACING18
                    warningRectSecond = warningSurfSecond.get_rect(topleft = (posX, posY))
                    posY += LINESPACING18
                    DISPLAYSURF.blit(warningSurfFirst, warningRectFirst)
                    DISPLAYSURF.blit(warningSurfSecond, warningRectSecond)
                    pygame.display.update()
                else:
                    # Being able to survive at least 4 rounds with a player
                    # is kind of what I would consider a minimum number of
                    # turns at a particular level of skill, considering how
                    # slanted the blackjack rules are (in favor of the house).
                    # So, we need test that number next and warn the user
                    # that the player might not survive very long.
                    # Reset this counter between iterations.
                    playerSurvival = 0
                    while (playerSurvival <= 5) and (playerSurvival * tableMin < playerBank):
                        playerSurvival += 1
                    if playerSurvival <= 5:
                        # The player won't last long at the current ante level.
                        tableProblems += 1
                        warningTextFirst  = "Given the table minimum of {0}, {1} can avoid".format(tableMin, playerName)
                        warningTextSecond = "elimination about {0} rounds at minimum bets.".format(playerSurvival)
                        warningTextThird  = "Withdrawing this player early is likely to prevent elimination."
                        warningSurfFirst  = INSTRUCTFONT.render(warningTextFirst, True, TEXTCOLOR)
                        warningSurfSecond = INSTRUCTFONT.render(warningTextSecond, True, TEXTCOLOR)
                        warningSurfThird  = INSTRUCTFONT.render(warningTextThird, True, TEXTCOLOR)
                        warningRectFirst  = warningSurfFirst.get_rect(topleft = (posX, posY))
                        posY += LINESPACING18
                        warningRectSecond = warningSurfSecond.get_rect(topleft = (posX, posY))
                        posY += LINESPACING18
                        warningRectThird  = warningSurfThird.get_rect(topleft = (posX, posY))
                        posY += LINESPACING18
                        DISPLAYSURF.blit(warningSurfFirst, warningRectFirst)
                        DISPLAYSURF.blit(warningSurfSecond, warningRectSecond)
                        DISPLAYSURF.blit(warningSurfThird, warningRectThird)
                        pygame.display.update()
            
            if tableProblems != 0:
                # There were some serious problems with the dealer choice.
                promptTextFirst  = "Given these problems, are you sure you want to"
                promptTextSecond = "pick {0} as your dealer?".format(dealerName)
                promptSurfFirst  = INSTRUCTFONT.render(promptTextFirst, True, TEXTCOLOR)
                promptSurfSecond = INSTRUCTFONT.render(promptTextSecond, True, TEXTCOLOR)
                promptRectFirst  = promptSurfFirst.get_rect(topleft = (posX, posY))
                posY += LINESPACING18
                promptRectSecond = promptSurfSecond.get_rect(topleft = (posX, posY))
                posY += LINESPACING18
                DISPLAYSURF.blit(promptSurfFirst, promptRectFirst)
                DISPLAYSURF.blit(promptSurfSecond, promptRectSecond)
                pygame.display.update()
                answer = checkForYesNo(posX, posY, 'topleft')
                if answer == True:
                    # The user still wants to move ahead with this choice.
                    break
                else:
                    # The user decided to pick another choice after all.
                    tableChoice = {}                

    # Now, we need to generate a CasinoTable object. This object needs to be
    # populated from listPlayers and tableChoice. Note, 'table bets' is the
    # key to a tuple (min_bet, max_bet).
    tableObj = CasinoTable(listPlayers,
                           tableChoice['blackjack multiplier'],
                           tableChoice['name'],
                           tableChoice['bank'],
                           tableChoice['table bets'][0],
                           tableChoice['table bets'][1])
    print("main: Table min is ${0}. Table max is ${1}.".format(tableObj.min_bet, tableObj.max_bet))

    # Note: The following turn controls are also initialized with tableObj:
    # tableObj.phase: string indicating the current phase of the round of
    #       play. There are several values. This is a global variable.
    #           'pregame' : indicates that the game has not started.
    #           'start'   : allows the user to withdraw players before ante
    #           'ante'    : collecting initial bets from players
    #           'deal'    : dealing the cards, split hands and insurance bets
    #           'raise'   : option to raise bets
    #           'left'    : left player's turn (must be one)
    #           'middle'  : middle player's turn (if there is one)
    #           'right'   : right player's turn (if there is one)
    #           'dealer'  : dealer's turn
    #           'end'     : end of the current round (clean up phase)
    #           'postgame': ends the current game.
    # tableObj.seat: string indicating the seat of the player, used to
    #       indicate which player turn it is and as a dictionary key to get
    #       player data out of the tableObj.player dictionary. Valid values
    #       are None, 'left', 'middle', or 'right'.
    # Out of __init__, phase = 'pregame' and seat = None
    playBlackjack()
    # main

def terminate():
    """
    This function ends the game, closing pygame and exiting to the system.
    It has no inputs or outputs.
    """
    pygame.quit()
    sys.exit()

def cardImagesDiagnosticPrint(adjX=0, adjY=0):
    """
    This function prints out all 52 cards to verify spacing and apperance.
    INPUT: optional posX and posY adjustments, defaults are 30 (LINESPACING12)
    OUTPUT: None
    """
    DISPLAYSURF.fill(BGCOLOR)
    posX = int(3 * (CARDSPACING + CARDWIDTH) / 2) + adjX
    posY = CARDHEIGHT + CARDSPACING + adjY
    for card in CARDIMAGES.iterkeys():
        rank, suit = card
        if rank == 'A':
            posX  = int(3 * (CARDSPACING + CARDWIDTH) / 2) + adjX
            posY += CARDHEIGHT + CARDSPACING + adjY
        CARDIMAGES[card]['rect'].center = (posX, posY)
        DISPLAYSURF.blit(CARDIMAGES[card]['surface'], CARDIMAGES[card]['rect'])
        posX += CARDWIDTH + CARDSPACING
        pygame.display.update()
        FPSCLOCK.tick()

def diagnosticPrint(tableObj, output = ''):
    """
    This function checks for and prints out the following objects classes:
        CasinoTable
        CardShoe
        Player(s)
        Dealer
    It also prints out the game information on the following local objects:
        listPlayers : stores names of players and their current bank
        blackjack_multiplier : multiplier for the casino (can be overridden
            by the table multiplier, if better)
        listDealers : list of the Dealers in the casino and the type of table
            they deal at (normal, special event, high rollar, beginner)
    When player(s) pick a table to play at, a table object is created. Before
    that, it does not exist. The tableObj has a Dealer object and up to
    three player objects that manage their hands, banks, and betting options.
    Since this is partly a diagnostic function, we cannot assume that any of
    these objects exist.
    INPUT: two arguments
        tableObj, a CasinoTable object
        optional 'v' or 'verbose' argument (all other strings are ignored)
    OUTPUT: A quick visual printout of the contents of the active objects in
        the current game. If the verbose option is requested, it will also
        issue the dianostic_print() methods for the classes CasinoTable,
        Player, Dealer, and CardShoe. The latter outputs should go to the
        terminal output.
    """
    # First, clear the screen.
    DISPLAYSURF.fill(BGCOLOR)
    posX = LEFTMARGIN
    posY = TOPMARGIN
    
    # See if a table object exists.
    if tableObj:
        tableObjInfoSurf = BASICFONT.render('A CasinoTable object exists', True, TEXTCOLOR)
        tableObjInfoRect = tableObjInfoSurf.get_rect()
        tableObjInfoRect.topleft = (posX, posY)
        DISPLAYSURF.blit(tableObjInfoSurf, tableObjInfoRect)
        posY += LINESPACING12
        if output == 'v' or output == 'verbose':
            tableObj.diagnostic_print()
        if tableObj.tableDealer != None:
            tableObjInfoSurf = BASICFONT.render('A Dealer object was found inside the CasinoTable', True, TEXTCOLOR)
            tableObjInfoRect = tableObjInfoSurf.get_rect()
            tableObjInfoRect.topleft = (posX, posY)
            DISPLAYSURF.blit(tableObjInfoSurf, tableObjInfoRect)
            posY += LINESPACING12
            tableDealer = tableObj.tableDealer.extract_data()
            printTableDealer(tableDealer, 'diagnostic')
            generateTable(tableChoice['table color'])

        if tableObj.players:
            numOfPlayers = len(tableObj.players)
            tableObjInfoSurf = BASICFONT.render('%s players have been found inside the CasinoTable' % (numOfPlayers), True, TEXTCOLOR)
            tableObjInfoRect = tableObjInfoSurf.get_rect()
            tableObjInfoRect.topleft = (posX, posY)
            DISPLAYSURF.blit(tableObjInfoSurf, tableObjInfoRect)
            # Note: We need the index to go from 1 to 3 inclusive.
            for seat in TABLESEATS:
                playerObj = tableObj.players[seat].extract_data()
                printTablePlayer(playerObj, seat, 'diagnostic')
            

    else: # tableObj is not defined.
        tableObjInfoSurf = BASICFONT.render('No CasinoTable object found', True, TEXTCOLOR)
        tableObjInfoRect = tableObjInfoSurf.get_rect()
        tableObjInfoRect.topleft = (posX, posY)
        DISPLAYSURF.blit(tableObjInfoSurf, tableObjInfoRect)
        posY += LINESPACING12


def printTableDealer(tableDealer, output = 'player turn'):
    '''
    This method requires a dealer object produced by the Dealer.__str__()
    method. The dictionary with all of the Dealer's data has the  structure:
        'name'               : dealer's name (aka "Dealer")
        'bank'               : dealer's bank
	'hand'               : dealer's hand or None (a list)
	'soft score'         : soft score for dealer's hand or None
	'hard score'         : hard score for dealer's hand or None
	'visible card'       : a tuple of the hand[0] or None
	'visible soft score  : soft score of the visible card
	'visible hard score  : hard score of the visible card
	'dealer turn'        : set to None (normal) or True (dealer's turn)
    To avoid too much code duplication, this method uses an argument to
    determine what kind of output to produce. See below for an explanation:
    INPUT: tableDealer (a dict object with the data above),
           optional output argument that determines printout content
               valid options are:
               'player turn'    : keep dealer's hold card and actual scores
                                  hidden, default value
               'dealer turn'    : print out real hands and score, skipping any
                                  marked 'visible', can be triggered by the
                                  'dealer turn' key existing
               'diagnostic'     : print everything in the dealer's dictionary
    OUTPUT: There is output to the screen, but no return value
    '''
    # We need a starting position for this data above the dealer. All the
    # remaining lines of output will print relative to the staring position.
    # Dealer's name and bank always print out regardless of the mode in this
    # function call.
    posY = 2 * LINESPACING12
    if output == 'diagnostic':
        outputTypeSurf = DATAFONT.render("Diagnostic Printout", True, TEXTCOLOR)
        outputTypeRect = outputTypeSurf.get_rect()
        outputTypeRect.center = (WINCENTERX, posY)
        DISPLAYSURF.blit(outputTypeSurf, outputTypeRect)
    # The dealer and player turn banners are no longer needed with the phase
    # and turn numbers in the upper right corner.
    posY += 2 * LINESPACING12
    dealerNameSurf = BASICFONT.render("Dealer's Name: %s" % (tableDealer['name']), True, TEXTCOLOR)
    dealerNameRect = dealerNameSurf.get_rect()
    dealerNameRect.center = (WINCENTERX, posY)
    DISPLAYSURF.blit(dealerNameSurf, dealerNameRect)
    posY += LINESPACING12
    dealerBankString = "Dealer's Bank: ${:,}.".format(tableDealer['bank'])
    dealerBankSurf = BASICFONT.render(dealerBankString, True, TEXTCOLOR)
    dealerBankRect = dealerBankSurf.get_rect()
    dealerBankRect.center = (WINCENTERX, posY)
    DISPLAYSURF.blit(dealerBankSurf, dealerBankRect)
    posY += LINESPACING12

    # The cover color for the hold card will be SILVER. The alpha for its
    # overlay is 50% for diagnostic printouts, 100% during player's turns,
    # and unused in the Dealer's turn. Opaque = 255. These cards stay in front
    # of the Dealer's station until the Dealer's turn. The code for the
    # Dealer's turn skips the use of the overlay.
    if output == 'diagnostic':
        alpha = 128
    else:
        alpha = 255
    dealerHoldCardOverlaySurf = pygame.Surface((CARDWIDTH, CARDHEIGHT))
    dealerHoldCardOverlaySurf.fill(SILVER)
    dealerHoldCardOverlaySurf.convert_alpha()
    dealerHoldCardOverlayRect = dealerHoldCardOverlaySurf.get_rect()

    # Now, we need to know how many cards are in the Dealer's hand or if it
    # it exists at all.
    if tableDealer['hand']:
        sizeOfHand = len(tableDealer['hand'])
    else:
        sizeOfHand = 0
    
    # If the Dealer's hand does not exist, normally, all output associated
    # the Dealer's hand is skipped. For diagnostic printouts, we need a notice
    # that the hand is missing.
    if not tableDealer['hand'] and output == 'diagnostic':
        dealerHandSurf = BASICFONT.render("Dealer's hand does not exist", True, TEXTCOLOR)
        dealerHandRect = dealerHandSurf.get_rect()
        dealerHandRect.center = (WINCENTERX, posY)
        DISPLAYSURF.blit(dealerHandSurf, dealerHandRect)
        posY += LINESPACING12

    # During the Dealer's turn and in diagnostic mode, we need a full view of
    # the Dealer's hand and the actual cards present. The hand is also placed
    # in the middle of the table as the Dealer plays its hand.
    # Remember, we can send a printout of 'dealer turn' to indicate it is the
    # Dealer's turn. The Dealer.dealer_print() method will set the 'dealer turn'
    # flag in the dictionary it returns to True.
    if (tableDealer['dealer turn'] or output == 'dealer turn' or output == 'diagnostic') and tableDealer['hand']:
        dealerHardScoreSurf = SCOREFONT.render("Dealer's hard score: %s" % (tableDealer['hard score']), True, TEXTCOLOR)
        dealerHardScoreRect = dealerHardScoreSurf.get_rect()
        dealerHardScoreRect.center = (WINCENTERX, posY)
        DISPLAYSURF.blit(dealerHardScoreSurf, dealerHardScoreRect)
        posY += LINESPACING12
        dealerSoftScoreSurf = SCOREFONT.render("Dealer's soft score: %s" % (tableDealer['soft score']), True, TEXTCOLOR)
        dealerSoftScoreRect = dealerSoftScoreSurf.get_rect()
        dealerSoftScoreRect.center = (WINCENTERX, posY)
        DISPLAYSURF.blit(dealerSoftScoreSurf, dealerSoftScoreRect)
        posY += LINESPACING12
        # Now, we need print the hand in the middle of the table. The cards
        # are played in the center of the table. The first two cards will be
        # to the left of center. Any additional cards the Dealer must accept
        # during its turn will be to the right of the center.
        for i in xrange(0, sizeOfHand):
            card = tableDealer['hand'][i]
            cardY = WINCENTERY
            cardX = WINCENTERX - (2 - i) * (CARDWIDTH + CARDSPACING) + (int((CARDSPACING + CARDWIDTH)/ 2))
            cardRect = CARDIMAGES[card]['rect']
            cardRect.center = (cardX, cardY)
            DISPLAYSURF.blit(CARDIMAGES[card]['surface'], cardRect)

    # In a diagnostic run, we want messages indicating that the game is aware
    # that the Dealer has no hand when one does not exist. During regular
    # game play, these messages would be skipped. This message has to do with
    # visible card not existing with a hand that does exist.
    if not tableDealer['visible card'] and sizeOfHand == 1 and output == 'diagnostic':
        # As above, in diagnostic mode, we need to see that there is no
        # visible card in a message on screen. On the Player's turn
        # and Dealer's turn, this code would be skipped.
        dealerVisibleCardSurf = BASICFONT.render("Dealer's visible card does not exist", True, TEXTCOLOR)
        dealerVisibleCardRect = dealerVisibleCardSurf.get_rect()
        dealerVisibleCardRect.center = (WINCENTERX, posY)
        DISPLAYSURF.blit(dealerVisibleCardSurf, dealerVisibleCardRect)
        posY += LINESPACING12
    
    # On the players' turn (the turn in which all of the players play their
    # hands, the Dealer's hold card is kept confidential and the hand scores
    # change to scoring around the visible card. The Dealer's hand is also
    # kept in front of the Dealer's station at the top of the table (black
    # rectangle). The hold card is covered in an opaque mask that is reduced
    # to 50% alpha in diagnostic mode (see code block above.
    if (output == 'player turn' and not tableDealer['dealer turn']) or output == 'diagnostic':

        # As before, we print any scores that are valid, but this time only
        # on the visible card. It is possible to get this far, and still not
        # have a dealer's hand (and therefore no visible card either).
        # There could also be only the hold card dealt.

        # Now, we need to print the hold card, if the hand exists. This code
        # block is still inside the test for player's turn or diagnostics.
        if tableDealer['hand']:
            posXHoldCard = WINCENTERX - (int((CARDSPACING + CARDWIDTH)/ 2))
            posYHoldCard = DEALERSCARDS
            holdCard = tableDealer['hand'][0]
            print("printTableDealer: holdCard is {}.".format(holdCard))
            dealerHoldCardSurf = CARDIMAGES[holdCard]['surface']
            dealerHoldCardRect = CARDIMAGES[holdCard]['rect']
            dealerHoldCardRect.topleft = (posXHoldCard, posYHoldCard)
            DISPLAYSURF.blit(dealerHoldCardSurf, dealerHoldCardRect)
            dealerHoldCardOverlaySurf.set_alpha(alpha)
            dealerHoldCardOverlayRect.topleft = (posXHoldCard, posYHoldCard)
            DISPLAYSURF.blit(dealerHoldCardOverlaySurf, dealerHoldCardOverlayRect)

        # We need to print the "visisble card" if it exists. Again, we are
        # still in the player's turn code block.
        if tableDealer['hand'] and sizeOfHand > 1:
            posXVisCard = WINCENTERX + (int((CARDSPACING + CARDWIDTH)/ 2))
            posYVisCard = DEALERSCARDS
            print("printTableDealer: tableDealer's visible card is {}.".format(tableDealer['visible card']))
            # In Dealer and Player objects, the cards are tuples inside of
            # lists. We need to call the first and only member of this list.
            visCard = tableDealer['visible card'][0]
            print("printTableDealer: visCard = {}.".format(visCard))
            dealerVisCardSurf = CARDIMAGES[visCard]['surface']
            dealerVisCardRect = CARDIMAGES[visCard]['rect']
            dealerVisCardRect.topleft = (posXVisCard, posYVisCard)
            DISPLAYSURF.blit(dealerVisCardSurf, dealerVisCardRect)
            dealerVisHardScoreSurf = SCOREFONT.render("Dealer is showing a hard score: %s" % (tableDealer['visible hard score']), True, TEXTCOLOR)
            dealerVisHardScoreRect = dealerVisHardScoreSurf.get_rect()
            dealerVisHardScoreRect.center = (WINCENTERX, posY)
            DISPLAYSURF.blit(dealerVisHardScoreSurf, dealerVisHardScoreRect)
            posY += LINESPACING12
            dealerVisSoftScoreSurf = SCOREFONT.render("Dealer is showing a soft score: %s" % (tableDealer['visible soft score']), True, TEXTCOLOR)
            dealerVisSoftScoreRect = dealerVisSoftScoreSurf.get_rect()
            dealerVisSoftScoreRect.center = (WINCENTERX, posY)
            DISPLAYSURF.blit(dealerVisSoftScoreSurf, dealerVisSoftScoreRect)
            posY += LINESPACING12
                
    pygame.display.update()
    FPSCLOCK.tick()
    return # printTableDealer

def printTablePlayer(playerObj, seat, output = 'normal'):
    '''
    This method prints on screen the full data for a player. This data
    is pulled from the Player.extract_data method, which returns a dictionary
    of the form below:
        'name'                  : player's name
        'bank'                  : player's bank
        'hand'                  : player's regular hand or None
        'split hand'            : player's split hand or None
        'soft score'            : soft score for player's hand or None
        'hard score'            : hard score for player's hand or None
        'soft score split hand' : soft score for split hand or None
        'hard score split hand' : hard score for split hand or None
        'regular bet'           : bet amount on regular hand or None
        'split hand bet'        : bet amount on split hand or None
        'insurance bet'         : bet amount on dealer blackjack or None

    "hands" are set to None if they do not exist, including split_hand.  The
    split_flag is used to check for the latter. Bets and scores are set to
    None if they are zero in this dictionary.
    Note: This method assumes that player being printed has been found in a
    CasinoTable class object.
    INPUTS: playerObj : dict object, see above
            ordinal   : ordinal string 'left' 'middle' 'right' corresponding
                to seat 1, 2, 3
            output    : string determining the output of this function
                'diagnostic' : prints everything about the player, putting in
                               messages for None items
                'normal'     : prints only what exists for the player. "None"
                               items are skipped.
    '''
    # This function has to calculate where the player's data will be printed.
    # There is only room for MAXPLAYERS. All of this screen output needs  to
    # written from the bottom up. The players will never see teh difference
    # because nothing appears on screen until a pygame.display.update() is
    # called. regHandX and regHandY are the positions of the player's cards.
    # splitHandY are a card height directly above them while splitHandX will
    # the same for the both the regular and split hands. We need all three
    # sets of coordinates for the score data and both hands of cards, as they
    # all printing independently of each other.
    if seat == 'left':
        # The player is the left one. posX will be on the screen margin,
        # while regHandX and splitHandX will on the left margin of the green
        # area of the table.
        posX       = LEFTMARGIN
        regHandX   = TABLELEFTMARGIN
        splitHandX = regHandX

    elif seat == 'middle':
        # The player is the center one. posX moves the output under the center
        # of the table, but it will be lined up there. Likewise, regHandX moves
        # there as well. We set the pointer to place the first two cards of
        # either hand to the left of the center line of the table. splitHandX
        # does the same.
        posX       = WINCENTERX - CENTEROUTPUT
        regHandX   = WINCENTERX - (2 * (CARDWIDTH + CARDSPACING)) + (int((CARDSPACING + CARDWIDTH)/ 2))
        splitHandX = regHandX

    else:
        # The player is the right one. posX will be on the screen margin, with
        # an adjustment width of the score data rectangle. regHandX will on the
        # left margin of the green area of the table, less the width of four
        # cards laid side by side. The same is true of splitHandX,
        posX       = RIGHTMARGIN - SCOREWIDTH
        regHandX   = TABLERIGHTMARGIN - (4 * (CARDWIDTH + CARDSPACING))
        splitHandX = regHandX
    # posY is the same in all cases. It starts half of LINESPACING12 above the
    # bottom margin. regHandY is at the bottom margin of the table. This is
    # where the split and regular hands differ. The split hand is positioned
    # above the regular hand.
    posY       = BOTTOMMARGIN - int(LINESPACING12 / 2)
    regHandY   = TABLEBOTTOMMARGIN
    splitHandY = regHandY - (CARDHEIGHT + CARDSPACING)

    if playerObj['insurance bet']:
        insBetString = "Insurance Bet: ${:,}.".format(playerObj['insurance bet'])
        insBetSurf = SCOREFONT.render(insBetString, True, TEXTCOLOR)
        insBetRect = insBetSurf.get_rect()
        insBetRect.topleft = (posX, posY)
        DISPLAYSURF.blit(insBetSurf, insBetRect)
        posY -= LINESPACING12
    else:
        if output == 'diagnostic':
            insBetSurf = SCOREFONT.render("No insurance bet found", True, TEXTCOLOR)
            insBetRect = insBetSurf.get_rect()
            insBetRect.topleft = (posX, posY)
            DISPLAYSURF.blit(insBetSurf, insBetRect)
            posY -= LINESPACING12

    if playerObj['split hand bet']:
        splitBetString = "Bet on split hand: ${:,}.".format(playerObj['split hand bet'])
        splitBetSurf = SCOREFONT.render("Bet on split hand: $%s" % (playerObj['split hand bet']), True, TEXTCOLOR)
        splitBetRect = splitBetSurf.get_rect()
        splitBetRect.topleft = (posX, posY)
        DISPLAYSURF.blit(splitBetSurf, splitBetRect)
        posY -= LINESPACING12
    else:
        if output == 'diagnostic':
            splitBetSurf = SCOREFONT.render("No split bet found", True, TEXTCOLOR)
            splitBetRect = splitBetSurf.get_rect()
            splitBetRect.topleft = (posX, posY)
            DISPLAYSURF.blit(splitBetSurf, splitBetRect)
            posY -= LINESPACING12

    if playerObj['regular bet']:
        regBetString = "Bet on regular hand: ${:,}.".format(playerObj['regular bet'])
        regBetSurf = SCOREFONT.render(regBetString, True, TEXTCOLOR)
        regBetRect = regBetSurf.get_rect()
        regBetRect.topleft = (posX, posY)
        DISPLAYSURF.blit(regBetSurf, regBetRect)
        posY -= LINESPACING12
    else:
        if output == 'diagnostic':
            regBetSurf = SCOREFONT.render("No regular bet found", True, TEXTCOLOR)
            regBetRect = regBetSurf.get_rect()
            regBetRect.topleft = (posX, posY)
            DISPLAYSURF.blit(regBetSurf, regBetRect)
            posY -= LINESPACING12

    if playerObj['hard score split hand']:
        hardSplitScoreSurf = SCOREFONT.render("Hard score on split hand: %s" % (playerObj['hard score split hand']), True, TEXTCOLOR)
        hardSplitScoreRect = hardSplitScoreSurf.get_rect()
        hardSplitScoreRect.topleft = (posX, posY)
        DISPLAYSURF.blit(hardSplitScoreSurf, hardSplitScoreRect)
        posY -= LINESPACING12
    else:
        if output == 'diagnostic':
            hardSplitScoreSurf = SCOREFONT.render("No hard hand score on split hand was found", True, TEXTCOLOR)
            hardSplitScoreRect = hardSplitScoreSurf.get_rect()
            hardSplitScoreRect.topleft = (posX, posY)
            DISPLAYSURF.blit(hardSplitScoreSurf, hardSplitScoreRect)
            posY -= LINESPACING12

    if playerObj['soft score split hand']:
        softSplitScoreSurf = SCOREFONT.render("Soft score on split hand: %s" % (playerObj['soft score split hand']), True, TEXTCOLOR)
        softSplitScoreRect = softSplitScoreSurf.get_rect()
        softSplitScoreRect.topleft = (posX, posY)
        DISPLAYSURF.blit(softSplitScoreSurf, softSplitScoreRect)
        posY -= LINESPACING12
    else:
        if output == 'diagnostic':
            softSplitScoreSurf = SCOREFONT.render("No soft hand score on split hand was found", True, TEXTCOLOR)
            softSplitScoreRect = softSplitScoreSurf.get_rect()
            softSplitScoreRect.topleft = (posX, posY)
            DISPLAYSURF.blit(softSplitScoreSurf, softSplitScoreRect)
            posY -= LINESPACING12

    # This is purely diagnostic message that the split hand has does not exist.
    if not playerObj['hand'] and output == 'diagnostic':
        splitHandDiagSurf = SCOREFONT.render("No split hand was found", True, TEXTCOLOR)
        splitHandDiagRect = splitHandDiagSurf.get_rect()
        splitHandDiagRect.topleft = (posX, posY)
        DISPLAYSURF.blit(splitHandDiagSurf, splitHandDiagRect)
        posY -= LINESPACING12

    if playerObj['hard score']:
        hardScoreSurf = SCOREFONT.render("Hard score on regular hand: %s" % (playerObj['hard score']), True, TEXTCOLOR)
        hardScoreRect = hardScoreSurf.get_rect()
        hardScoreRect.topleft = (posX, posY)
        DISPLAYSURF.blit(hardScoreSurf, hardScoreRect)
        posY -= LINESPACING12
    else:
        if output == 'diagnostic':
            hardScoreSurf = SCOREFONT.render("No hard hand score was found", True, TEXTCOLOR)
            hardScoreRect = hardScoreSurf.get_rect()
            hardScoreRect.topleft = (posX, posY)
            DISPLAYSURF.blit(hardScoreSurf, hardScoreRect)
            posY -= LINESPACING12

    if playerObj['soft score']:
        softScoreSurf = SCOREFONT.render("Soft score on regular hand: %s" % (playerObj['soft score']), True, TEXTCOLOR)
        softScoreRect = softScoreSurf.get_rect()
        softScoreRect.topleft = (posX, posY)
        DISPLAYSURF.blit(softScoreSurf, softScoreRect)
        posY -= LINESPACING12
    else:
        if output == 'diagnostic':
            softScoreSurf = SCOREFONT.render("No soft hand score was found", True, TEXTCOLOR)
            softScoreRect = softScoreSurf.get_rect()
            softScoreRect.topleft = (posX, posY)
            DISPLAYSURF.blit(softScoreSurf, softScoreRect)
            posY -= LINESPACING12

    # This is purely diagnostic message that the regular has does not exist.
    if not playerObj['hand'] and output == 'diagnostic':
        handDiagSurf = SCOREFONT.render("No regular hand was found", True, TEXTCOLOR)
        handDiagRect = handDiagSurf.get_rect()
        handDiagRect.topleft = (posX, posY)
        DISPLAYSURF.blit(handDiagSurf, handDiagRect)
        posY -= LINESPACING12

    if playerObj['bank']:
        playerBankString = "Bank: ${:,}.".format(playerObj['bank'])
        playerBankSurf = BASICFONT.render(playerBankString, True, TEXTCOLOR)
        playerBankRect = playerBankSurf.get_rect()
        playerBankRect.topleft = (posX, posY)
        DISPLAYSURF.blit(playerBankSurf, playerBankRect)
        posY -= LINESPACING12
    else:
        if output == 'diagnostic':
            playerBankSurf = BASICFONT.render("No bank for this player was found", True, TEXTCOLOR)
            playerBankRect = playerBankSurf.get_rect()
            playerBankRect.topleft = (posX, posY)
            DISPLAYSURF.blit(playerBankSurf, playerBankRect)
            posY -= LINESPACING12

    if playerObj['name']:
        playerNameSurf = BASICFONT.render("Name: %s" % (playerObj['name']), True, TEXTCOLOR)
        playerNameRect = playerNameSurf.get_rect()
        playerNameRect.topleft = (posX, posY)
        DISPLAYSURF.blit(playerNameSurf, playerNameRect)
        posY -= LINESPACING12
    else:
        if output == 'diagnostic':
            playerNameSurf = BASICFONT.render("No name for the player was found", True, TEXTCOLOR)
            playerNameRect = playerNameSurf.get_rect()
            playerNameRect.topleft = (posX, posY)
            DISPLAYSURF.blit(playerNameSurf, playerNameRect)
            posY -= LINESPACING12

    # Diagnostic output should be indicated on each player.
    if output == 'diagnostic':
        outputTypeSurf = DATAFONT.render("Diagnostic Printout", True, TEXTCOLOR)
        outputTypeRect = outputTypeSurf.get_rect()
        outputTypeRect.topleft = (posX, posY)
        DISPLAYSURF.blit(outputTypeSurf, outputTypeRect)
        posY -= LINESPACING12

    # Now, we need to print out the cards in any hands the player has,
    # starting with the regular hand. The users cannot see this take place.
    # (regHandX, regHandY) and (splitHandX, splitHandY) have already been
    # intialized at the beginning of this function. All these loops do is
    # increment across horizontally as the cards are laid out. Y coordinates
    # do not change.
    if playerObj['hand']:
        sizeOfHand = len(playerObj['hand'])
        for i in xrange(0, sizeOfHand):
            card = playerObj['hand'][i]
            cardRect = CARDIMAGES[card]['rect']
            cardRect.center = (regHandX, regHandY)
            print("printTablePlayer: Card location is ({0}, {1}).".format(regHandX, regHandY))
            DISPLAYSURF.blit(CARDIMAGES[card]['surface'], cardRect)
            regHandX += CARDWIDTH + CARDSPACING

    if playerObj['split hand']:
        sizeOfHand = len(playerObj['split hand'])
        for i in xrange(0, sizeOfHand):
            card = playerObj['split hand'][i]
            cardRect = CARDIMAGES[card]['rect']
            cardRect.center = (splitHandX, splitHandY)
            print("printTablePlayer: Card location is ({0}, {1}).".format(splitHandX, splitHandY))
            DISPLAYSURF.blit(CARDIMAGES[card]['surface'], cardRect)
            splitHandX += CARDWIDTH + CARDSPACING
        
        
    pygame.display.update()
    FPSCLOCK.tick()

def generateTable(tableColor = OLIVE):
    """
    This function prints a basic table to the screen. It does not print the
    cards, nor any data on the players or dealers. That is done by other
    methods and functions.
    INPUTS: None
    OUTPUTS: None, other than pygame creation of a blank table.
    """
    # This stanza creates the table surface. It is composed of a brown oval
    # a green oval, a black rectangle (dealer's station), and areas where
    # player cards will be dealt. These Rect objects use the form:
    # pygame.Rect((left, top), (width, height)). The formulas are calculating
    # the X and Y distances to the (left, top) of each rect object from the
    # CENTER of the game window.
    
    tableOuterRectLeft = WINCENTERX - int(TABLEWIDTH / 2)
    tableOuterRectTop  = WINCENTERY - int(TABLEHEIGHT / 2)
    tableOuterRect = pygame.Rect((tableOuterRectLeft, tableOuterRectTop),
                                 (TABLEWIDTH, TABLEHEIGHT))

    tableInnerRectLeft = WINCENTERX - int((TABLEWIDTH - TABLERIM) / 2)
    tableInnerRectTop  = WINCENTERY - int((TABLEHEIGHT - TABLERIM) / 2)
    tableInnerRect = pygame.Rect((tableInnerRectLeft, tableInnerRectTop),
                                 (TABLEWIDTH - TABLERIM, TABLEHEIGHT - TABLERIM))
    
    dealerStationRectTop  = DEALERSTATIONTOP
    dealerStationRectLeft = DEALERSTATIONLEFT
    dealerStationRect = pygame.Rect((dealerStationRectLeft, dealerStationRectTop),
                                    (STATIONWIDTH, STATIONHEIGHT))

    pygame.draw.rect(DISPLAYSURF, SADDLEBROWN, tableOuterRect)
    pygame.draw.rect(DISPLAYSURF, tableColor,  tableInnerRect)
    pygame.draw.rect(DISPLAYSURF, BLACK,       dealerStationRect)

    pygame.display.update()
    FPSCLOCK.tick()

def generateDealerList():
    """
    This function creates a list of dictionary objects that feed initial
    settings for creating dealer objects in CasinoTable objects. The structure
    is a list of dictionaries of the form below:
        'name'  : Dealer's name (string)
        'type'  : This is type of CasinoTable that this "dealer" normally works
                    'high'    : only works high roller tables, banks over $1m
                    'starter' : best for new players, bank under $100k
                    'normal'  : banks 100-250k
                    'special' : dealer only works special events
                    
    For the early versions of the pygame implementation, this list will be
    hardcoded, but the intention is to migrate this data to a much more
    complete database, such as a postgres or sql-lite database.
    INPUTS: None
    OUTPUTS: list of dictionaries with the following additions
        'bank' : A value calculated from a base determined by table type
                 and adjusted by a random amount
        'blackjack_multiplier : A value chosen randomly from a set of ratios
                 controlled by the table type
        'table color' : This the color of the felt of the table. The rim is
                 always leather.
        'table bets'  : Tuple storing the min and max bets that table allows

    Each table type has formulas, complete with random choices to create
    variety during play. All die rolls have a max value of whatever the die
    itself can produce (d6+2 still maxes at 6, but a d6-2 maxes at 4). All die
    rolls have a min of 0 (no negative values). The function, dieRoll(),
    produces these "weighted" die results.
        'starter': Starter tables
            'bank': $50k + [(d30 - 5) * $1k]
                This produces a range 50-75k with most banks being 50k
            'table color' : OLIVE
            'blackjack multiplier' : d6 choice from the following options:
                1) 7:3, 2.33
                2) 9:4, 2.25
                3) 2:1, 2.00
                4) 7:4, 1.75
                5) 5:3, 1.67
                6) 3:2, 1.50
            'table bets' : (tableMin = 5, tableMax = 100)
            
        'high' : High Roller Tables
            'bank': $1m + (d100 * $25k)
                This produces a range of $1-3.5m (uniform)
            'table color' : PURPLE
            'blackjack multiplier' : d6 choice from the following options:
                1) 11:4, 2.75
                2) 8:3, 2.67
                3) 5:2, 2.50
                4) 7:3, 2.33
                5) 9:4, 2.25
                6) 2:1, 2.00
            'table bets' : (tableMin = 500, tableMax = 100k)

        'special' : Special Event Tables
            'bank': $250k + (d100 * 5k)
                This produces a range of $250-750k (uniform)
            'table color' : AQUAMARINE
            'blackjack multiplier' : d4 choice from the following options:
                1) 3:1, 3.00
                2) 5:2, 2.50
                3) 2:1, 2.00
                4) 3:2, 1.50
            'table bets' : (tableMin = 250, tableMax = 1000)        

        'normal' : Regular Tables
            'bank': $100k + [(d100 - 25) * 2k]
                This produces a range of $100-250k, weighted to 25% of banks
                being $100k
            'table color' : BLUE
            'blackjack multiplier' : d8 choice from the following options:
                1) 2:1, 2.00
                2) 9:5, 1.80
                3) 7:4, 1.75
                4) 8:5, 1.60
                5) 5:3, 1.67
                6) 7:5, 1.40
                7) 4:3, 1.33
                8) 6:5, 1.20
            'table bets' : (tableMin = 50, tableMax = 200)
            
    Note: All players start with the starter tables while they learn to play
    this game. It helps to reinforce that the game is partly about having fun,
    but it is also about beating the bank.
    """
    listDealers = []
    listDealers.append({'name' : 'Frank',   'type' : 'starter'})
    listDealers.append({'name' : 'Hannah',  'type' : 'normal'})
    listDealers.append({'name' : 'Mike',    'type' : 'normal'})
    listDealers.append({'name' : 'Rayden',  'type' : 'special'})
    listDealers.append({'name' : 'Charlie', 'type' : 'special'})
    listDealers.append({'name' : 'Freddie', 'type' : 'high'})
    listDealers.append({'name' : 'James',   'type' : 'high'})
    listDealers.append({'name' : 'Angela',  'type' : 'high'})
    # print(listDealers)

    numOfDealers = len(listDealers)
    # As mentioned in the main comment block, we need to calculate the banks
    # for each dealer, their current table blackjack_multiplier, and the color
    # of the felt on their table. These are determined by formulas that depend
    # on the type of table the dealer works at.
    for i in range(0, numOfDealers):
        if listDealers[i]['type'] == 'starter':
            listDealers[i]['table color'] = OLIVE
            listDealers[i]['bank'] = 50000 + (1000 * dieRoll(30, 0, 25, -5))
            multiplierChoice = dieRoll(6, 1, 6)
            if multiplierChoice == 1:
                listDealers[i]['blackjack multiplier'] = ('7:3', 2.33)
            elif  multiplierChoice == 2:
                listDealers[i]['blackjack multiplier'] = ('9:4', 2.25)
            elif  multiplierChoice == 3:
                listDealers[i]['blackjack multiplier'] = ('2:1', 2.00)
            elif  multiplierChoice == 4:
                listDealers[i]['blackjack multiplier'] = ('7:4', 1.75)
            elif  multiplierChoice == 5:
                listDealers[i]['blackjack multiplier'] = ('5:3', 1.67)
            elif  multiplierChoice == 6:
                listDealers[i]['blackjack multiplier'] = ('3:2', 1.50)
            listDealers[i]['table bets'] = (5, 100)
            
        elif listDealers[i]['type'] == 'normal':
            listDealers[i]['table color'] = BLUE
            listDealers[i]['bank'] = 100000 + (2000 * dieRoll(100, 0, 75, -25))
            multiplierChoice = dieRoll(8, 1, 8)
            if multiplierChoice == 1:
                listDealers[i]['blackjack multiplier'] = ('2:1', 2.00)
            elif  multiplierChoice == 2:
                listDealers[i]['blackjack multiplier'] = ('9:5', 1.80)
            elif  multiplierChoice == 3:
                listDealers[i]['blackjack multiplier'] = ('7:4', 1.75)
            elif  multiplierChoice == 4:
                listDealers[i]['blackjack multiplier'] = ('8:5', 1.60)
            elif  multiplierChoice == 5:
                listDealers[i]['blackjack multiplier'] = ('3:2', 1.50)
            elif  multiplierChoice == 6:
                listDealers[i]['blackjack multiplier'] = ('7:5', 1.40)
            elif  multiplierChoice == 7:
                listDealers[i]['blackjack multiplier'] = ('4:3', 1.33)
            elif  multiplierChoice == 8:
                listDealers[i]['blackjack multiplier'] = ('6:5', 1.20)
            listDealers[i]['table bets'] = (50, 200)

        elif listDealers[i]['type'] == 'special':
            listDealers[i]['table color'] = AQUAMARINE
            listDealers[i]['bank'] = 250000 + (5000 * dieRoll(100, 1, 100))
            multiplierChoice = dieRoll(4, 1, 4)
            if multiplierChoice == 1:
                listDealers[i]['blackjack multiplier'] = ('3:1', 3.00)
            elif  multiplierChoice == 2:
                listDealers[i]['blackjack multiplier'] = ('5:2', 2.50)
            elif  multiplierChoice == 3:
                listDealers[i]['blackjack multiplier'] = ('2:1', 2.00)
            elif  multiplierChoice == 4:
                listDealers[i]['blackjack multiplier'] = ('3:2', 1.50)
            listDealers[i]['table bets'] = (250, 1000)

        elif listDealers[i]['type'] == 'high':
            listDealers[i]['table color'] = PURPLE
            listDealers[i]['bank'] = 1000000 + (25000 * dieRoll(100, 1, 100))
            multiplierChoice = dieRoll(6, 1, 6)
            if multiplierChoice == 1:
                listDealers[i]['blackjack multiplier'] = ('11:4', 2.75)
            elif  multiplierChoice == 2:
                listDealers[i]['blackjack multiplier'] = ('8:3', 2.67)
            elif  multiplierChoice == 3:
                listDealers[i]['blackjack multiplier'] = ('5:2', 2.50)
            elif  multiplierChoice == 4:
                listDealers[i]['blackjack multiplier'] = ('7:3', 2.33)
            elif  multiplierChoice == 5:
                listDealers[i]['blackjack multiplier'] = ('9:4', 2.25)
            elif  multiplierChoice == 6:
                listDealers[i]['blackjack multiplier'] = ('2:1', 2.00)
            listDealers[i]['table bets'] = (500, 1000000)

    return listDealers # generateDealerList

def dieRoll(die, minNum, maxNum, adj=0):
    """
    This function generates random numbers for sequences with floor or ceiling
    values. For example, suppose you need to have a roll weighted to be zero
    more often than one possible value, such as d6-2 with a 0 minimum value.
    The sequence of numbers would be [0, 0, 1, 2, 3, 4]. Or suppose you want
    a d12+3 with max of 12. That sequence would be [4, 5, 6, 7, 8, 9 ,10, 11
    12, 12, 12, 12]. In this version, it cannot do a sequence like [1, 1, 2, 2].
    """
    numList = []
    for i in range(1, die + 1):
        currentNum = i + adj
        if not (minNum <= currentNum <= maxNum):
            if currentNum < minNum:
                currentNum = minNum
            elif currentNum > maxNum:
                currentNum = maxNum
        numList.append(currentNum)
    random.shuffle(numList)
    output = random.randint(0, die - 1)
    return numList[output]

def findPlayers(filename = './etc/savedgame.txt'):
    """
    This function looks for saved game files. The correct format for a saved
    game is a CSV file broken down as follows:
        string1, integer, string2
    where string1 is the player's name, integer is their remaining money in
    their bank (without any formatting), and string2 is their rank as a
    player (acceptable values are 'high', 'starter', 'normal', or 'special'.
    INPUT: filename (optional), defaults to 'etc/savedgame'
    OUTPUT: listPlayers, which will either be None or a list of player
        dictionaries with the following structure:
        'name'   : player's name (string)
        'bank'   : player's money in chips (integer)
        'skill'  : player's skill ('high'|'starter'|'normal'|'special')
    The list corresponds to seating where 0 --> left, 1 --> center, and
    2 --> right.
    NOTE: If filename cannot be found, read, or written to, it will return
    None. Likewise, if the file has bad data, it will return None.
    NOTE: This file can contain less than three players, but it cannot
    have less than one.
    """
    listPlayers = None
    try:
        # We try to open the saved game file. If it fails, we return None.
        testOpen = open(filename)
    except:
        # Something went wrong. So, we return None.
        listPlayers = None
        print("findPlayers: {} not found.".format(filename))
    else:
        # Successful fileopen. We need to see if we any good players contained
        # in the file. Note: We will only read up to three players. There can
        # be less than three in a saved game if a player was eliminated from
        # during a previous game.
        i = 0
        with open(filename) as savedGame:
            # We need to reinitialize listPlayers since the saved game is
            # readable. We will put this player's data into their dictionary
            # near the end of this process.
            print("findPlayers: Preparing to read {}.".format(filename))
            listPlayers = []
            for line in savedGame:
                print("findPlayers: Reading line {} of {}.".format(i, filename))
                # Break the line up into a list of strings on the commas.
                data = line.split(',')
                # There must be at least three strings. If not, the file is
                # corrupt.
                print("findPlayers: Read {} from {}.".format(data, filename))
                if len(data) < 3:
                    listPlayers = None
                    break
                # Assign the first string to playerName.
                playerName = data[0]
                # Now, we try to set the second string to an integer and
                # assign it to playerBank
                try:
                    playerBank = int(data[1])
                except:
                    # Python could not convert it into an integer, suggesting
                    # a corrupt file. We need to cancel the file reading
                    # process and return None.
                    listPlayers = None
                    break

                # Now, we need to check the third string to see if it is valid.
                # If it has an invalid value, again, we need to cancel reading
                # the file and return None. If it is valid, we assign it to
                # playerSkill. To make sure it ignores whitespace characters,
                # like linefeeds or returns, we need to remove them from this
                # string.
                for char in string.whitespace:
                    data[2] = data[2].replace(char, '')
                if data[2] not in ('high', 'starter', 'normal', 'special'):
                    listPlayers = None
                    break
                else:
                    playerSkill = data[2]

                # Since we got this far, all three data elements were usable.
                # We need to assign them to a player dictionary.
                listPlayers.append({ 'name'  : playerName,
                                     'bank'  : playerBank,
                                     'skill' : playerSkill})
                # Now, we increment our player counter. If it reaches 3, we
                # break out of the saved game file. We only need to read the
                # data for three players successfully. The writeSavedGame
                # function will overwrite the saved game later on.
                i += 1
                if i > 3:
                    break

    # We have either read a file with good data and return that data or we
    # had problems along the way and have to return None.
    return listPlayers

def writeSavedGame(listPlayers, filename = './etc/savedgame.txt'):
    """
    This function saves Player data to a saved game file.
    INPUTS: listPlayers, which will a list of player dictionaries with the
        following structure:
        'name'   : player's name (string)
        'bank'   : player's money in chips (integer)
        'skill'  : player's skill ('high'|'starter'|'normal'|'special')
        There will never be more than 3 players in listPlayers, but their
        may be less as players are eliminated during the game play.
    OUTPUTS: Boolean for successful/failed write. The data is written to
        a CSV text file with the following format:
            string1, integer, string2
        where string1 is the player's name, integer is their remaining money
        in their bank (without any formatting), and string2 is their rank as
        a player (acceptable values are 'high', 'starter', 'normal', or
        'special'. This indicates the highest dealer bank the surviving
        "team" busted.
    NOTE: This function will return True if there are no players to write to
    disk.
    """
    # If there are no players in listPlayers, there is nothing to do.
    if len(listPlayers) == 0:
        print("writeSavedGame: No players remained after the last game. Nothing to do.")
        return True
    # We need to convert the player data back into a list of CSV text lines.
    savedGameData = []
    for i in range(0, len(listPlayers)):
        newLine = listPlayers[i]['name'] + ', ' + str(listPlayers[i]['bank']) + ', ' + listPlayers[i]['skill'] + '\n'
        savedGameData.append(newLine)
        print("writeSavedGame: Data to save is now {}.".format(savedGameData))
    # Now, we try to write this data to disk.
    try:
        open(filename, 'w')
    except:
        print("writeSavedGame: Could not save game to disk.")
        return False
    else:
        with open(filename, 'a') as savedGame:
            for lineOut in savedGameData:
                savedGame.write(lineOut)
        return True
    # writeSavedGame

def pressSpaceToContinue(posX = WINDOWWIDTH, posY = WINDOWHEIGHT):
    """
    This function actually pauses the game so that the user can read the
    screen. It basically halts any progress until a key is pressed. It
    grabs all events, and terminates on QUIT events.
    Normally, this function prints the text on the edge of the bottom right
    of the game screen, but this can be overridden by specifying where you
    want the bottomright of the rect object to be.
    INPUTS: posX (pixel x-coordinate of bottomright corner of rect object)
                Default: bottom corner of the screen
            posY (pixel y-coordinate of bottomright corner of rect object)
                Default: bottom corner of the screen
    OUTPUTS: All outputs are to the screen.
    """
    displayRect = DISPLAYSURF.get_rect()
    while True:
        # In the lower right corner, print this message.
        textSurf = BASICFONT.render("Press spacebar to continue.", True, TEXTCOLOR)
        textRect = textSurf.get_rect()
        textRect.bottomright = (posX, posY)
        DISPLAYSURF.blit(textSurf, textRect)
        for event in pygame.event.get(QUIT): # get all QUIT events
            terminate()                      # terminate if any QUIT events are present
        for event in pygame.event.get(KEYUP):# get all KEYUP events
            if event.key == K_ESCAPE:        # ESCAPE is also a 'quit' event
                terminate()

        for event in pygame.event.get():     # Removed KEYDOWN only type
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:    # These are also QUIT events.
                    terminate()
                elif event.key == K_SPACE:
                    return
            # This stanza is an effort to make the game screen become active
            # after a change of focus.
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                active = displayRect.collidepoint(event.pos)
        pygame.display.update()
        FPSCLOCK.tick()
    return # pressSpaceToContinue

def createPlayers():
    """
    This function uses the Textbox class to create alphabetical only textboxes
    to get player names from the user. listPlayers is a global variable, but
    this function can return the value as well.
    INPUTS: None
    OUTPUTS: A list of player dictionaries with the following structure:
        'name'   : player's name (string)
        'bank'   : player's money in chips (integer)
        'skill'  : player's skill ('high'|'starter'|'normal'|'special')
        The skill will default to 'starter' since these are "new" players.
    """
    DISPLAYSURF.fill(BLACK)
    leftEdgeY = 0
    # We need to create a while loop that acts like a game loop here.
    welcomeMessage = "Welcome to Casino Blackjack."
    welcomeSurf = INSTRUCTFONT.render(welcomeMessage, True, TEXTCOLOR)
    welcomeRect = welcomeSurf.get_rect()
    welcomeRect.topleft = (LEFTMARGIN, leftEdgeY)
    DISPLAYSURF.blit(welcomeSurf, welcomeRect)
    leftEdgeY += LINESPACING18
    instructionMessages = []
    instructionMessages.append("You will be prompted for the names of three")
    instructionMessages.append("players who will help you beat the bank. Since")
    instructionMessages.append("you are starting a new game, all players will be")
    instructionMessages.append("'starter' in skill. Starter tables often have")
    instructionMessages.append("better blackjack payouts than regular tables.")
    instructionMessages.append("Only high roller and special event tables have")
    instructionMessages.append("better payouts than the starters. You will also")
    instructionMessages.append("have a chance to read the actual casino rules for")
    instructionMessages.append("blackjack once you have chosen a table.")
    # print("createPlayers: Instructions: {}".format(instructionMessages))
    # This loop prints the instruction messages down the left edge of the
    # screen. pressAnyKeyToContinue() pauses the game to give the player time
    # to read the instructions.
    for i in range(0, len(instructionMessages)):
        instMsgSurf = INSTRUCTFONT.render(instructionMessages[i], True, TEXTCOLOR)
        instMsgRect = instMsgSurf.get_rect()
        instMsgRect.topleft = (LEFTMARGIN, leftEdgeY)
        DISPLAYSURF.blit(instMsgSurf, instMsgRect)
        leftEdgeY += LINESPACING18
    pygame.display.update()
    FPSCLOCK.tick()
    pressSpaceToContinue()
    posY = int(WINDOWHEIGHT/3)
    for i in range(1, 4):
        playerText   = "What would you like to name Player #{}?".format(i)
        instTextSurf = INSTRUCTFONT.render(playerText, True, TEXTCOLOR)
        instTextRect = instTextSurf.get_rect(centerx = WINCENTERX, centery = posY)
        posY += LINESPACING18
        nameTextboxRect = instTextRect.copy()
        nameTextboxRect.center = (WINCENTERX, posY)
        pNameTextbox = Textbox((nameTextboxRect), fontSize = 18, command = setupPlayer,
                               charFilter = 'alpha', enterClears = True, enterDeactivates = True)
        playerName   = getTextboxNameEvents(pNameTextbox, instTextSurf, instTextRect, DISPLAYSURF)
    return # createPlayers

def getTextboxNameEvents(Textbox, promptSurf, promptRect, Surface):
    """
    This function takes a textbox as an argument and runs an event loop
    around it to capture the text entered into the textbox and return it to
    calling program.
    INPUTS: four arguments
        Textbox (a Textbox class object)
        promptSurf (a user prompt rendered text Surface)
        promptRect (the rect object for promptSurf)
        Surface (the surface to render prompts and Textbox on)
    OUTPUTS: string, Textbox.buffer contents
    """
    finishUp = False
    while not finishUp:
        for event in pygame.event.get():
            if event.type == QUIT:
                finishUp = True
            # This line ensures that pressing return ends the event loop.
            finishUp = Textbox.getEvent(event)
        # Update Textbox with any changes the "event" required.
        Textbox.updateBox()
        # Render the Textbox with the user prompt. Clear the screen as part
        # of the process.
        Surface.fill(NAVY)
        Textbox.drawBox(Surface)
        Surface.blit(promptSurf, promptRect)
        pygame.display.update()
        FPSCLOCK.tick()
        

def setupPlayer(id, name):
    """
    This function sets a player's name in listPlayers with the name extracted
    by the Textbox.  When RETURN or ENTER is pressed inside the Textbox, its
    command attribute executes this function with Textbox.buffer as an
    argument.
    This function  is only used when a new set of players has to be created.
    So, all players are 'starter' skill and have a starting bank.
    INPUTS: two arguments
        id, the id of the Textbox object
        name, a string captured from Textbox.finalBuffer
    OUTPUT: None, all changes are made to global variables
    """
    bank = STARTINGBANK + (1000 * dieRoll(30, 5, 25, 4))
    listPlayers.append({ 'name'  : name,
                         'bank'  : bank,
                         'skill' : 'starter' })

def getTableSkillList(listPlayers):
    """
    This function takes a list of players and returns a set listing all of
    table types they can play at. It creates a set of their skill levels and
    returns it to main. We use sets because they cannot store duplicat values.
    INPUT: listPlayers, a list of player dictionaries
    OUTPUT: tableTypes, a set of table types (see SKILLS constant for a full
        list)
    """
    playerLevels = set()
    for i in range(0, len(listPlayers)):
        playerLevels.add(listPlayers[i]['skill'])
    print("getTableSkillList: Players's skills are {}".format(playerLevels))
    # Now that we have players levels, we need to find the max table type they
    # can attend. We use slicing to do that.
    tableTypes = set()
    for level in playerLevels:
        newElements = []
        skillIndex = SKILLS.index(level)
        newElements.extend(SKILLS[:skillIndex + 1])
        for element in newElements:
            tableTypes.add(element)
    return tableTypes

def filterDealers(tableTypes, listDealers):
    """
    This function filters out the dealers who operate tables beyond the skills
    of the players in the user's list. This function uses a set, dealerIndexes
    to find all of the dealers that match skill/table types. Once identified,
    it creates a new list of dealers from that list.
    INPUT: two arguments
        tableTypes, set with the table types matching the players' skills
        listDealers, the full list of Dealer dictionaries
    OUTPUT: filtered list of dealer dictionaries
    """
    dealerIndexes = set()
    for tableType in tableTypes:
        for i in range(0, len(listDealers)):
            if tableType == listDealers[i]['type']:
                dealerIndexes.add(i)
    # Now, we have all of the indexes for the proper dealers, we need to build
    # the new list.
    filteredDealers = []
    for index in dealerIndexes:
        filteredDealers.append(listDealers[index])
    return filteredDealers

def offerTableChoices(listDealers):
    """
    This function takes the new list of dealers, lists them and their specs
    for the user, and asks them to choose a dealer. The dictionary for the
    user's choice is returned to main().  There are a number of "constants"
    used for data formatting:
        COLUMNSPACING: the distance in pixels between data columns
    INPUTS: listDealer, a list of dealer dictionary objects
    OUTPUTS: tableChoice, a dealer dictionary object based on name choice,
        not actually returned directly, since tableChoice is a global
    """
    COLUMNSPACING = 150
    # Clear the screen.
    DISPLAYSURF.fill(BGCOLOR)
    # First, we print the columns headers.
    posX = LEFTMARGIN
    posY = int(WINDOWHEIGHT / 4)
    nameHeader      = "Dealer's Name"
    nameHeaderSurf  = BASICFONT.render(nameHeader, True, TEXTCOLOR)
    nameHeaderRect  = nameHeaderSurf.get_rect(topleft = (posX, posY))
    DISPLAYSURF.blit(nameHeaderSurf, nameHeaderRect)
    posX += COLUMNSPACING
    bankHeader      = "Dealer's Current Bank"
    bankHeaderSurf  = BASICFONT.render(bankHeader, True, TEXTCOLOR)
    bankHeaderRect  = bankHeaderSurf.get_rect(topleft = (posX, posY))
    DISPLAYSURF.blit(bankHeaderSurf, bankHeaderRect)
    posX += COLUMNSPACING
    skillHeader      = "Dealer's Table Type"
    skillHeaderSurf  = BASICFONT.render(skillHeader, True, TEXTCOLOR)
    skillHeaderRect  = skillHeaderSurf.get_rect(topleft = (posX, posY))
    DISPLAYSURF.blit(skillHeaderSurf, skillHeaderRect)
    posX += COLUMNSPACING
    betHeader     = "Min and Max Bets"
    betHeaderSurf = BASICFONT.render(betHeader, True, TEXTCOLOR)
    betHeaderRect = betHeaderSurf.get_rect(topleft = (posX, posY))
    DISPLAYSURF.blit(betHeaderSurf, betHeaderRect)
    

    # Now, we print the information on the dealers.
    for i in range(0, len(listDealers)):
        posX = LEFTMARGIN
        posY += LINESPACING12
        nameSurf   = BASICFONT.render(listDealers[i]['name'], True, TEXTCOLOR)
        nameRect   = nameSurf.get_rect(topleft = (posX, posY))
        DISPLAYSURF.blit(nameSurf, nameRect)
        posX += COLUMNSPACING
        bankAmt = "{:,}".format(listDealers[i]['bank'])
        bankSurf   = BASICFONT.render(bankAmt, True, TEXTCOLOR)
        bankRect   = bankSurf.get_rect(topleft = (posX, posY))
        DISPLAYSURF.blit(bankSurf, bankRect)
        posX += COLUMNSPACING
        if listDealers[i]['type'] == 'special':
            skillValue = 'special events'
        elif listDealers[i]['type'] == 'high':
            skillValue = 'high rollers'
        else:
            skillValue = listDealers[i]['type']
        skillSurf   = BASICFONT.render(skillValue, True, TEXTCOLOR)
        skillRect   = skillSurf.get_rect(topleft = (posX, posY))
        DISPLAYSURF.blit(skillSurf, skillRect)
        posX += COLUMNSPACING
        minBet, maxBet = listDealers[i]['table bets']
        betAmountsText = "${:3d}/${:4d}".format(minBet, maxBet)
        betAmountsSurf = BASICFONT.render(betAmountsText, True, TEXTCOLOR)
        betAmountsRect = betAmountsSurf.get_rect(topleft = (posX, posY))
        DISPLAYSURF.blit(betAmountsSurf, betAmountsRect)
        
    pygame.display.update()
    FPSCLOCK.tick()

    # Now that that data has been printed, we need to setup the prompt for
    # user input, create the Textbox object for this input, and call
    # getTextboxEvents to get the name.
    posX = LEFTMARGIN
    posY += LINESPACING18
    playerText   = "Which dealer would you like to challenge?"
    instTextSurf = INSTRUCTFONT.render(playerText, True, TEXTCOLOR)
    instTextRect = instTextSurf.get_rect(topleft = (posX, posY))
    posY += LINESPACING18
    nameTextboxRect = instTextRect.copy()
    nameTextboxRect.topleft = (posX, posY)
    dNameTextbox = Textbox((nameTextboxRect), fontSize = 18, command = getTableChoice,
                            charFilter = 'alpha', enterClears = True, enterDeactivates = True)
    dealerName   = getTextboxEvents(dNameTextbox, instTextSurf, instTextRect, DISPLAYSURF)
    return # offerTableChoices

def getTextboxEvents(Textbox, promptSurf, promptRect, Surface):
    """
    While this function may appear to be a repeat of getTextboxNameEvents(),
    the code is somewhat different. That loop was designed to break out when
    it detected that listPlayers added a new item. It also cleared the screen
    between prompts. This function takes a user prompt, a Textbox, and the
    display Surface and renders the Textbox on screen, capturing the events
    the Textbox is set to filter for. It uses pressing Enter to exit.
    INPUTS: five arguments
        Textbox (a Textbox class object)
        promptSurf (a user prompt rendered text Surface)
        promptRect (the rect object for promptSurf)
        Surface (the surface to render prompts and Textbox on)
    OUTPUTS: string, Textbox.buffer contents
    """
    finishUp = False
    while not finishUp:
        for event in pygame.event.get():
            if event.type == QUIT:
                finishUp = True
            # This line ensures that pressing return ends the event loop.
            finishUp = Textbox.getEvent(event)
        # Update Textbox with any changes the "event" required.
        Textbox.updateBox()
        # Render the Textbox with the user prompt.
        Textbox.drawBox(Surface)
        Surface.blit(promptSurf, promptRect)
        pygame.display.update()
        FPSCLOCK.tick()
    return # getTextboxEvents
        
def getTableChoice(id, name):
    """
    This function is executed by the Textbox.command attribute. It returns
    the name of the dealer the user wants to pit the players against.
    INPUTS: two arguments
        id, the id of the Textbox object
        name, a string captured from Textbox.finalBuffer
    OUTPUTS: name, a string with the player's choice of dealer
    NOTE: The tableChoice is another global variable due to some limitations
        of pygame's GUI libraries.
    """
    global tableChoice
    tableChoice = {}
    # We need to find the dealer with a matching name and set tableChoice
    # equal to that object. Using the lower() string methods eliminates
    # capitalization problems.
    for i in range(0, len(listDealers)):
        if name.lower() == listDealers[i]['name'].lower():
            tableChoice = listDealers[i]
            print("getTableChoice: User's choice is {0}, which points to dealer {1}.".format(name, tableChoice))
            break
    return

def checkForQuit():
    """
    This function looks for QUIT events. It also checks KEYDOWN/KEYUP events
    for ESCAPE events. It will confirm any such events before calling the
    terminate() function. The booleans, endGame and verifyChoice are used to
    tell Python, respecitively, to terminate() or to verify that the user
    really wants to end without saving. If not, it will ask if the user
    wants to save and exit. saveGame carries that decision. If the user
    wants to save, it will copy any remaining player data in tableObj over to
    listPlayers, then write listPlayers to a save file.
    INPUTS: none, listPlayers and tableObj are both global variable.
    """
    # pdb.set_trace()
    endGame = False
    verifyChoice = False
    saveGame = False
    # Get all QUIT events.
    for event in pygame.event.get(QUIT):
        verifyChoice = True
        # verifyChoice means to check for exit.
        
    # Now, we need to check to see if ESCAPE was pressed or released. To
    # keep these event queues separate, we need to check them individualy.
    # We do this so that we can put all other KEYUPs and KEYDOWNs back into
    # their respective queues.
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            verifyChoice = True
        pygame.event.post(event)
    for event in pygame.event.get(KEYDOWN):
        if event.key == K_ESCAPE:
            verifyChoice = True
        pygame.event.post(event)
        
    # Now, we need to check for the case in which there are no players
    # remaining at the game table. In this case, it is possible that another
    # QUIT or ESCAPE event took place before the tableObj was created. So,
    # we will use try to make sure it exists first.
    try:
        type(tableObj)
    except:
        # There is no tableObj or it is corrupt.
        verifyChoice = True
    else:
        if tableObj.numPlayers == 0:
            verifyChoice = True
    
    # Now, we verify the choice.
    if verifyChoice == True:
        DISPLAYSURF.fill(BLACK)
        posX, posY = (WINCENTERX, WINCENTERY)
        instText = "Are you sure you want to exit?(Y/N)"
        instSurf = INSTRUCTFONT.render(instText, True, TEXTCOLOR)
        instRect = instSurf.get_rect(center = (posX, posY))
        DISPLAYSURF.blit(instSurf, instRect)
        pygame.display.update()
        posY += LINESPACING18
        answer = checkForYesNo(posX, posY, 'center')
        posY += LINESPACING18
        # answer will be True is Y was pressed, False if N is pressed.
        # True means the player wants to exit, but they may not want to
        # save their progress if the game did not go well. So, we set the
        # save boolean to False for now. If the answer was No, we return
        # to the calling function.
        if answer == True:
            endGame = True
            saveGame = False
        else:
            return
        # At this point, the player wants to exit, but they may want to save
        # their game after all.
        DISPLAYSURF.fill(BLACK)
        instText = "Do you want to save before exiting?(Y/N)"
        instSurf = INSTRUCTFONT.render(instText, True, TEXTCOLOR)
        instRect = instSurf.get_rect(center = (posX, posY))
        DISPLAYSURF.blit(instSurf, instRect)
        pygame.display.update()
        posY += LINESPACING18
        saveGame = checkForYesNo(posX, posY, 'center')
        if saveGame == True:
            # Note, this function does not care if players were eliminated or
            # were pulled from the game. Other function or methods would have
            # pulled or removed elimiated players at other times in the game.
            for i in xrange(1, MAXPLAYERS):
                try:
                    ordinal = TABLESEATS[str(i)]
                    checkName = tableObj.players[ordinal].name
                except:
                    # That ordinal (table position) was eliminated.
                    continue
                else:
                    for j in xrange(0, len(listPlayers)):
                        # If the names match, copy the bank amount to listPlayers.
                        if checkName == listPlayers[i]['name']:
                            listPlayers[i]['bank'] = tableObj.players[ordinal].bank
            writeSavedGame(listPlayers)
        terminate()
    return # checkForQuit

def checkForYesNo(posX = RIGHTMARGIN, posY = BOTTOMMARGIN, rectLocation = 'bottomright'):
    """
    This function watches for Y or N to be pressed.
    INPUTS: 3 optional arguments
        two optional positional arguments that control where the text
            instruction prints, default is bottom right corner
        rectLocation, string, indicates which of four possible paraments to
            use: topleft, topright, bottomleft, bottomright
        Note: There is also input from pygame.events.KEYDOWN events.
    OUTPUTS: True if Y was pressed, False is N was pressed.
    """
    displayRect = DISPLAYSURF.get_rect()
    while True:  # event loop
        # In the lower right corner, print this message.
        textSurf = DATAFONT.render("Press Y or N to respond.", True, TEXTCOLOR)
        textRect = textSurf.get_rect()
        if rectLocation == 'topleft':
            textRect.topleft = (posX, posY)
        elif rectLocation == 'topright':
            textRect.topright = (posX, posY)
        elif rectLocation == 'bottomleft':
            textRect.bottomleft = (posX, posY)
        else: # rectLocation == 'bottomright', the default value.
            textRect.bottomright = (posX, posY)
        DISPLAYSURF.blit(textSurf, textRect)
        
        for event in pygame.event.get(QUIT): # get all QUIT events
            terminate()                      # terminate if any QUIT events are present
        for event in pygame.event.get(KEYUP):# get all KEYUP events
            if event.key == K_ESCAPE:        # ESCAPE is also a 'quit' event
                terminate()

        for event in pygame.event.get():     # Removed KEYDOWN only type
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:    # These are also QUIT events.
                    terminate()
                elif event.key == K_y:
                    return True
                elif event.key == K_n:
                    return False
            # This stanza is an effort to make the game screen become active
            # after a change of focus.
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                active = displayRect.collidepoint(event.pos)
        pygame.display.update()
        FPSCLOCK.tick()
    return # checkForYesNo


def scrollText(filename):
    """
    This function displays scrolling text from a file one disk. If the file
    is not found, it will display an error message on screen instead.
    INPUTS: filename,a text file in etc.
    OUTPUTS: all outputs are on screen
    """
    installError = False
    # Clear the screen.
    DISPLAYSURF.fill(BLACK)
    # Extract a Rect object for the game screen. Normally, this is not needed.
    displayRect = DISPLAYSURF.get_rect()
    # We have no way of knowing if the program is installed correctly or if
    # that are any potiential rights issues that might crop up. So, we are
    # going to "try" to open the file for reading. The installError is a flag
    # we flip if something goes wrong reading the file.
    try:
        f = open(filename, 'r')
    except:
        installError = True
    if installError == True:
        instText = "scrollText: File {} not found or is not readable. Check installation of Casino Blackjack.".format(filename)
        instSurf = DATAFONT.render(instText, True, TEXTCOLOR)
        instRect = instSurf.get_rect(center = (WINCENTERX, WINCENTERY))
        DISPLAYSURF.blit(instSurf, instRect)
        pygame.display.update()
        pressSpaceToContinue()
        return
    # So, the file was found and is readable. We need to create a series of
    # lines of text which start out empty. As we read a line of text, it begin
    # at the bottom of the screen and scroll up by reducing swapping the text
    # to higher lines on the screen. That will make the text will scroll
    # upward, scrolling off eventually. It really shouuld not matter how many
    # lines are in the file either.
    
    # First, create the blanklines. LINESPACING for instruction text is 18pt
    # making the maximum number of lines on a 1024 screen 40. The text is so
    # large, barely 30 lines fit on screen.
    MAXLINESONSCREEN = 28
    # Now, we need a list of dictionary objects to make this easier to work
    # with. The format of each dictionary will be:
    #   'text'    : text content of the line
    #   'surface' : the surface object holding it
    #   'rect'    : the rect object containg the surface
    # We cannot include posX, posY in this dictionary because the positions
    # of the surfaces have to change on a regular cycle until the last line
    # of the file is read and printed on screen.
    textLines = []
    posX = LEFTMARGIN
    posY = TOPMARGIN
    for i in xrange(0, MAXLINESONSCREEN):
        textLine     = " ".format(i)
        textLineSurf = INSTRUCTFONT.render(textLine, True, TEXTCOLOR)
        textLineRect = textLineSurf.get_rect(topleft = (posX, posY))
        textLines.append({ 'text'    : textLine,
                           'surface' : textLineSurf,
                           'rect'    : textLineRect })
        DISPLAYSURF.blit(textLineSurf, textLineRect)
        if i < (MAXLINESONSCREEN - 1):
            posY += LINESPACING18
    lastLine = (posX, posY)
    pygame.display.update()
    FPSCLOCK.tick()
    # We now have some empty lines on screen. We need to start pulling in
    # a line of text and replacing lines to make it scroll up. The loop
    # shifts all of the lines up one position.
    for fileLine in f:
        # To keep this window active, we also need a loop in here to capture
        # pygame events.
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    # Allow the user to escape out when they have read as
                    # much text as they want to.
                    return
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    # This code keeps the game active when it is in focus.
                    active = displayRect.collidepoint(event.pos)
        # Clear the screen before each iteration.
        DISPLAYSURF.fill(BLACK)
        # Reset posY. posX is effectively a constant here.
        posY = TOPMARGIN
        for i in xrange(0, MAXLINESONSCREEN - 1):
            # We have to move the surface up one line. That means
            # changing the coordinates of the rect.topleft after
            # we copy the contents over.
            nextIndex = i + 1
            print("scrollText: textLines[{0}] equals {1}.".format(i, textLines[i]))
            textLines[i] = textLines[nextIndex]
            textLines[i]['rect'].topleft = (posX, posY)
            print("scrollText: textLines[{0}] equals {1}.".format(i, textLines[i]))
            print("scrollText: Blitting text {0} on screen.".format(textLines[i]['text']))
            DISPLAYSURF.blit(textLines[i]['surface'], textLines[i]['rect'])
            posY += LINESPACING18
        # Before we import the line from the file, we need to drop the newline
        # character at the end of the line.
        fileLineCleaned = string.strip(fileLine)
        # Now, we need to import the line of text from the file and create
        # irs initial surface and rect object. It will use lastLine as its
        # position. We also need to blit to the screen.
        fileLineSurf = INSTRUCTFONT.render(fileLineCleaned, True, TEXTCOLOR)
        fileLineRect = fileLineSurf.get_rect(topleft = (lastLine))
        DISPLAYSURF.blit(fileLineSurf, fileLineRect)
        # This removes the last line so we can append new data in its place.
        textLines.pop()
        textLines.append({  'text'    : fileLineCleaned,
                            'surface' : fileLineSurf,
                            'rect'    : fileLineRect })
        # We need to update the screen with these new text surfaces. We also
        # insert a pause to make is easier to read.
        pygame.display.update()
        pygame.time.wait(SCROLLSPEED)
    return # scrollText        



def playBlackjack():
    """
    This is the game loop for playing Blackjack at the user's choice of table.
    The tableObj takes care of the game play, thanks in no small part to the
    BlackjackClasses. Much of the functionality comes from those sources.
    The roundCounter actually determines if a player has played long enough
    to 'level up' in the game. The pattern for this is:
        STARTER = 50
        NORMAL  = 75
        SPECIAL = 100
    Once that number of rounds has been completed in a single game without
    busting, the player can move to the next level. The user can opt to pull
    a character with a dwindling bank instead of allowing them to bust. They
    won't be removed from the game that way.
    
    These constants indicate the number of rounds the player must finish in
    single game to move from that skill level to the next level. So, a
    STARTER player can move to the next level if they leave the game having
    played at least 50 rounds without breaking their bank. Once a player
    leaves a round, they cannot return to the game until the user has all
    remaining players bust or leave the table. This is how a player can level
    up without breaking the bank at a table.
    
    INPUTS: No arguments. All objects changed are global ones.
        tableObj, a CasinoTable object
        listPlayers. the global list of player dictionaries which must be
            updated as the game progresses
    OUTPUTS: listPlayers, updated with new bank amounts, removal of players who
        busted, and new table options (represented by the player's skill level)
    """
    roundCounter = 0
    #  Clear the screen.
    DISPLAYSURF.fill(BGCOLOR)
    posX = LEFTMARGIN
    posY = TOPMARGIN + LINESPACING12
    rulesText = "Would like to see the rules of Casino Blackjack and this game (Y/N)?"
    rulesSurf = BASICFONT.render(rulesText, True, TEXTCOLOR)
    rulesRect = rulesSurf.get_rect(topleft = (posX, posY))
    DISPLAYSURF.blit(rulesSurf, rulesRect)
    posY += LINESPACING18
    pygame.display.update()
    answer = checkForYesNo(posX, posY, 'topleft')
    # pdb.set_trace()
    if answer == True:
        scrollText('./etc/BlackJack-Rules.txt')
        pressSpaceToContinue()
        scrollText('./etc/Break-The-Bank-Rules.txt')
        pressSpaceToContinue()

    # Clear the screen again.
    DISPLAYSURF.fill(BLACK)
    pygame.display.update()
    endGame = False
    while not endGame:  # This is the actual game loop. main() sets it up.
        roundCounter += 1
        tableObj.phase = 'start'
        # First, we print the table, the dealer, and the players.
        DISPLAYSURF.fill(BGCOLOR)
        refreshTable(tableObj.phase, roundCounter)
        print("playBlackjack: tableObj contains {}".format(tableObj))
        print("playBlackjack: Current Status: phase = {}".format(tableObj.phase))
        # Before a round starts, the user may pull any player out of the
        # game to keep them from being eliminated, including all three.
        posX = LEFTMARGIN
        posY = TOPMARGIN
        leaveText = "Would you like to withdraw any players before this round starts?"
        leaveSurf = BASICFONT.render(leaveText, True, TEXTCOLOR)
        leaveRect = leaveSurf.get_rect(topleft = (posX, posY))
        DISPLAYSURF.blit(leaveSurf, leaveRect)
        posY += LINESPACING12
        pygame.display.update()
        # Clear the answer before resetting.
        answer = checkForYesNo(posX, posY, 'topleft')
        if answer == True:
            # We need to ask about each player that still remains in the
            # game. Note, we use seat here because we do not want to
            # use the global variable, seat that will be very
            # important in the player turns.
            posY += LINESPACING12
            for seat in TABLESEATS:
                if isPlayerStillThere(seat):
                    withdrawText = "Would like to withdraw {}?".format(tableObj.players[seat].name)
                    withdrawSurf = BASICFONT.render(withdrawText, True, TEXTCOLOR)
                    withdrawRect = withdrawSurf.get_rect(topleft = (posX, posY))
                    DISPLAYSURF.blit(withdrawSurf, withdrawRect)
                    pygame.display.update()
                    posY += LINESPACING12
                    answer = checkForYesNo(posX, posY, 'topleft')
                    if answer == True:
                        # This function alters the tableObj.
                        removeActivePlayer(seat, roundCounter)
                        print("playBlackjack: tableObj is now {0}. Number of players remaining: {1}.".format(tableObj, tableObj.numPlayers))
                    posY += LINESPACING12
                    
            # We need to offer the user a chance to save their players'
            # progress if they pulled all of their players from the table.
            if tableObj.numPlayers == 0:
                DISPLAYSURF.fill(BLACK)
                pygame.display.update()
                checkForQuit()
                print("playBlackjack: checkForQuit() completed.")
                # Even if the user does not want to quit, control must be
                # returned to main() to start a new game.
                return

        # There was a flaw in the logic that would lock a player in a
        # loop if the player had a non-zero bank, but one that is not
        # sufficient to make an ante bet. (It also effected insurance
        # and split hand bets.) Here, we prevent it by eliminating any
        # player that cannot make the ante bet.
        checkPlayerViability()

        # Now, the game will call for ante amounts for initial bets on the
        # hands. This also sets the maximum raise later in the round.
        # This is a very interactive phase of the round, requiring that
        # user ante up for each player. It will user another set of Textbox
        # objects to get each initial bet.
        tableObj.phase = 'ante'
        # Clear the screen and redraw the table.
        DISPLAYSURF.fill(BGCOLOR)
        pygame.display.update()
        refreshTable(tableObj.phase, roundCounter)
        for seat in TABLESEATS:
            if isPlayerStillThere(seat):
                while tableObj.players[seat].bet == 0:
                    tableObj.seat = seat
                    # This loop will continue until the player's ante
                    # is a valid amount. There are other functions that
                    # provide error messages, but not this one.
                    getBet()

        # Now, we refresh the screen to show the bets in place.
        DISPLAYSURF.fill(BGCOLOR)
        refreshTable(tableObj.phase, roundCounter)
        pygame.display.update()
        pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)

        # The next phase is dealing the cards. The first round of dealt
        # card includes the Dealer's hold (facedown) card.
        tableObj.phase = 'deal'
        # Deal first card.
        dealRound(roundCounter)
        # Deal second card.
        dealRound(roundCounter)

        # Now that all players (dealer included) have a full hand and any
        # player blackjacks have been resolved, we need to see if the
        # dealer has a ten value card or an ace showing. If so, the
        # players can bet on the dealer having a blackjack.
        checkForInsBet()

        # Next, we need to offer any players who have received a pair the
        # opportuntity to split their hand. Once that is done, a 21 for
        # either hand is not considered a blackjack. At best, it can tie
        # dealer if the dealer has non-blackjack.
        checkForPairs(roundCounter)

        # Now that all of the hands have been dealt, including split
        # hands, and ante bets have been placed on all existing hands,
        # it is time to offer the user the option of doubling down on
        # some of the better looking blackjack hands.
        tableObj.phase = 'raise'
        doubleDown(roundCounter)

        # Bets have been raised on all hands. It is time for the player
        # turns to begin. They will go counterclockwise, left, middle,
        # then right. For each playable hand, the player has the option
        # to hit or stand. Each time a card is dealt, the Player method
        # add_card_to_hand or add_card_to_split will update the results
        # dictionary with the status of their hand. The function
        # checkForHitStand works very similarly to checkForYesNo.
        # The function hitOrStand calls the others as it progresses.
        # When finished, it will return a value indicating how many
        # hands were still playable by the time the dealer's turn begins.
        # The value determines if a dealer automatically wins all 
        # remaining hands or has to actually play the turn.
        remainingHands, remainingPlayers = hitOrStand(roundCounter)

        # Now, it is time for the dealer's turn. This could change the
        # remainginPlayers as well.
        tableObj.phase = 'dealer'
        dealersTurn(remainingHands, remainingPlayers, roundCounter)

        # Now, we need to check to see if any players should have been
        # eliminated, but were spared for outstanding bets. This should
        # not happen, but it is a good idea to check anyway.
        # This code is designed to test findDefunctPlayer
       remainingPlayers = findDefunctPlayer()
            
        # Finally, we have the endOfRound. This resets function will reset
        # results, eliminate players who busted, reset hands and bets for
        # players who remain in the game.
        tableObj.phase = 'end'
        endOfRound(roundCounter)
        endGame = (tableObj.phase == 'postgame')
    # End of game while loop
    return # playBlackjack

def removeActivePlayer(seat, rounds):
    """
    This function removes a player from the table object, but updates their
    bank in listPlayers. This function is used with the player wants to
    withdraw a player between rounds.
    INPUTS: three arguments (listPlayers and tableObj are global objects)
        tableObj, a CasinoTable class object (global)
        seat, string, the player's seat at the table
        rounds, integer, the number of rounds the player played before
            being pulled from the table
    OUTPUTS: none
    Note: This function changes global object, tableObj, by removing a player.
    It also updates listPlayers with the player's bank.
    """
    # We need to match their name. The playerObj should have it. We need to
    # update the bank for that player once found. If they played sufficient
    # rounds, the player's skill should be updated as well.
    # pdb.set_trace()
    playerObj = tableObj.players[seat]
    for i in range(0, len(listPlayers)):
        if listPlayers[i]['name'] == playerObj.name:
            # Update the player's bank.
            listPlayers[i]['bank'] = playerObj.bank
            # Check to see if they played enough rounds to advance their skill.
            if listPlayers[i]['skill'] == 'starter' and rounds >= STARTER:
                listPlayers[i]['skill'] = 'normal'
            elif listPlayers[i]['skill'] == 'normal' and rounds >= NORMAL:
                listPlayers[i]['skill'] = 'special'
            elif listPlayers[i]['skill'] == 'special' and rounds >= SPECIAL:
                listPlayers[i]['skill'] = 'high'
    # Now, we need to remove that player from the tableObj. We also need to
    # reduce the number of players by 1. The only problem is that CasinoTable
    # objects do not easily delete items.
    newPlayerDict = {}
    for playerSeat in TABLESEATS:
        if isPlayerStillThere(playerSeat) and playerSeat != seat:
            newPlayerDict[playerSeat] = tableObj.players[playerSeat]
        # It will skip the player with the matching seat.
    tableObj.players = newPlayerDict            
    tableObj.numPlayers -= 1
    return # removeActivePlayer

def checkPlayerViability():
    """
    This function checks each player from the previous round or from a saved
    game to see if they can be meet the table minimum ante for the new round.
    If so, they will remain. If not, they are deleted.
    INPUTS: None
    OUTPUT: None. All changes are made to tableObj, a global object.
    """
    # First, we pull out the information that we need from the tableObj.
    tableMin = tableObj.min_bet
    for seat in TABLESEATS:
        if isPlayerStillThere(seat):
            # This seat is occupied. So, we need to determine if the player
            # is viable or will lock the game in a loop. Any player unable
            # to make their ante bet this round would break the game.

            # These variables have to be refreshed for each iteration.
            posX = LEFTMARGIN
            posY = TOPMARGIN
            playerName = tableObj.players[seat].name
            playerBank = tableObj.players[seat].bank
            if playerBank < tableMin:
                # This player is not viable.
                clearStatusCorner()
                warningTextFirst  = "{0} cannot make the ante. This player".format(playerName)
                warningTextSecond = "will be eliminated from the game."
                warningSurfFirst  = PROMPTFONT.render(warningTextFirst, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                warningSurfSecond = PROMPTFONT.render(warningTextSecond, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                warningRectFirst  = warningSurfFirst.get_rect(topleft = (posX, posY))
                posY += LINESPACING12
                warningRectSecond = warningSurfSecond.get_rect(topleft = (posX, posY))
                DISPLAYSURF.blit(warningSurfFirst, warningRectFirst)
                DISPLAYSURF.blit(warningSurfSecond, warningRectSecond)
                pygame.display.update()
                pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
                eliminatePlayer(seat)
            continue
    return # checkPlayerViability

def refreshTable(phase, rounds):
    """
    This function refreshes the player/dealer data, cards dealt, and game
    as the game round progresses. It uses the phase of the round to determine
    what should print out of the Dealer's cards and data. This function uses
    phase, a string with one of the following values:
        'pregame': setting up for a game (not used here)
        'start'  : allows the user to withdraw players before ante
        'ante'   : collecting initial bets from players
        'deal'   : dealing the cards
        'raise'  : the players have an opportunity to double down before
                    playing their hands
        'left'   : left player's turn (must be one)
        'middle' : middle player's turn (if there is one)
        'right'  : right player's turn (if there is one)
        'dealer' : dealer's turn
        'end'    : end of the current round (clean up phase)
    INPUTS: two arguments
        phase. string, see above for valid values
        rounds, integer (round number of the current game)
    NOTE: This function does NOT clear the screen before printing, because
    thst is often not required.
    """
    # Start with a full board clear.
    DISPLAYSURF.fill(BGCOLOR)
    generateTable(tableChoice['table color'])
    if phase != 'dealer':
        printTableDealer(tableObj.tableDealer.extract_data())
    else:
        printTableDealer(tableObj.tableDealer.extract_data(), 'dealer turn')
    for seat in TABLESEATS:
        if isPlayerStillThere(seat):
            printTablePlayer(tableObj.players[seat].extract_data(), seat)
    if phase == 'start':
        roundText = "Currently starting Round {0}.".format(rounds)
    elif phase == 'ante':
        roundText = "Currently anteing up for Round {0}.".format(rounds)
    elif phase == 'deal':
        roundText = "Currently dealing cards in Round {0}.".format(rounds)
    elif phase == 'raise':
        roundText = "Currently offering double down in Round {0}.".format(rounds)
    elif phase == 'left':
        roundText = "Currently {0}'s turn in Round {1}.".format(tableObj.players['left'].name, rounds)
    elif phase == 'middle':
        roundText = "Currently {0}'s turn in Round {1}.".format(tableObj.players['middle'].name, rounds)
    elif phase == 'right':
        roundText = "Currently {0}'s turn in Round {1}.".format(tableObj.players['right'].name, rounds)
    elif phase == 'dealer':
        roundText = "Currently {0}'s turn in Round {1}.".format(tableObj.tableDealer.name, rounds)
    elif phase == 'end':
        roundText = "End of round {0}.".format(rounds)
    posX = RIGHTMARGIN
    posY = TOPMARGIN
    roundSurf = DATAFONT.render(roundText, True, TEXTCOLOR)
    roundRect = roundSurf.get_rect(topright = (posX, posY))
    DISPLAYSURF.blit(roundSurf, roundRect)
    # New functionality added to inform the user on the table aspects min
    # bet, max bet, and blackjack multiplier.
    posY += LINESPACING12
    tableMin = tableObj.min_bet
    tableMax = tableObj.max_bet
    blackjackRatio, blackjackFloat = tableObj.blackjack_multiplier
    minBetText = "Table minimum:    ${:7d}.".format(tableMin)
    maxBetText = "Table maximum:    ${:7d}.".format(tableMax)
    minBetSurf = DATAFONT.render(minBetText, True, TEXTCOLOR)
    maxBetSurf = DATAFONT.render(maxBetText, True, TEXTCOLOR)
    minBetRect = minBetSurf.get_rect(topright = (posX, posY))
    posY += LINESPACING12
    maxBetRect = maxBetSurf.get_rect(topright = (posX, posY))
    posY += LINESPACING12
    DISPLAYSURF.blit(minBetSurf, minBetRect)
    DISPLAYSURF.blit(maxBetSurf, maxBetRect)
    blackjackMultTextFirst  = "Blackjack Multiplier: {:>4}.".format(blackjackRatio)
    blackjackMultTextSecond = "Decimal Equivalent:   {:4.2f}.".format(blackjackFloat)
    blackjackMultSurfFirst  = DATAFONT.render(blackjackMultTextFirst, True, TEXTCOLOR)
    blackjackMultSurfSecond = DATAFONT.render(blackjackMultTextSecond, True, TEXTCOLOR)
    blackjackMultRectFirst  = blackjackMultSurfFirst.get_rect(topright = (posX, posY))
    posY += LINESPACING12
    blackjackMultRectSecond = blackjackMultSurfSecond.get_rect(topright = (posX, posY))
    posY += LINESPACING12
    DISPLAYSURF.blit(blackjackMultSurfFirst, blackjackMultRectFirst)
    DISPLAYSURF.blit(blackjackMultSurfSecond, blackjackMultRectSecond)
    pygame.display.update()
    return # refreshTable

def isPlayerStillThere(seat):
    """
    This function checks to see if a player occupies a particular seat at the
    game table. Returns True if so, False otherwise. It uses "seat" to prevent
    any changes to global seat.
    INPUTS: seat, a string with values 'left', 'middle', or 'right'
    OUTPUTS: boolean, True if occupied, False otherwise.
    """
    # Some player positions may be empty.
    print("isPlayerStillThere: Status: seat is {0}.".format(seat))
    try:
        playerName = tableObj.players[seat].name
    except:
        # Player position is empty. Skip it.
        print("isPlayerStillThere: No player at seat {}. Skipping it.".format(seat))
        # pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
        return False
    else:
        print("isPlayerStillThere: Player {0} is in seat {1}.".format(playerName, seat))
        # pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
        return True

def getBet(betType = 'reg'):
    """
    This function leverages the Textbox class to create a numbers only textbox
    for the user to enter their bet amount. If the phase is 'ante', it will
    check that the bet falls between the table max and min bets. If the phase
    is 'left', 'right', or 'middle' (the player's turn), it will check the
    bet amount against their original bet to see that it does not exceed that
    original bet (double down).
    
    If the split flag is True and the phase is 'deal', this is the split hand
    ante bet. The table max and min apply to it as well. If the split flag is
    True and the phase is a player's turn, then it is a double down bet on the
    split hand, which cannot exceed the previous bet amount for the split hand.

    The functions each option calls is actually the function, handleBet().
    The actual functions called by the Textbox objects are wrappers to ensure
    that split can be transmitted to handleBet() successfully.

    INPUTS: seat, a string indicating the player's position
            split, boolean, True for split hand, False for regular hand
    OUTPUTS: All outputs are made to tableObj.
    """
    print("getBet: Status (tableObj): phase is {0}. seat is {1}. name is {2}.".format(tableObj.phase, tableObj.seat, tableObj.players[tableObj.seat].name))
    partOfRound = tableObj.phase
    seat = tableObj.seat
    playerName = tableObj.players[seat].name
    print("getBet: Status: partOfRound is {0}. seat is {1}. playerName is {2}.".format(partOfRound, seat, playerName))
    posX = LEFTMARGIN
    posY = TOPMARGIN
    # First, we need to clear any text from the STATUSBLOCK in the upper left
    # corner of the screen.
    clearStatusCorner()

    if partOfRound == 'ante':
        print("getBet: Status: Starting regular ante bet for {0}.".format(playerName))
        # This is an initial ante before any cards are dealt.
        anteText = "{0}, please ante up for this round.".format(playerName)
        anteSurf = PROMPTFONT.render(anteText, True, TEXTCOLOR)
        anteRect = anteSurf.get_rect(topleft = (posX, posY))
        posY += LINESPACING18
        betTextboxRect = anteRect.copy()
        betTextboxRect.topleft = (posX, posY)
        betTextbox = Textbox((betTextboxRect), fontSize = 12, command = handleRegBet,
                             charFilter = 'number', enterClears = True, enterDeactivates = True)
        betResult = getTextboxEvents(betTextbox, anteSurf, anteRect, DISPLAYSURF)

    elif partOfRound == 'deal' and betType == 'split':
        print("getBet: Status: Starting split ante bet for {0}.".format(playerName))
        # This is the ante for a split hand. It takes place while cards are
        # still being dealt.
        anteText = "{0}, please ante up for your split hand.".format(playerName)
        anteSurf = PROMPTFONT.render(anteText, True, TEXTCOLOR)
        anteRect = anteSurf.get_rect(topleft = (posX, posY))
        posY += LINESPACING18
        betTextboxRect = anteRect.copy()
        betTextboxRect.topleft = (posX, posY)
        betTextbox = Textbox((betTextboxRect), fontSize = 12, command = handleSplitBet,
                             charFilter = 'number', enterClears = True, enterDeactivates = True)
        betResult = getTextboxEvents(betTextbox, anteSurf, anteRect, DISPLAYSURF)

    elif partOfRound == 'raise' and betType == 'reg':
        print("getBet: Status: Starting raise bet for {0}.".format(playerName))
        # This is a double down for a regular hand.
        doubleDownText = "{0}, how much would you like to raise your bet by?".format(playerName)
        doubleDownSurf = PROMPTFONT.render(doubleDownText, True, TEXTCOLOR)
        doubleDownRect = doubleDownSurf.get_rect(topleft = (posX, posY))
        posY += LINESPACING18
        betTextboxRect = doubleDownRect.copy()
        betTextboxRect.topleft = (posX, posY)
        betTextbox = Textbox((betTextboxRect), fontSize = 12, command = handleRegBet,
                             charFilter = 'number', enterClears = True, enterDeactivates = True)
        betResult = getTextboxEvents(betTextbox, doubleDownSurf, doubleDownRect, DISPLAYSURF)

    elif partOfRound == 'raise' and betType == 'split':
        print("getBet: Status: Starting raise split bet for {0}.".format(playerName))
        # This is a double down on a split hand.
        doubleDownText = "{0}, how much would you like to raise your bet on your split hand by?".format(playerName)
        doubleDownSurf = PROMPTFONT.render(doubleDownText, True, TEXTCOLOR)
        doubleDownRect = doubleDownSurf.get_rect(topleft = (posX, posY))
        posY += LINESPACING18
        betTextboxRect = doubleDownRect.copy()
        betTextboxRect.topleft = (posX, posY)
        betTextbox = Textbox((betTextboxRect), fontSize = 12, command = handleSplitBet,
                             charFilter = 'number', enterClears = True, enterDeactivates = True)
        betResult = getTextboxEvents(betTextbox, doubleDownSurf, doubleDownRect, DISPLAYSURF)

    elif betType == 'ins':
        print("getBet: Status: Starting insurance bet for {0}.".format(playerName))
        # This is an insurance bet.
        insText = "{0}, how much do you want to wager as an insurance bet?".format(playerName)
        insSurf = PROMPTFONT.render(insText, True, TEXTCOLOR)
        insRect = insSurf.get_rect(topleft = (posX, posY))
        posY += LINESPACING18
        betTextboxRect = insRect.copy()
        betTextboxRect.topleft = (posX, posY)
        betTextbox = Textbox((betTextboxRect), fontSize = 12, command = handleInsBet,
                             charFilter = 'number', enterClears = True, enterDeactivates = True)
        betResult = getTextboxEvents(betTextbox, insSurf, insRect, DISPLAYSURF)
        
    return # getBet

def handleBet(id, betAmt, betType):
    """
    This function uses a text flag and the tableObj.phase variable to
    determine which Player method to call to perform the operation. The
    operations include taking an ante bet on a player's hand, regular and
    split, taking double down increases to the same, and taking insurance
    bets when it is called for. The Player class methods can check the
    amounts to make sure they are valid. If the amount is invalid or is not
    a number, this function print an error message, and returns control back
    to the calling function. That calling function will need a while loop that
    loops until the desired tableObj attribute has been changed.
    
    It calls the Player.update_bet() and update_split_bet() methods and checks
    the code to determine the right response to bad amounts. Their return
    codes are:
            'success'   = the bet could be increased
            'bust'      = the bet exceeds the money in the bank
            'size'      = the bet is not allowed because it exceeds double the
                        original bet
            'min'       = the bet is not enough to meet the casino minimums
            'max'       = the bet exceeds the max allowed initial bet
            'TypeError' = at least one 'numerical' argument supplied was not a
                        number
            'Unknown'   = an unknown error occurred

    INPUTS: three arguments
        id     : integer, the location of the calling process in memory
        betAmt : string to convert into an integer
        betType: string with the following values:
            'reg'  : this bet is on the regular hand
            'split': this bet is on the split hand
            'ins'  : this is an insurance bet on the dealer's hand
    OUTPUTS: All outputs are changes to the global tableObj
    Note: The Textbox objects have filters to prevent undesirable characters
    from being entered in the dialog box.
    Note: This function is called by the command run by the Textbox objects
    collecting the bet information, handleRegBet, handleSplitBet, updateBet
    and updateSplitBet.
    """
   # There is a possiblity that the user will hit return prematurely. We
    # need to be prepared for that possibility.
    try:
        betAmt = int(betAmt)
    except:
        return
    tableMin = tableObj.min_bet
    tableMax = tableObj.max_bet
    seat = tableObj.seat
    partOfRound = tableObj.phase
    maxRegRaise   = tableObj.players[seat].bet
    maxSplitRaise = tableObj.players[seat].split_bet
    playerName = tableObj.players[seat].name
    print("handleBet: Status: tableMin is ${0}. tableMax is ${1}.".format(tableMin, tableMax))
    print("handleBet: Status: seat is {0}. phase is {1}. playerName is {2}.".format(seat, partOfRound, playerName))
    print("handleBet: Status: maxRegRaise is ${0}. maxSplitRaise is ${1}.".format(maxRegRaise, maxSplitRaise))
    # The first thing we need to do after the user hits return in the Textbox
    # is to clear the status block.
    clearStatusCorner()
    
    # This alligns the "on screen response", either confirming a valid bet
    # or giving instruction on what would be an acceptable bet.
    posX = LEFTMARGIN
    posY = TOPMARGIN

    # First, we check to see if this an ante bet (before cards are dealt).
    if betType == 'reg' and partOfRound == 'ante':
        print("handleBet: Applying regular ante bet {0} for Player {1}.".format(betAmt, playerName))
        # We have to check the validity of the bet. Note, a result of 'size'
        # is only possible when doubling down.
        result = tableObj.players[seat].update_bet(betAmt, tableMin, tableMax)
        print("handleBet: result returned by update_bet is {0}.".format(result))
        if result == 'success':
            # Bet is valid. The tableObj has been updated.
            responseText = "Thank you and good luck, {}.".format(playerName)
            
        # The bet is not a valid ante amount. We need to send an error
        # message.
        elif result in ('min', 'max'):
            responseText = "Invalid ante bet. Min bet is ${:d}. Max bet is ${:d}.".format(tableMin, tableMax)
        elif result == 'bust':
            # The amount, including all other bets, exceeds the player's bank.
            responseText = "Your bank cannot cover that bet."
        else:
            # Code Unknown. TypeError should not be possible with number
            # filters turned on in the Textbox.
            responseText = "An error occurred trying to apply the ante."

        # There is a loop in the original calling function, playBlackjack,
        # that will attempt to get a valid bet again.
            
    # Next, we check if this is a double down on a player's regular bet.
    # First we check the regular bet. The player can raise it zero up to
    # double their original ante on the hand.
    elif partOfRound == 'raise' and betType == 'reg':
        print("handleBet: Applying raise to regular bet {0} for Player {1}.".format(betAmt, playerName))
        # First, we eliminate the zero raises.
        if betAmt == 0:
            # This bet amount is treated as if the user changed their mind
            # about raising the bet.
            responseText = "Changing your mind can be wise. Good luck, {}.".format(playerName)
            # We need to set the raise flag for the bet as well.
            tableObj.players[seat].raise_bet = True
            result = None
        else: # The raise is non-zero.
            result = tableObj.players[seat].double_down(betAmt, False)
            if result == 'success':
                # The raise amount is valid. The player methods update_bet
                # and double_down have updated the bet attribute already.
                # We just need to respond with an acceptance and set the
                # raise_bet flag.
                responseText = "Thank you and good luck, {}.".format(playerName)
                tableObj.players[seat].raise_bet = True
            elif result == 'bust':
                # The player's bank cannot cover the increase.
                responseText = "Your bank cannot cover the new regular bet."
            elif result == 'size':
                # The bet is outside the range of 0 to the original ante.
                responseText = "Invalid raise. Min is $0. Max is {0}.".format(maxRegRaise)
            else: # Some kind of error occurred that try captured. 
                responseText = "An error occurred trying to raise the bet."
        print("handleBet: result returned by update_bet is {0}. Raise flag is {1}.".format(result, tableObj.players[seat].raise_bet))
    
    # Next, we check if this is a double down on a player's existing split
    # bet. First we check the regular bet. The player can raise it zero up to
    # double their original ante on the hand.
    elif partOfRound == 'raise' and betType == 'split':
        print("handleBet: Applying raise to split bet {0} for Player {1}.".format(betAmt, playerName))
        # First, as with raising the regular bet, we eliminate the zero raises.
        if betAmt == 0:
            # Again, this is taken as the "player" changing their mind.
            responseText = "Changing your mind can be wise. Good luck, {}.".format(playerName)
            # Like the reg bet, we still need to flip the raise flag for this
            # bet.
            tableObj.players[seat].raise_split_bet = True
            result = None
        else: # The raise is non-zero.
            result = tableObj.players[seat].double_down(betAmt, True)
            if result == 'success':
                # The raise amount is valid. The player methods, 
                # update_split_bet and double_down have updated the split_bet
                # attribute already. We just need to respond with an
                # acceptance and set the raise_split_bet flag.
                responseText = "Thank you and good luck, {}.".format(playerName)
                tableObj.players[seat].raise_split_bet = True 
            elif result == 'bust':
                # Their bank could not cover the amount.
                responseText = "Your bank cannot cover the new split bet."
            elif result == 'size':
                # The raise exceeded the original bet.
                responseText = "Invalid raise. Min is $0. Max is {0}.".format(maxSplitRaise)
            else:
                # Code Unknown. TypeError should not be possible with number
                # filters turned on in the Textbox.
                responseText = "An error occurred trying to raise the split bet."
        print("handleBet: result returned by update_split_bet is {0}. Raise flag is {1}.".format(result, tableObj.players[seat].raise_split_bet))
            
        # There is a loop in the original calling function, playBlackjack,
        # that will attempt to get a valid bet again.

    # Next, we deal with the ante on a split hand. It is created while during
    # the initial deal (after a second card has been dealt to all players).
    # Note: Insurance bets cannot be raised.
    elif betType == 'split' and partOfRound == 'deal':
        print("handleBet: Applying split ante bet {0} for Player {1}.".format(betAmt, playerName))
        # We have to check the validity of the bet. Split bets still have to
        # adhere to tableMax and tableMin.
        result = tableObj.players[seat].update_split_bet(betAmt, tableMin, tableMax)
        print("handleBet: result returned by update_split_bet is {0}.".format(result))
        if result == 'success':
            # Bet is valid. The tableObj has been updated.
            responseText = "Thank you and good luck, {}.".format(playerName)
            
        # The bet is not a valid ante amount. We need to send an error
        # message.
        elif result in ('min', 'max'):
            responseText = "Invalid ante bet. Min bet is ${:d}. Max bet is ${:d}.".format(tableMin, tableMax)
        elif result == 'bust':
            # The amount, including all other bets, exceeds the player's bank.
            responseText = "Your bank cannot cover that bet."
        else:
            # Code Unknown. TypeError should not be possible with number
            # filters turned on in the Textbox.
            responseText = "An error occurred trying to apply the split ante."
            
        # There is a loop in the original calling function, playBlackjack,
        # that will attempt to get a valid bet again.

    # Finally, we deal with the case that all hands have been dealt and the
    # Dealer is showing a ten value or Ace. This means that the dealer had to
    # offer an insurance bet. This only happens after 'deal' is over and before
    # 'raise' starts.
    elif betType == 'ins':
        print("handleBet: Applying insurance bet {0} for Player {1}.".format(betAmt, playerName))
        # Insurance bets abide by the same table limits as any other bet.
        result = tableObj.players[seat].update_ins(betAmt, tableMin, tableMax)
        print("handleBet: result returned by update_ins is {0}.".format(result))
        if result == 'success':
            # Bet is valid. The tableObj has been updated.
            responseText = "Excellent choice. Good luck, {}.".format(playerName)

        # Something is wrong with the bet.
        elif result == 'exists':
            responseText = "You cannot raise an insurance bet."
        elif result in ('min', 'max'):
            responseText = "Invalid insurance bet. Min bet is ${:d}. Max bet is ${:d}.".format(tableMin, tableMax)
        elif result == 'bust':
            # The amount, including all other bets, exceeds the player's bank.
            responseText = "Your bank cannot cover that bet."
        else:
            # Code Unknown. TypeError should not be possible with number
            # filters turned on in the Textbox.
            responseText = "An error occurred trying to apply the insurance bet."

        # There is a loop in the original calling function, playBlackjack,
        # that will attempt to get a valid bet again.

    # This block prints the response, then pauses waiting for the user to hit
    # the spacebar.
    responseSurf = BASICFONT.render(responseText, True, TEXTCOLOR)
    responseRect = responseSurf.get_rect(topleft = (posX, posY))
    DISPLAYSURF.blit(responseSurf, responseRect)
    pygame.display.update()
    pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
    clearStatusCorner()
    pygame.display.update()
    return # handleBet

def handleRegBet(id, betAmt):
    """
    This is a wrapper function for handldBet(). It allows us to pass an
    argument to handleBet telling it what kind of bet this is.
    INPUTS: two arguments
        id : integer memory address of the process
        betAmt : text from the Textbox object
    OUTPUTS: None. This does not write to the screen, either. It simply runs
        handleBet with betType = 'reg'
    """
    handleBet(id, betAmt, 'reg')
    return

def handleSplitBet(id, betAmt):
    """
    This is a wrapper function for handldBet(). It allows us to pass an
    argument to handleBet telling it what kind of bet this is.
    INPUTS: two arguments
        id : integer memory address of the process
        betAmt : text from the Textbox object
    OUTPUTS: None. This does not write to the screen, either. It simply runs
        handleBet with betType = 'split'
    """
    handleBet(id, betAmt, 'split')
    return

def handleInsBet(id, betAmt):
    """
    This is a wrapper function for handldBet(). It allows us to pass an
    argument to handleBet telling it what kind of bet this is.
    INPUTS: two arguments
        id : integer memory address of the process
        betAmt : text from the Textbox object
    OUTPUTS: None. This does not write to the screen, either. It simply runs
        handleBet with betType = 'ins'
    """
    handleBet(id, betAmt, 'ins')
    return


def dealRound(rounds):
    """
    This function deal a round of cards to each player, including the dealer.
    It uses the Player.add_card_to_hand() method to (which the Dealer also
    has) to add cards to their hands. Both methods return strings 'blackjack',
    'playable', or 'bust' each time a new card is added. It also uses the
    CardShoe.remove_top() to produce the card to be dealt. The results of each
    card dealt are stored in tableObj.results. This is a nested dictionary
    object. The keys point to:
        'left reg'     : player in left seat, regular hand
        'left split'   : player in left seat, split hand
        'middle reg'   : player in middle seat, regular hand
        'middle split' : player in middle seat, split hand
        'right reg'    : player in right seat, regular hand
        'right split'  : player in right seat, split hand
        'dealer reg'   : dealer's hand
    The statuses for these hands are:
        'blackjack'    : natural 21
        'playable'     : the hand is still playable
        'bust'         : the hand busted
        'none'         : this hand does not exist
    INPUTS: rounds, integer, the number of the current game round
    OUTPUTS: only on screen and tableObj changes
    """
    # Clear the screen.
    DISPLAYSURF.fill(BGCOLOR)
    pygame.display.update()
    posX = LEFTMARGIN
    posY = TOPMARGIN
    blackjackMultiplier = tableObj.blackjack_multiplier[1]
    if len(tableObj.tableDealer.hand) == 0:
        statusText = "Dealing first round of cards."
    else:
        statusText = "Dealing second round of cards."
    statusSurf = BASICFONT.render(statusText, True, TEXTCOLOR)
    statusRect = statusSurf.get_rect(topleft = (posX, posY))
    DISPLAYSURF.blit(statusSurf, statusRect)
    pygame.display.update()
    posY += LINESPACING18
    for seat in TABLESEATSALL:
        # Removing a card from the top of the deck has to take place after
        # a player has been verified present to receive it.
        if seat != 'dealer':
            if isPlayerStillThere(seat):
                # Draw and deal if the seat is occupied.
                card = tableObj.deck.remove_top()
                tableObj.results[seat + ' reg'] = tableObj.players[seat].add_card_to_hand(card)
        else: # Seat is the dealer's, which is always occupied during the game.
            card = tableObj.deck.remove_top()
            tableObj.results[seat + ' reg'] = tableObj.tableDealer.add_card_to_hand(card)
    refreshTable(tableObj.phase, rounds)
    pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
    # Print out and deal with all blackjack results from the players. This is
    # now an attribute of the class CasinoTable. The dealer having a hidden
    # blackjack will dealt with on the Dealer's turn.
    for seat in TABLESEATS:
        dealerLosses = 0
        if tableObj.results[seat + ' reg'] == 'blackjack':
            winnings = int(tableObj.players[seat].bet * blackjackMultiplier)
            dealerLosses += winnings
            blackjackTextFirst  = "Congratulations, {}. You have a blackjack".format(tableObj.players[seat].name) 
            blackjackTextSecond = "that paid out ${}.".format(winnings)
            blackjackSurfFirst  = SCOREFONT.render(blackjackTextFirst, True, TEXTCOLOR)
            blackjackRectFirst  = blackjackSurfFirst.get_rect(topleft = (posX, posY))
            DISPLAYSURF.blit(blackjackSurfFirst, blackjackRectFirst)
            posY += LINESPACING12
            blackjackSurfSecond = SCOREFONT.render(blackjackTextSecond, True, TEXTCOLOR)
            blackjackRectSecond = blackjackSurfSecond.get_rect(topleft = (posX, posY))
            DISPLAYSURF.blit(blackjackSurfSecond, blackjackRectSecond)
            pygame.display.update()
            posY += LINESPACING12
            # We need to add the winning to the player's bank. This method
            # does it for us.
            tableObj.players[seat].blackjack(blackjackMultiplier)
            pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
        # Now, we need to deduct the immediate losses the dealer suffered
        # from player blackjacks. The method below returns True if the
        # Dealer's bank survived the losses, False if this round of player
        # wins breaks the bank.
        dealerBreak = tableObj.tableDealer.dealer_lost(dealerLosses)
        if dealerBreak == False:
            playersWinGame()
    return # dealRound

def checkForInsBet():
    """
    This function looks at the Dealer attribute, blackjack_flag. It will be
    true if the Dealer's visible card is a ten, a face card, or an ace. That
    means that the player's can bet on whether or not the dealer has a 21.
    This function calls getBet with 'ins' option for betType.
    Note: Even players who scored a blackjack (which would have been resolved
    by this point in the game) can opt to bet on a dealer blackjack and win a
    'second' time.
    INPUTS: None
    OUTPUTS: None
    """
    # Initialize variables used to determine if a play can cover the table
    # minimum for an insurance bet.
    playerTotalBets = 0
    tableMin = tableObj.min_bet
    playerBank = 0
    
    # First, clear the corner of the screen.
    clearStatusCorner()

    print("checkForInsBet: Blackjack Flag is {}.".format(tableObj.tableDealer.blackjack_flag))
    blackjackFlag = tableObj.tableDealer.blackjack_flag
    visCard = tableObj.tableDealer.visible_card[0]
    posX = LEFTMARGIN
    posY = TOPMARGIN
    if blackjackFlag == True:
        rank, suit = visCard
        if rank == 'K':
            cardName = 'a king'
        elif rank == 'Q':
            cardName = 'a queen'
        elif rank == 'J':
            cardName = 'a jack'
        elif rank == '10':
            cardName = 'a ten'
        else: # Card is an Ace.
            cardName = 'an ace'
        insBetAckTextFirst  = "Since I have {0} showing, would anyone like".format(cardName)
        insBetAckTextSecond = "to place an insurance bet on my possible blackjack?"
        insBetAckSurfFirst  = PROMPTFONT.render(insBetAckTextFirst, True, TEXTCOLOR)
        insBetAckRectFirst  = insBetAckSurfFirst.get_rect(topleft = (posX, posY))
        DISPLAYSURF.blit(insBetAckSurfFirst, insBetAckRectFirst)
        posY += LINESPACING12
        insBetAckSurfSecond = PROMPTFONT.render(insBetAckTextSecond, True, TEXTCOLOR)
        insBetAckRectSecond = insBetAckSurfSecond.get_rect(topleft = (posX, posY))
        DISPLAYSURF.blit(insBetAckSurfSecond, insBetAckRectSecond)
        pygame.display.update()
        posY += LINESPACING12
        answer = checkForYesNo(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
        pygame.display.update()
        # If the user does not want the players to make insurance bets, this
        # function will return to playBlackjack.
        if answer == False:
            return

        # Since we cleaned the corner again already, we can reset the position.
        posX = LEFTMARGIN
        posY = TOPMARGIN
        # We need ask each "player" if they want to place an insurance bet.
        for seat in TABLESEATS:
            # We need to reset the variables used to determine if a player
            # can cover an insurance bet each iteration of the for loop.
            playerTotalBets = 0
            # We need to clear the corner between loops. The statusSurf is the
            # entire upper left corner.
            clearStatusCorner()
            posY = LEFTMARGIN
            # We have to make sure a player is in the seat.
            if isPlayerStillThere(seat):
                # Since the player is still in the seat, we can reset two
                # more variables.
                playerName = tableObj.players[seat].name
                playerBank = tableObj.players[seat].bank
                playerTotalBets = tableObj.players[seat].total_bets()
                print("checkForInsBet: Seat is set to {}.".format(seat))
                print("checkForInsBet: Players is now {}.".format(playerName))
                # We have to make sure that the player can cover the table
                # minimum for an insurance bet before asking them if they
                # want to make one.
                if playerTotalBets + tableMin >= playerBank:
                    insBetTextFirst  = "{0}, you have insufficient money remaining".format(playerName)
                    insBetTextSecond = "to cover the table minimum for an insurance bet."
                    insBetSurfFirst  = PROMPTFONT.render(insBetTextFirst, True, TEXTCOLOR)
                    insBetRectFirst  = insBetSurfFirst.get_rect(topleft = (posX, posY))
                    DISPLAYSURF.blit(insBetSurfFirst, insBetRectFirst)
                    posY += LINESPACING12
                    insBetSurfSecond = PROMPTFONT.render(insBetTextSecond, True, TEXTCOLOR)
                    insBetRectSecond = insBetSurfSecond.get_rect(topleft = (posX, posY))
                    DISPLAYSURF.blit(insBetSurfSecond, insBetRectSecond)
                    pygame.display.update()
                    pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
                    # Skip this player.
                    continue
                insBetText = "{}, would you like to place an insurance bet?.".format(playerName)
                insBetSurf = PROMPTFONT.render(insBetText, True, TEXTCOLOR)
                insBetRect = insBetSurf.get_rect(topleft = (posX, posY))
                DISPLAYSURF.blit(insBetSurf, insBetRect)
                pygame.display.update()
                posY += LINESPACING18
                answer = checkForYesNo(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
                if answer == True:
                    while tableObj.players[seat].insurance == 0:
                        tableObj.seat = seat
                        getBet('ins')
                        print("checkForInsBet: Player {0} placed an insurance bet of ${1}.".format(playerName, tableObj.players[seat].insurance))
    return # checkForInsBet

def checkForPairs(rounds):
    """
    This function checks for pairs in the players dealt hands. Each player
    that has a pair will be offered the option of splitting their hand into
    two hands. From that point on, even a 21 from 2 cards cannot be considered
    a blackjack result.

    This function uses Player.split_check(), which returns True when a pair
    exists, False otherwise. Once a pair is found, it will ask the player who
    has the pair if they want to split their hand. If so, it will call the
    Player.split_pair() method. After that, it will call for a bet on this
    new hand, called a split hand.

    Neither Player method requires arguments, but refreshTable needs the 
    phase and round count. The phase can come from tableObj, but rounds has 
    to be passed through from playBlackjack.

    There is an error condition that came in development. This function needs
    to verify that the player can meet the table minimum before allowing them
    to split their hand. Otherwise, the game will be stuck in a loop.

    INPUTS: integer rounds (number of the current round)
    OUTPUTS: Only to the screen
    """
    # Initializing variables used to determine if a player can ante up with
    # their current bets already made. Some of these variables will be reset
    # each time the for loop iterates.
    playerTotalBets = 0
    tableMin = tableObj.min_bet
    playerBank = 0
    # First, we need to clear the corner of the screen.
    clearStatusCorner()
    # Next, we need to check each regular hand for pairs. We also need to
    # make sure a player is still in the seat.
    for seat in TABLESEATS:
        # Resetting playerTotalBets for the next iteration.
        playerTotalBets = 0
        if isPlayerStillThere(seat) and tableObj.results[seat + ' reg'] == 'playable':
            # The player needs to exist before we can set these variables.
            playerName = tableObj.players[seat].name
            playerBank = tableObj.players[seat].bank
            print("checkForPairs: seat is {0}. Player is {1}.".format(seat, tableObj.players[seat].name))
            pairExists = tableObj.players[seat].split_check()
            if pairExists == True:
                posX = LEFTMARGIN
                posY = TOPMARGIN
                clearStatusCorner()
                # An serious problem develops with players running on very
                # low balance banks: They can trap the game in a loop in
                # the player has to ante up, but does not have enough money
                # left to do so. In this case, we need to trap that error by
                # making sure that the player can ante up before offering to
                # split their hand.  canAnte is the boolean flag for this.
                # It is initialized to False for each player and when this
                # function is called.
                playerTotalBets = tableObj.players[seat].total_bets()
                if playerTotalBets + tableMin >= playerBank:
                    splitHandTextFirst  = "{0}, you have insufficient money remaining".format(playerName)
                    splitHandTextSecond = "to cover the table minimum ante on a split hand."
                    splitHandSurfFirst  = PROMPTFONT.render(splitHandTextFirst, True, TEXTCOLOR)
                    splitHandRectFirst  = splitHandSurfFirst.get_rect(topleft = (posX, posY))
                    DISPLAYSURF.blit(splitHandSurfFirst, splitHandRectFirst)
                    posY += LINESPACING12
                    splitHandSurfSecond = PROMPTFONT.render(splitHandTextSecond, True, TEXTCOLOR)
                    splitHandRectSecond = splitHandSurfSecond.get_rect(topleft = (posX, posY))
                    DISPLAYSURF.blit(splitHandSurfSecond, splitHandRectSecond)
                    pygame.display.update()
                    pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
                    # Skip to the next player.
                    continue
                # To get this far, the player's bank can cover the new ante.
                # We need to ask the user if they want to split up the
                # player's pair into two hands.
                splitHandTextFirst  = "{0}, you have a pair showing.".format(playerName)
                splitHandTextSecond = "Would you like to split your hand?"
                splitHandSurfFirst  = PROMPTFONT.render(splitHandTextFirst, True, TEXTCOLOR)
                splitHandRectFirst  = splitHandSurfFirst.get_rect(topleft = (posX, posY))
                DISPLAYSURF.blit(splitHandSurfFirst, splitHandRectFirst)
                posY += LINESPACING12
                splitHandSurfSecond = PROMPTFONT.render(splitHandTextSecond, True, TEXTCOLOR)
                splitHandRectSecond = splitHandSurfSecond.get_rect(topleft = (posX, posY))
                DISPLAYSURF.blit(splitHandSurfSecond, splitHandRectSecond)
                pygame.display.update()
                answer = checkForYesNo(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
                if answer == True:
                    # Now, we need to split the pair into two hands and update
                    # the full screen. Note, the phase is still 'deal'. We also
                    # need to reset the text position to the upper left again.
                    tableObj.players[seat].split_pair()
                    refreshTable(tableObj.phase, rounds)
                    posX = LEFTMARGIN
                    posY = TOPMARGIN
                    clearStatusCorner()
                    pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
                    # Now, the players needs to make a new ante on the split
                    # hand. After that, two cards will be dealt, one to each
                    # hand. The loop below will break out once a valid ante
                    # has been entered.
                    while tableObj.players[seat].split_bet == 0:
                        tableObj.seat = seat
                        getBet('split')
                    refreshTable(tableObj.phase, rounds)
                    dealSingleCard(seat, rounds, 'split regular')
                    dealSingleCard(seat, rounds, 'split new')
                    # Note: dealSingleCard has a pressSpaceToContinue at the
                    # end of function.
    return # checkForPairs
                    
def dealSingleCard(seat, rounds, handType):
    """
    This function handles dealing a single card to a specific player's hand,
    including the Dealer. It uses the player and dealer methods add_card_to_hand
    and checks the outcome of adding the card. There are a few types of hands
    that will be encountered in the game. The handTypes are:
        'regular'       : player's regular hand after the deal phase is done
        'split regular' : player's regular hand after a pair was split
        'split new'     : player's new single card split hand
        'split'         : player's split hand after the deal phase is done
        'dealer'        : dealer's hand during the dealer's turn
    Each of these options has different requirements, but the process has a
    number of common steps. Mainly, it changes what is said to the user/player
    and which hand receives the dealt card.

    This function also updates the results dictionary that is part of the 
        tableObj (tableObj.results). The keys for this dictionary are:
        'left reg'     : player in left seat, regular hand
        'left split'   : player in left seat, split hand
        'middle reg'   : player in middle seat, regular hand
        'middle split' : player in middle seat, split hand
        'right reg'    : player in right seat, regular hand
        'right split'  : player in right seat, split hand
        'dealer reg'   : dealer's hand
    The statuses for these hands are:
        'blackjack'    : natural 21
        'playable'     : the hand is still playable
        'bust'         : the hand busted
        'none'         : this hand does not exist

    INPUTS: three arguments
        seat : string, the seat at the casino table, values are TABLESEATSALL
        rounds : integer, number of the current round of play
        handType : string (see above for values and meanings)
    OUTPUTS: None, all changes occur to the screen or parts of tableObj.
    """
    # Clearing the status corner.
    clearStatusCorner()
    # Setting up the position variables
    posX = LEFTMARGIN
    posY = TOPMARGIN
    # Draw a card from the CardShoe.
    newCard = tableObj.deck.remove_top()
    # For each hand possibility, we have three things we need to do. First,
    # we need to add the card to correct hand and see what effect that has
    # on player or dealer scores. That is the "result". Second, we need to
    # put up an appropriate message in the status corner. Third, we need to
    # add the result to the tableObj.results dictionary.
    if handType == 'regular':
        result = tableObj.players[seat].add_card_to_hand(newCard)
        promptText = "Here is another card for your regular hand."
        tableObj.results[seat + ' reg'] = result

    elif handType == 'split regular':
        result = tableObj.players[seat].add_card_to_hand(newCard)
        promptText = "Dealing a new card for your regular hand."
        # Blackjacks only count before splitting hands, not after.
        if result == 'blackjack':
            result = 'playable'
        tableObj.results[seat + ' reg'] = result

    elif handType == 'split new':
        result = tableObj.players[seat].add_card_to_split(newCard)
        promptText = "Dealing a new card for your split hand."
        tableObj.results[seat + ' split'] = result

    elif handType == 'split':
        result = tableObj.players[seat].add_card_to_split(newCard)
        promptText = "Here is another card for your split hand."
        tableObj.results[seat + ' split'] = result

    elif handType == 'dealer':
        result = tableObj.tableDealer.add_card_to_hand(newCard)
        promptText = "Dealer takes another card."
        tableObj.results['dealer reg'] = result
    
    # Now, we need to update the whole table layout and add to it the text
    # for the hand that will receive the newly dealt card.
    refreshTable(tableObj.phase, rounds)
    promptSurf = PROMPTFONT.render(promptText, True, TEXTCOLOR)
    promptRect = promptSurf.get_rect(topleft = (posX, posY))
    DISPLAYSURF.blit(promptSurf, promptRect)
    pygame.display.update()
    pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
    print("dealSingleCard: Player Hands: Regular {0}. Split {1}.".format(tableObj.players[seat].hand, tableObj.players[seat].split_hand))
    return # dealSingleCard
                
def clearStatusCorner():
    """
    These commands get used over and over in this game. Basically, this
    function writes over the corner of the screen with the background color.
    This clears that block, called the status block.
    INPUTS: None
    OUTPUTS: Only to the screen.
    """
    statusSurf = pygame.Surface((STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT))
    statusRect = statusSurf.get_rect(topleft = (LEFTMARGIN, TOPMARGIN))
    statusSurf.fill(BGCOLOR)
    DISPLAYSURF.blit(statusSurf, statusRect)
    pygame.display.update()
    return

def doubleDown(rounds):
    """
    This method offers the user an opportunity to raise the bets on the hands
    dealt to the players. Under Casino rules for Blackjack, players may
    raise their bets up to double the amount of the original bet, hence the
    term 'double down'. There are two exceptions, and both have to do with
    player or dealer blackjacks. Players who get dealt a blackjack have already
    won their hand by now. They get an increased payout (up to triple at the
    high rollers tables) for it. Insurance bets cannot be raised either. They
    payout when the dealer reveals the hold card.

    This phase of the game is called 'raise'.

    The function getBet deals with these bet increases. It is calls handleBet
    via the wrappers handleRegBet or handleSplitBet. This time, since the
    antes make the original regular bet and split bet non-zero, the Player bet
    update methods already know to look for a range of increases from $0 to
    the current bet amount. As with the antes, it will not accept an invalid
    raise.

    INPUTS: rounds, integer, number of the current round of play
    OUTPUTS: No outputs except to the game screen.
    """
    # As always, when a new function starts, we clear the status corner and
    # set the position coordinates.
    clearStatusCorner()
    posX = LEFTMARGIN
    posY = TOPMARGIN
    # Now, we need to setup a local variable that we may need later on.
    partOfRound = tableObj.phase

    # We need to give the user a few instructions before moving ahead.
    instructTextFirst  = "Now, you may raise the ante bets. The increase"
    instructTextSecond = "cannot exceed double the original bet. If you change"
    instructTextThird  = "your mind, simply enter a zero raise amount."
    instructSurfFirst  = PROMPTFONT.render(instructTextFirst, True, TEXTCOLOR)
    instructSurfSecond = PROMPTFONT.render(instructTextSecond, True, TEXTCOLOR)
    instructSurfThird  = PROMPTFONT.render(instructTextThird, True, TEXTCOLOR)
    instructRectFirst  = instructSurfFirst.get_rect(topleft = (posX, posY))
    posY += LINESPACING18
    instructRectSecond = instructSurfSecond.get_rect(topleft = (posX, posY))
    posY += LINESPACING18
    instructRectThird  = instructSurfThird.get_rect(topleft = (posX, posY))
    DISPLAYSURF.blit(instructSurfFirst, instructRectFirst)
    DISPLAYSURF.blit(instructSurfSecond, instructRectSecond)
    DISPLAYSURF.blit(instructSurfThird, instructRectThird)
    pygame.display.update()
    pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
    for seat in TABLESEATS:
        print("doubleDown: seat is {0} in {1}.".format(seat, TABLESEATS))
        if isPlayerStillThere(seat):
            # getBet will prompt the "player" for bet raises. handleBet
            # validates the bet amounts and warns the user of invalid bets.
            # We just have to ask if the user wants to raise the bet and
            # setup a while loop to verify that the bet changed amount.
            # The big issues for this function are determining if the
            # player already won the round with a blackjack and to check
            # for a split hand, along with a regular hand. The results dict
            # object supplies these answers. There is an attribute for
            # players, raise_bet and raise_split_bet, which are used to
            # verify that a raise success was received.
            # First, we need to reset the position and clear the status
            # corner for each pass.
            clearStatusCorner()
            tableObj.seat = seat
            playerName = tableObj.players[seat].name
            posX = LEFTMARGIN
            posY = TOPMARGIN

            # A hand that is 'playable' has neither won already nor busted.
            if tableObj.results[seat + ' reg'] == 'playable':
                print("doubleDown: Asking Player {0} to raise bet.".format(playerName))
                raiseText = "{0}, would like to raise your regular bet?".format(playerName)
                raiseSurf = PROMPTFONT.render(raiseText, True, TEXTCOLOR)
                raiseRect = raiseSurf.get_rect(topleft = (posX, posY))
                DISPLAYSURF.blit(raiseSurf, raiseRect)
                # diagnosticPrint(tableObj, 'v')
                pygame.display.update()
                answer = checkForYesNo(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
                print("doubleDown: Status: Phase is {0}. partOfRound is {1}".format(tableObj.phase, partOfRound))
                print("doubleDown: Status: Player.name is {0}.".format(tableObj.players[seat].name))
                print("doubleDown: Status: Player's current bet is {0}. Answer is {1}.".format(tableObj.players[seat].bet, answer))
                if answer == True:
                    while tableObj.players[seat].raise_bet == False:
                        getBet('reg')
                        clearStatusCorner()
                        refreshTable(partOfRound, rounds)
                print("doubleDown: Status: Completed Player {0}'s raise on regular hand.".format(playerName))
            print("doubleDown: Status: Completed stanza for Player {0}'s regular hand.".format(playerName))
            # Need to clear the status corner again and reset position.
            clearStatusCorner()
            posX = LEFTMARGIN
            posY = TOPMARGIN
            # answer = None  # Resetting answer between stanzas.
            refreshTable(partOfRound, rounds)
            # diagnosticPrint(tableObj, 'v')

            # A split hand that is playable has neither won nor busted. A None
            # value will be ignored as well.
            if tableObj.results[seat + ' split'] == 'playable':
                print("doubleDown: Asking Player {0} to raise split bet.".format(playerName))
                raiseText = "{0}, would like to raise your split bet?".format(playerName)
                raiseSurf = PROMPTFONT.render(raiseText, True, TEXTCOLOR)
                raiseRect = raiseSurf.get_rect(topleft = (posX, posY))
                DISPLAYSURF.blit(raiseSurf, raiseRect)
                pygame.display.update()
                answer = checkForYesNo(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
                print("doubleDown: Status: Phase is {0}. partOfRound is {1}".format(tableObj.phase, partOfRound))
                print("doubleDown: Status: Player.name is {0}.".format(tableObj.players[seat].name))
                print("doubleDown: Status: Player's split bet is {0}. Answer is {1}.".format(tableObj.players[seat].split_bet, answer))
                if answer == True:
                    while tableObj.players[seat].raise_split_bet == False:
                        getBet('split')
                        clearStatusCorner()
                        refreshTable(partOfRound, rounds)
                print("doubleDown: Status: Completed Player {0}'s raise on split hand.".format(playerName))
            # diagnosticPrint(tableObj, 'v')
            print("doubleDown: Status: Completed stanza for Player {0}'s split hand.".format(playerName))
    clearStatusCorner()
    refreshTable(partOfRound, rounds)
    # diagnosticPrint(tableObj, 'v')
    return # doubleDown

def hitOrStand(rounds):
    """
    This function interacts with the user to provide additional cards to the
    players. It uses the Player methods add_card_to_hand and add_card_to_split
    along with the function dealSingleCard to determine if a player busts.
    INPUTS: rounds, integer, the number of the current round of play
    OUTPUTS: tuple of integers
        remainingHands: number of hands remaining for the dealer's turn
        remainingPlayers: number of players eliminated during this phase
    """
    # Set our hand and player counters. playerLosses tabulates each players
    # losses during their turn.
    # Note: Players cannot win until the dealer's turn if they did not hit
    # blackjack already.
    remainingHands = 0
    remainingPlayers = 0
    playerLosses = 0
    for seat in TABLESEATS:
        tableObj.phase = partOfRound = seat
        # A player might have been withdrawn or busted the bank in previous
        # rounds, or the player may have already hit blackjack. So, we have
        # to check both before proceeding. This part checks the regular hand.
        if isPlayerStillThere(seat):
            # The player's name is only available if the seat is occupied.
            playerName = tableObj.players[seat].name
            # Increment the player counter and reset playerLosses.
            remainingPlayers += 1
            playerLosses = 0
            # This loop continues until the player says stop or the hand busts.
            while tableObj.results[seat + ' reg'] == 'playable':
                # Reset the position to the upper left of the status corner
                # and clear the status corner. Increment the hands counter.
                remainingHands += 1
                posX = TOPMARGIN
                posY = LEFTMARGIN
                clearStatusCorner()
                hitText = "{0}, would like another card for your regular hand?".format(playerName)
                hitSurf = PROMPTFONT.render(hitText, True, TEXTCOLOR)
                hitRect = hitSurf.get_rect(topleft = (posX, posY))
                DISPLAYSURF.blit(hitSurf, hitRect)
                pygame.display.update()
                # Returns True for Y/H or False for N/S.
                answer = checkForHitStand()
                if answer == True:
                    dealSingleCard(seat, rounds, 'regular')
                else:
                    # Breaks the loop if the user does not want another card.
                    break
                refreshTable(partOfRound, rounds)
                if tableObj.results[seat + ' reg'] == 'bust':
                    # Decrement hand counter since this one is defunct.
                    remainingHands -= 1
                    # Increment the player's losses
                    playerLosses += tableObj.players[seat].bet
                    # This method updates the dealer's bank with the player's
                    # lost bet.
                    tableObj.tableDealer.dealer_won(tableObj.players[seat].bet)
                    bustTextFirst  = "{0}, your regular hand busted.".format(playerName)
                    bustTextSecond = "Your losses are now ${0}.".format(playerLosses)
                    bustSurfFirst  = DATAFONT.render(bustTextFirst, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                    bustSurfSecond = DATAFONT.render(bustTextSecond, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                    bustRectFirst  = bustSurfFirst.get_rect(topleft = (posX, posY))
                    posY += LINESPACING18
                    bustRectSecond = bustSurfSecond.get_rect(topleft = (posX, posY))
                    DISPLAYSURF.blit(bustSurfFirst, bustRectFirst)
                    DISPLAYSURF.blit(bustSurfSecond, bustRectSecond)
                    pygame.display.update()
                    posY += LINESPACING18
                    lossResult = tableObj.players[seat].reg_loss()
                    print("hitOrStand: Status: lossResult = {0}.".format(lossResult))
                    print("hitOrStand: Status: Split Flag is {0}.".format(tableObj.players[seat].split_flag))
                    print("hitOrStand: Status: Insurance bet is {0}.".format(tableObj.players[seat].insurance))
                    pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
                    # A False result means the player broke their bank. It is
                    # still possible for them to survive if they have a split
                    # hand or an insurance bet, however.
                    # Note: Bust means the while loop will terminate.
                    # Note: Entering the stanza below means that the player
                    # cannot have another hand.
                    if (lossResult == False and\
                        tableObj.players[seat].split_flag == False and\
                        tableObj.players[seat].insurance == 0):
                        eliminateTextFirst  = "You do not have additional bets that could"
                        eliminateTextSecond = "cover your losses. You have been eliminated."
                        eliminateSurfFirst  = PROMPTFONT.render(eliminateTextFirst, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                        eliminateSurfSecond = PROMPTFONT.render(eliminateTextSecond, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                        eliminateRectFirst  = eliminateSurfFirst.get_rect(topleft = (posX, posY))
                        posY += LINESPACING18
                        eliminateRectSecond = eliminateSurfSecond.get_rect(topleft = (posX, posY))
                        DISPLAYSURF.blit(eliminateSurfFirst, eliminateRectFirst)
                        DISPLAYSURF.blit(eliminateSurfSecond, eliminateRectSecond)
                        pygame.display.update()
                        pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
                        # This function removes the player from the tableObj.
                        # We also need to decrement the player counter.
                        eliminatePlayer(seat)
                        remainingPlayers -= 1
                        # We have to break out because the player is gone now.
                        break
            # End of while loop for cards for the regular hand.
            
            # Now, we have to make sure that the player is still here. Then,
            # we need to do the same things for a split hand, if it exists.
            if not isPlayerStillThere(seat):
                # The player was eliminated, meaning there is no playable
                # split hand.
                continue

            while tableObj.results[seat + ' split'] == 'playable':
                # Reset the position to the upper left of the status corner
                # and clear the status corner. Increment the hands counter.
                remainingHands += 1
                posX = TOPMARGIN
                posY = LEFTMARGIN
                clearStatusCorner()
                hitText = "{0}, would like another card for your split hand?".format(playerName)
                hitSurf = PROMPTFONT.render(hitText, True, TEXTCOLOR)
                hitRect = hitSurf.get_rect(topleft = (posX, posY))
                DISPLAYSURF.blit(hitSurf, hitRect)
                pygame.display.update()
                # Returns True for Y/H or False for N/S.
                answer = checkForHitStand()
                if answer == True:
                    dealSingleCard(seat, rounds, 'split')
                else:
                    # Breaks the loop if the user does not want another card.
                    break
                refreshTable(partOfRound, rounds)
                if tableObj.results[seat + ' split'] == 'bust':
                    # Decrement hand counter since this one is defunct.
                    remainingHands -= 1
                    # Increment the player's losses
                    playerLosses += tableObj.players[seat].split_bet
                    # This method updates the dealer's bank with the player's
                    # lost split bet.
                    tableObj.tableDealer.dealer_won(tableObj.players[seat].split_bet)
                    bustTextFirst  = "{0}, your split hand busted.".format(playerName)
                    bustTextSecond = "Your losses are now ${0}.".format(playerLosses)
                    bustSurfFirst  = DATAFONT.render(bustTextFirst, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                    bustSurfSecond = DATAFONT.render(bustTextSecond, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                    bustRectFirst  = bustSurfFirst.get_rect(topleft = (posX, posY))
                    posY += LINESPACING18
                    bustRectSecond = bustSurfSecond.get_rect(topleft = (posX, posY))
                    DISPLAYSURF.blit(bustSurfFirst, bustRectFirst)
                    DISPLAYSURF.blit(bustSurfSecond, bustRectSecond)
                    pygame.display.update()
                    posY += LINESPACING18
                    lossResult = tableObj.players[seat].split_loss()
                    print("hitOrStand: Status: lossResult = {0}.".format(lossResult))
                    print("hitOrStand: Status: Insurance bet is {0}.".format(tableObj.players[seat].insurance))
                    pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
                    # A False result means the player broke their bank. It is
                    # still possible for them to survive with an insurance
                    # bet, however.
                    # Note: Bust means the while loop will terminate.
                    if (lossResult == False and tableObj.players[seat].insurance == 0):
                        eliminateTextFirst  = "You do not have additional bets that could"
                        eliminateTextSecond = "cover your losses. You have been eliminated."
                        eliminateSurfFirst  = PROMPTFONT.render(eliminateTextFirst, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                        eliminateSurfSecond = PROMPTFONT.render(eliminateTextSecond, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                        eliminateRectFirst  = eliminateSurfFirst.get_rect(topleft = (posX, posY))
                        posY += LINESPACING18
                        eliminateRectSecond = eliminateSurfSecond.get_rect(topleft = (posX, posY))
                        DISPLAYSURF.blit(eliminateSurfFirst, eliminateRectFirst)
                        DISPLAYSURF.blit(eliminateSurfSecond, eliminateRectSecond)
                        pygame.display.update()
                        pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
                        # This function removes the player from the tableObj.
                        # We also need to decrement the player counter.
                        removeCheck = eliminatePlayer(seat)
                        if removeCheck == True:
                            remainingPlayers -= 1
                        else:
                            print("hitOrStand: Unable to remove player in seat {0}.".format(seat))
                            terminate()
                        # We have to break out because the player is gone now.
                        break 
                # End of while loop for cards for the split hand.
            # End of if statement checking for filled seats.
        # End of for loop checking seats.
    return (remainingHands, remainingPlayers) # hitOrStand
            
def checkForHitStand():
    """
    This function works similar to checkForYesNo, except that it accepts four
    different inputs, besides QUIT and ESCAPE. These inputs are:
        'Y' : yes the player wants another card
        'H' : the player wants a 'hit' (another card)
        'N' : no, the player does not want another card
        'S' : the player wants to 'stand' (no more cards)
    INPUTS: None
    OUTPUTS: True, if Y or H were pressed, False is N or S were pressed
    """
    displayRect = DISPLAYSURF.get_rect()
    while True: # event loop
        # Note: Unlike checkForYesNo, this function works only in the bottom
        # right corner of the status block.
        posX = STATUSBLOCKWIDTH
        posY = STATUSBLOCKHEIGHT - LINESPACING18
        instructTextFirst  = "Press H or Y to get another card (hit or yes)."
        instructTextSecond = "Press S or N to stand (stand or no)."
        instructSurfFirst  = DATAFONT.render(instructTextFirst, True, TEXTCOLOR)
        instructSurfSecond = DATAFONT.render(instructTextSecond, True, TEXTCOLOR)
        instructRectFirst  = instructSurfFirst.get_rect(bottomright = (posX, posY))
        posY = STATUSBLOCKHEIGHT
        instructRectSecond = instructSurfSecond.get_rect(bottomright = (posX, posY))
        DISPLAYSURF.blit(instructSurfFirst, instructRectFirst)
        DISPLAYSURF.blit(instructSurfSecond, instructRectSecond)
        pygame.display.update()

        for event in pygame.event.get(QUIT): # get all QUIT events
            terminate()                      # terminate if any QUIT events are present
        for event in pygame.event.get(KEYUP):# get all KEYUP events
            if event.key == K_ESCAPE:        # ESCAPE is also a 'quit' event
                terminate()

        for event in pygame.event.get():     # Removed KEYDOWN only type
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:    # Another QUIT event
                    terminate()
                elif event.key in (K_y, K_h):
                    return True
                elif event.key in (K_n, K_s):
                    return False
            # This stanza is an effort to make the game screen become active
            # after a change of focus.
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                active = displayRect.collidepoint(event.pos)
        pygame.display.update()
        FPSCLOCK.tick()
    return # checkForHitStand
    
def eliminatePlayer(seat):
    """
    This function eliminates a player that has broken their bank during the
    game. They will also be eliminated from the saved game, but not by this
    function.
    INPUTS: seat, string, indicating the seat the player was in before
        breaking their bank
    """
    playerName = tableObj.players[seat].name
    print("eliminatePlayer: Status: seat for elimination is {0}.".format(seat))
    print("eliminatePlayer: Status: Player to be eliminated is {0}.".format(playerName))
    del tableObj.players[seat]
    return

def dealersTurn(remainingHands, remainingPlayers, rounds):
    """
    This function plays out the dealers turn. First, it checks to see if any
    hands remain that the dealer has to play against. Here are a list of the
    conditions for each hand:
        Player              Dealer              Outcome
        ----------------------------------------------------
        Blackjack           Playable hand       Player wins
        Any non-blackjack   Blackjack           Dealer wins
        Non-blackjack 21    Non-blackjack 21    Tie, no winner
        High score          High score          Tie, no winner
        Low score           High score          Dealer wins
        Busts               Playable hand       Dealer wins
        Playable hand       Busts               Player wins
    
    The dealer has to abide by the following casino rules:
        * dealer must stand on a hard 17 or more
        * dealer stands on any 21 (blackjack or otherwise)
        * dealer must take a card on a soft 16 or less
        * dealer must stand on a hard 16 or less if the soft score on the
            hand is 17 or greater AND it beats at least one player's hand
            (of the remaining playable hands)
        * dealer must take a card on a hard 16 or less if the soft score on
            the hand does not beat any of the players' remaining hands
    
    INPUTS: three arguments
        remainingHands, integer, the number of playable player hands
        remainingPlayers, integer, the number of players still seated
        rounds, integer, number of the current round
    OUTPUTS: None. All outputs are to the screen. Any data changes are
        made to the global tableObj object. This function uses the results
        attribute to track remaining winners, losers, and ties.
    """
    # First, we need to set a few required variables. The first checks to see
    # if the dealer has blackjack. If so, the dealer won all remaining hands.
    # The second checks to see if any hands remain for the dealer to play
    # against. The third is a check to see if any players remain. If not, we
    # have a case of the user losing the game.
    # Note: All of these variables are booleans using logical expression for
    # variable assignment.
    dealerBlackjack = (tableObj.results['dealer reg'] == 'blackjack')
    insuranceBets = False
    noHandsRemain = (remainingHands == 0)
    userLosesGame = (remainingPlayers == 0)
    dealerLosses = 0
    dealerWins = 0
    print("dealersTurn: Status: remainingHands is {0}. remainingPlayers is {1}.".format(remainingHands, remainingPlayers))
    print("dealersTurn: Status: dealerBlackjack is {0}. noHandsRemain is {1}.".format(dealerBlackjack, noHandsRemain))
    print("dealersTurn: Status: userLosesGame is {0}. dealerLosses is {1}. dealerWins is {2}.".format(userLosesGame, dealerLosses, dealerWins))

    # Next, we need to determine if any insurance were made.
    for seat in TABLESEATS:
        if isPlayerStillThere(seat):
            insBetAmt = tableObj.players[seat].insurance
            if insBetAmt != 0:
                insuranceBets = True
                break
    # All we need is one non-zero bet to make it a reality.


    # Now, clear the status corner and set the positionals.
    clearStatusCorner()
    posX = LEFTMARGIN
    posY = TOPMARGIN

    # This function will tell the user they lost and terminate the game. We
    # need to find out if it is necessary to do so. Other functions verify
    # that additional bets exist that might save a player. If there are no
    # players left at this point, all of them were eliminated by busting
    # there banks without insurance reprieves.
    if userLosesGame:
        refreshTable('dealer', rounds)
        userLostGame()

    # Dealer reveals their hold card.
    refreshTable('dealer', rounds)
    # First, we look as the case that the dealer has blackjack and there are
    # insurance bets. Note, there is a separate function that handles dealer
    # blackjack and the actual insurance bets. This is just a notification
    # block.
    if dealerBlackjack and insuranceBets:
        blackjackTextFirst  = "The dealer has blackjack."
        blackjackTextSecond = "All insurance bets win."
    # Next, we look at the case that the dealer did not have blackjack and
    # there are insurance bets.
    elif not dealerBlackjack and insuranceBets:
        blackjackTextFirst  = "The dealer does not have blackjack."
        blackjackTextSecond = "All insurance bets lose."
    # Next, we look at the case in which the dealer has blackjack but none
    # of players made insurance bets. Again, this is a notification block.
    # The function, dealerHasBlackjack(), deals with insurance and player
    # losses.
    elif dealerBlackjack and not insuranceBets:
        blackjackTextFirst  = "The dealer has blackjack, but"
        blackjackTextSecond = "there are no insurance bets."
    # Finally, we look at the case that the dealer does not have blackjack
    # and there are no insurance bets.
    else:
        blackjackTextFirst  = "The dealer does not have blackjack."
        blackjackTextSecond = "There are no insurance bets either."
    
    # Common print block following reveal of the hold card.
    blackjackSurfFirst  = SCOREFONT.render(blackjackTextFirst, True, TEXTCOLOR)
    blackjackSurfSecond = SCOREFONT.render(blackjackTextSecond, True, TEXTCOLOR)
    blackjackRectFirst  = blackjackSurfFirst.get_rect(topleft = (posX, posY))
    posY += LINESPACING12
    blackjackRectSecond = blackjackSurfSecond.get_rect(topleft = (posX, posY))
    DISPLAYSURF.blit(blackjackSurfFirst, blackjackRectFirst)
    DISPLAYSURF.blit(blackjackSurfSecond, blackjackRectSecond)
    pygame.display.update()
    pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)

    # Next, we need to resolve the insurance bets, as that might save a
    # player facing elimination from a hand that busted.  resolveInsBets
    # returns the number of players remaining in the game.
    remainingPlayers = resolveInsBets(dealerBlackjack)
    if remainingPlayers == 0:
        refreshTable('dealer', rounds)
        userLostGame()

    # Next, we need to check to see if the dealer needs to play their hand.
    # No remaining playable hands means that there is nothing to do. All of
    # the player hands have already been resolved.
    if noHandsRemain:
        # Reset the status corner.
        clearStatusCorner()
        posX = LEFTMARGIN
        posY = TOPMARGIN
        noHandsTextFirst  = "No playable hands remain. The dealer is not required"
        noHandsTextSecond = "to play out their hand. The round is over."
        noHandsSurfFirst  = SCOREFONT.render(noHandsTextFirst, True, TEXTCOLOR)
        noHandsSurfSecond = SCOREFONT.render(noHandsTextSecond, True, TEXTCOLOR)
        noHandsRectFirst  = noHandsSurfFirst.get_rect(topleft = (posX, posY))
        posY += LINESPACING12
        noHandsRectSecond = noHandsSurfSecond.get_rect(topleft = (posX, posY))
        posY += LINESPACING12
        DISPLAYSURF.blit(noHandsSurfFirst, noHandsRectFirst)
        DISPLAYSURF.blit(noHandsSurfSecond, noHandsRectSecond)
        pygame.display.update()
        pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
        return

    # Now, we need to check the case that the dealer has a blackjack. In this
    # case, all other playable hands lose automatically.
    if dealerBlackjack:
        remainingPlayers = dealerHasBlackjack()
        if remainingPlayers == 0:
            refreshTable('dealer', rounds)
            userLostGame()
        return

    # Since at least one playable hand remains, the dealer has to play their
    # hand to determine the outcome of the game. We need the highest score
    # and the lowest score among the playable hands. Remember, soft scores
    # are always greater than or equal to the hard score because the soft
    # score uses Ace = 11 whenever possible. The dealer has to take a card
    # until the dealer's soft score beats at least one player's score or the
    # dealer's hand score is 17 or greater. The minScore gives that to us.
    # The maxScore tells us if the dealer beat all of the remining hands.
    # We need the list of hands for a second purpose, determining win, tie,
    # or lose on each playable hand. Since we are collecting scores for the
    # hands, we can also collect keys for the hands as well.
    playableScores = []
    playableHands = []
    for possibleHand in HANDLIST:
        # The str.split() method turns a string into a list, or in this case,
        # one or two list entries.
        seat, handType = possibleHand.split(' ')
        # This keeps kicking out a 'dealer is not there message'. So, I am 
        # going to swap the order of the booleans.
        if seat != 'dealer' and isPlayerStillThere(seat):
            print("dealersTurn: Status: possibleHand is {0}. seat is {1}. handType is {2}. result is {3}.".format(possibleHand, seat, handType, tableObj.results[possibleHand]))
            # We are skipping the dealer because we are collecting data on 
            # players' hands.
            handStatus = tableObj.results[possibleHand]
            if handStatus == 'playable' and handType != 'split':
                # This is a playable regular hand. First, we check the scores
                # for the hand.
                softScore = tableObj.players[seat].soft_hand_score
                print("dealersTurn: Status: softScore is {0}.".format(softScore))
                # Using a list allows us to sort it, pulling the highest
                # and lowest scores out. We need the scores in order to
                # ensure that the dealer plays their hand properly.
                playableScores.append(softScore)
                playableHands.append(possibleHand)
            elif handStatus == 'playable' and handType == 'split':
                # This is a split hand. Again, we check the scores and 
                # append them to our list playableScores.
                softScore = tableObj.players[seat].soft_split_score
                print("dealersTurn: Status: softScore is {0}.".format(softScore))
                playableScores.append(softScore)
                playableHands.append(possibleHand)
            # We don't need to look at any other conditions.
    # We need to sort this list of scores in case the minScore is too small
    # to use.
    playableScores.sort
    print("dealersTurn: Status: playableScores is {0}.".format(playableScores))
    print("dealersTurn: Status: playableHands is {0}.".format(playableHands))
    maxScore = max(playableScores)
    minScore = min(playableScores)
    while minScore < 17 and len(playableScores) > 1:
        # The score must be greater than 17. It is possible for players to
        # stand at 12 or 13 and wait to see if the dealer busts. So, we will
        # remove the bottom score and get a new minScore until we reach the
        # maxScore.
        playableScores.pop(0)
        print("dealersTurn: Status: playableScore is {0}.".format(playableScores))
        print("dealersTurn: Status: minScore is {0}, maxScore is {1}.".format(minScore, maxScore))
        minScore = min(playableScores)
        if minScore == maxScore:
            break

    # Now, we set up a loop to play the dealer's hand. This loop uses the
    # result value for the dealer's hand to determine when to stop the loop.
    # There are three values that will stop it:
    #   'stand' : The dealer's score met the criteria that forces the dealer
    #               stand.
    #   'bust'  : The dealer's hand busted.
    while tableObj.results['dealer reg'] not in ('stand', 'bust'):
        refreshTable('dealer', rounds)
        dealerHardScore = tableObj.tableDealer.hard_hand_score
        dealerSoftScore = tableObj.tableDealer.soft_hand_score
        # Set positionals.
        posX = LEFTMARGIN
        posY = TOPMARGIN
        # First, we have to look at the scores that dealer has for its hand.
        # This will determine what actions to take next. We are not starting
        # with busts because Dealer.add_card_to_hand() will tell us if the
        # next card added to the dealer's hand caused a bust.
        if 21 >= dealerHardScore > 16:
            # Dealer must stand on a hard 17 or higher.
            tableObj.results['dealer reg'] = 'stand'
            dealerStandText = "Dealer must stand on a {0}.".format(dealerHardScore)
            dealerStandSurf = SCOREFONT.render(dealerStandText, True, TEXTCOLOR)
            dealerStandRect = dealerStandSurf.get_rect(topleft = (posX, posY))
            DISPLAYSURF.blit(dealerStandSurf, dealerStandRect)
            pygame.display.update()
            pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
            # This will end this while loop.
            continue

        # Next, we need to see if the dealer's soft hand score beats at least
        # one player and that the min score is above 16.
        if dealerHardScore <= 16 and\
           dealerSoftScore > minScore and\
           minScore >= 16:
            tableObj.results['dealer reg'] = 'stand'
            dealerStandTextFirst  = "Dealer has a soft {0}, which is greater".format(dealerSoftScore)
            dealerStandTextSecond = "than 16 and the minimum player score of {0}.".format(minScore)
            dealerStandTextThird  = "Dealer must stand."
            dealerStandSurfFirst  = SCOREFONT.render(dealerStandTextFirst, True, TEXTCOLOR)
            dealerStandSurfSecond = SCOREFONT.render(dealerStandTextSecond, True, TEXTCOLOR)
            dealerStandSurfThird  = SCOREFONT.render(dealerStandTextThird, True, TEXTCOLOR)
            dealerStandRectFirst  = dealerStandSurfFirst.get_rect(topleft = (posX, posY))
            posY += LINESPACING12
            dealerStandRectSecond = dealerStandSurfSecond.get_rect(topleft = (posX, posY))
            posY += LINESPACING12
            dealerStandRectThird  = dealerStandSurfThird.get_rect(topleft = (posX, posY))
            DISPLAYSURF.blit(dealerStandSurfFirst, dealerStandRectFirst)
            DISPLAYSURF.blit(dealerStandSurfSecond, dealerStandRectSecond)
            DISPLAYSURF.blit(dealerStandSurfThird, dealerStandRectThird)
            pygame.display.update()
            pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
            continue

        # Since we got to this point, the dealer must take a card.
        card = tableObj.deck.remove_top()
        result = tableObj.tableDealer.add_card_to_hand(card)
        refreshTable('dealer', rounds)
        if result == 'bust':
            hardScore = tableObj.tableDealer.hard_hand_score
            dealerBustTextFirst  = "Dealer busts with a hard {0}.".format(hardScore)
            dealerBustTextSecond = "All remaining players win their bets."
            dealerBustSurfFirst  = SCOREFONT.render(dealerBustTextFirst, True, TEXTCOLOR)
            dealerBustSurfSecond = SCOREFONT.render(dealerBustTextSecond, True, TEXTCOLOR)
            dealerBustRectFirst  = dealerBustSurfFirst.get_rect(topleft = (posX, posY))
            posY += LINESPACING12
            dealerBustRectSecond = dealerBustSurfSecond.get_rect(topleft = (posX, posY))
            posY += LINESPACING12
            DISPLAYSURF.blit(dealerBustSurfFirst, dealerBustRectFirst)
            DISPLAYSURF.blit(dealerBustSurfSecond, dealerBustRectSecond)
            pygame.display.update()
            pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
            dealerBusts(rounds)
            return
        # The result can only be 'playable' at this point. A playable hand
        # requires that the loop continue until the dealer busts or has to
        # stand.
    # End of while loop of dealer taking cards for its hand.

    # To get this far, the dealer had to stand with a playable hand. Now, we
    # to determine who wins and loses individually based on the scores for the
    # dealer's hand. dealerHardScore and dealerSoftScore should be correct,
    # since the dealer would not have taken another card. We also collected
    # the playable hands, so we can find them again.
    for hand in playableHands:
        seat, handType = hand.split(' ')
        print("dealersTurn: Status: Determining win/lose/tie. seat is {0}. handType is {1}. result is {2}".format(seat, handType, tableObj.results[hand]))
        if handType == 'split':
            # This is a split hand. To determine a winner, we only need the
            # highest score the dealer or the player could achieve, which is
            # the soft score. Remember, blackjack is a hand formed by the
            # first two cards dealt to a player or dealer that contain an
            # ace and a ten value card. This hand has a soft score of 21 and
            # a hard score of 11.
            playerSoftScore = tableObj.players[seat].soft_split_score
        else: # This is the regular hand.
            playerSoftScore = tableObj.players[seat].soft_hand_score
        # Now, none of steps that follow require anything specific about
        # hand in the tableObj. So, we can use the same code for regular
        # hands and split hands. The hand key is unchanged.
        if dealerSoftScore > playerSoftScore:
            # The player lost their bet. For now, we are going to change
            # the results from playable to 'loss'.
            tableObj.results[hand] = 'loss'
        elif dealerSoftScore == playerSoftScore:
            # This is a tie. Ties are treated as a draw.
            tableObj.results[hand] = 'tie'
        else: # dealerSoftScore < playerSoftScore
            # The player won against the dealer.
            tableObj.results[hand] = 'win'
        print("dealersTurn: Status: win/lose/tie determined. seat is {0}. handType is {1}. result is {2}".format(seat, handType, tableObj.results[hand]))

    # All of the results have been tabulated, but we have only distributed
    # the wins and losses for blackjack and busted hands. Now, we need to
    # go through and pull out the winner and losers. We will use the collect
    # the dealer's wins and losses, then use the Dealer.wins and Dealer.losses
    # methods to apply them, since they will give us feedback if it breaks
    # the dealer's bank. Likewise, as we roll through the hands, we will
    # give players their winning and deduct losses using the Player wins,
    # tie, and loss for each hand. These methods also give feedback, so that
    # we will know if a player has to be eliminated.
    # Note: playableHands is the list of hands that players had after the
    # players' turns were over.
    # Reset the ordinals. All of these results should be printable in the
    # status window with the right spacing.
    clearStatusCorner()
    posX = LEFTMARGIN
    posY = TOPMARGIN
    for hand in playableHands:
        seat, handType = hand.split(' ')
        print("dealersTurn: Status: Distributing wins and losses. seat is {0}. handType is {1}. result is {2}".format(seat, handType, tableObj.results[hand]))
        if tableObj.results[hand] == 'win':
            playerName = tableObj.players[seat].name
            # Players cannot be eliminated by a win. If they were already
            # insolvent and this win is not enough to save their bank, the
            # function findDefunctPlayer will identify and remove them.
            if handType == 'split':
                betAmt = tableObj.players[seat].split_bet
                playerStatus = tableObj.players[seat].split_win()
                playerHandText = "{0} won the bet of ${1} on their split hand.".format(playerName, betAmt)
            else: # It is a regular hand.
                betAmt = tableObj.players[seat].bet
                playerStatus = tableObj.players[seat].win()
                playerHandText = "{0} won the bet of ${1} on their regular hand.".format(playerName, betAmt)
            dealerLosses += betAmt
            playerHandSurf = SCOREFONT.render(playerHandText, True, TEXTCOLOR)
            playerHandRect = playerHandSurf.get_rect(topleft = (posX, posY))
            posY += LINESPACING12
            DISPLAYSURF.blit(playerHandSurf, playerHandRect)
            pygame.display.update()
            pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)

        elif tableObj.results[hand] == 'tie':
            playerName = tableObj.players[seat].name
            # Players cannot be eliminated by a tie. If they were already
            # insolvent, findDefunctPlayer will identify and remove them.
            if handType == 'split':
                betAmt = tableObj.players[seat].split_bet
                playerStatus = tableObj.players[seat].split_tie()
                playerHandText = "{0} tied on their split hand.".format(playerName)
            else: # It is a regular hand.
                betAmt = tableObj.players[seat].bet
                playerStatus = tableObj.players[seat].tie()
                playerHandText = "{0} tied on their regular hand.".format(playerName)
            # With a tie, neither side loses any money.
            playerHandSurf = SCOREFONT.render(playerHandText, True, TEXTCOLOR)
            playerHandRect = playerHandSurf.get_rect(topleft = (posX, posY))
            posY += LINESPACING12
            DISPLAYSURF.blit(playerHandSurf, playerHandRect)
            pygame.display.update()
            pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
        
        elif tableObj.results[hand] == 'loss':
            playerName = tableObj.players[seat].name
            # Players losing bets can be eliminated from the game at this
            # point. For that reason, all of these outcomes had to be
            # handled separately.
            if handType == 'split':
                betAmt = tableObj.players[seat].split_bet
                playerStatus = tableObj.players[seat].split_loss()
                dealerWins += betAmt
                playerHandText = "{0} lost the bet of {1} on their split hand.".format(playerName, betAmt)
                playerHandSurf = SCOREFONT.render(playerHandText, True, TEXTCOLOR)
                playerHandRect = playerHandSurf.get_rect(topleft = (posX, posY))
                posY += LINESPACING12
            else: # It is a regular hand.
                betAmt = tableObj.players[seat].bet
                playerStatus = tableObj.players[seat].reg_loss()
                dealerWins += betAmt
                playerHandText = "{0} lost the bet of {1} on their regular hand.".format(playerName, betAmt)
                playerHandSurf = SCOREFONT.render(playerHandText, True, TEXTCOLOR)
                playerHandRect = playerHandSurf.get_rect(topleft = (posX, posY))
                posY += LINESPACING12
            # Now, we have to determine if the player should be eliminated.
            if playerStatus:
                # The player is still solvent.
                playerStatusText = "This player is still solvent."
                playerStatusSurf = SCOREFONT.render(playerStatusText, True, TEXTCOLOR)
                playerStatusRect = playerStatusSurf.get_rect(topleft = (posX, posY))
                posY += LINESPACING12
            else: # The player is insolvent.
                playerStatusText = "This player is insolvent and was eliminated."
                playerStatusSurf = PROMPTFONT.render(playerStatusText, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                playerStatusRect = playerStatusSurf.get_rect(topleft = (posX, posY))
                posY += LINESPACING18
                eliminatePlayer(seat)
                # The line spacing needs to be greater because PROMPTFONT
                # is bigger.
            DISPLAYSURF.blit(playerHandSurf, playerHandRect)
            DISPLAYSURF.blit(playerStatusSurf, playerStatusRect)
            pygame.display.update()
            pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
    # All wins and losses for the players have been applied to their banks.
    # Now, we need to apply the dealer's aggregate wins and losses to its
    # bank. We start with the wins, since they cannot affect the dealer's
    # status, but may prevent a bust on the other bets. Then, we apply the
    # losses and see if the dealer breaks their bank over it. The methods
    # we use are Dealer.dealer_won(amt) and Dealer.dealer_lost(amt).
    tableObj.tableDealer.dealer_won(dealerWins)
    dealerStatus = tableObj.tableDealer.dealer_lost(dealerLosses)
    if dealerStatus:
        refreshTable('dealer', rounds)
        posX = LEFTMARGIN
        posY = TOPMARGIN
        dealerStatusText = "Dealer remains solvent."
        dealerStatusSurf = PROMPTFONT.render(dealerStatusText, True, TEXTCOLOR)
        dealerStatusRect = dealerStatusSurf.get_rect(topleft = (posX, posY))
        DISPLAYSURF.blit(dealerStatusSurf, dealerStatusRect)
        pygame.display.update()
        pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
        return
    else: # Dealer busted their bank.
        DISPLAYSURF.fill(BLACK)
        posX = WINCENTERX
        posY = WINCENTERY
        dealerStatusText = "Dealer is now insolvent and has been eliminated."
        dealerStatusSurf = PROMPTFONT.render(dealerStatusText. True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
        dealerStatusRect = dealerStatusSurf.get_rect(topleft = (posX, posY))
        DISPLAYSURF.blit(dealerStatusSurf, dealerStatusRect)
        pygame.display.update()
        pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
        playersWinGame()
    return # dealersTurn

def resolveInsBets(dealerBlackjack):
    """
    This function resolves all insurance bets. It will remove any player
    that becomes insolvent due to losing the insurance bet, but only if the
    player has no other playable hand left.
    INPUTS: dealerBlackjack, boolean, True for dealer having blackjack, False
        otherwise
    OUTPUTS: remainingPlayers, integer from 0 to 3
    """
    # Initialize player counter, so this function can return the number of
    # remainingPlayers.
    remainginPlayers = 0
    # Per usual, we need to set positionals and clear the status corner.
    clearStatusCorner()
    posX = LEFTMARGIN
    posY = TOPMARGIN

    # Go through all seats and see who is left and has an insurance bet. It 
    # will be non-zero if the player has one.
    for seat in TABLESEATS:
        if isPlayerStillThere(seat):
            # The seat is occupied. Reset the status corner each iteration.
            print("resolveInsBet: Status: Checking seat {0} and printing {1}.".format(seat, tableObj.players[seat]))
            remainginPlayers += 1
            clearStatusCorner()
            posY = TOPMARGIN
            if tableObj.players[seat].insurance != 0:
                # The player has an insurance bet. We need to populate a few
                # easier to read variables.
                playerName = tableObj.players[seat].name
                playerBank = tableObj.players[seat].bank
                betAmt = tableObj.players[seat].insurance
                # Player.ins() method handles the bet based on the value of
                # the boolean it is given. result will be True if the player's
                # bank is still solvent, False otherwise.
                result = tableObj.players[seat].ins(dealerBlackjack)

                # Now, we have a few different outcomes:
                #   1) dealer had blackjack (player won)
                #   2) dealer did not have blackjack (player lost) but they
                #       are solvent still
                #   3) dealer did not have blackjack (player lost) and their
                #       is insolvent.
                # This function takes place after the hold card is revealed
                # but before the dealer finishes playing out its hand.

                if dealerBlackjack:
                    resultTextFirst  = "{0} won ${1}.".format(playerName, betAmt)
                    resultTextSecond = "{0} remains solvent.".format(playerName)
                    resultTextThird  = "This player will not eliminated, yet."
                elif dealerBlackjack == False and result == True:
                    # The player lost this bet, but has a solvent bank.
                    resultTextFirst  = "{0} lost ${1}, but still has ${2}".format(playerName, betAmt, playerBank)
                    resultTextSecond = "in the bank. This player is still solvent."
                    resultTextThird  = "This player will not eliminated, yet."
                else:
                    resultTextFirst  = "{0} lost ${1} on this bet and is insolvent.".format(playerName, betAmt)
                    # We need to check to see if the player still has a
                    # playable hand. If so, they will not be eliminated.
                    if tableObj.results[seat + ' reg'] == 'playable' or\
                       tableobj.results[seat + ' split'] == 'playable':
                        resultTextSecond = "{0} has at least one playable hand.".format(playerName)
                        resultTextThird  = "This player will not eliminated, yet."
                    else: # The player has no other means of survival.
                        resultTextSecond = "{0} has no playable hands left.".format(playerName)
                        resultTextThird  = "This player has been eliminated."
                        eliminatePlayer(seat)
                        remainginPlayers -= 1
                        # This block uses a different set of colors. So,
                        # these messages need their own print block. The rest
                        # use the common block further below.
                        resultSurfFirst  = PROMPTFONT.render(resultTextFirst, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                        resultSurfSecond = PROMPTFONT.render(resultTextSecond, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                        resultSurfThird  = PROMPTFONT.render(resultTextThird, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                        resultRectFirst  = resultSurfFirst.get_rect(topleft = (posX, posY))
                        posY += LINESPACING18
                        resultRectSecond = resultSurfSecond.get_rect(topleft = (posX, posY))
                        posY += LINESPACING18
                        resultRectThird  = resultSurfThird.get_rect(topleft = (posX, posY))
                        DISPLAYSURF.blit(resultSurfFirst, resultRectFirst)
                        DISPLAYSURF.blit(resultSurfSecond, resultRectSecond)
                        DISPLAYSURF.blit(resultSurfThird, resultRectThird)
                        pygame.display.update()
                        # Go to the next seat.
                        continue
                
                # Now, we print whichever set of text messages to the screen.
                # All of these messages do not involve eliminating players. So,
                # they can use a common block of render commands.
                resultSurfFirst  = SCOREFONT.render(resultTextFirst, True, TEXTCOLOR)
                resultSurfSecond = SCOREFONT.render(resultTextSecond, True, TEXTCOLOR)
                resultSurfThird  = SCOREFONT.render(resultTextThird, True, TEXTCOLOR)
                resultRectFirst  = resultSurfFirst.get_rect(topleft = (posX, posY))
                posY += LINESPACING12
                resultRectSecond = resultSurfSecond.get_rect(topleft = (posX, posY))
                posY += LINESPACING12
                resultRectThird  = resultSurfThird.get_rect(topleft = (posX, posY))
                DISPLAYSURF.blit(resultSurfFirst, resultRectFirst)
                DISPLAYSURF.blit(resultSurfSecond, resultRectSecond)
                DISPLAYSURF.blit(resultSurfThird, resultRectThird)
                pygame.display.update()
            
            else: # Player does not have an insurance bet. Go to the next seat.
                continue
        # Skip the empty seat.
    # The final step is to see if the dealer's bank busted after paying out
    # the insurance bets.
    dealerBank = tableObj.tableDealer.bank
    if dealerBank <= 0:
        # The user beat the dealer.
        playersWinGame()
    return remainginPlayers # resolveInsBets

def dealerHasBlackjack():
    """
    This function collects the user losses due to a dealer blackjack. It
    returns the number of players remaining in the game.
    INPUTS: None
    OUTPUTS: remainingPlayers, integer between 0 and 3
    """
    # First, we need to set up an aggregator for the dealer's winnings. We
    # also need to clear the status corner and reset the positionals. All
    # losses will printed out in the status corner together.  The dealer
    # cannot be eliminated by wins, but players may be eliminated by their
    # losses. We also need to tabulate surviving players.
    clearStatusCorner()
    posX = LEFTMARGIN
    posY = TOPMARGIN
    dealerWins = 0
    remainingPlayers = 0
    # We need to process all of the hands marked "playable". All of them 
    # are losses for the players in question.
    for hand in HANDLIST:
        seat, handType = hand.split(' ')
        print("dealerHasBlackjack: Status: Looking for playable hands. seat is {0}. handType is {1}. result is {2}".format(seat, handType, tableObj.results[hand]))
        if isPlayerStillThere(seat):
            # Incremement the player counter.
            remainingPlayers += 1
            if tableObj.results[hand] == 'playable':
                # Set this one to a loss.
                tableObj.results[hand] = 'loss'
                playerName = tableObj.players[seat].name
                if handType == 'split':
                    # This is a split hand.
                    betAmt = tableObj.players[seat].split_bet
                    playerStatus = tableObj.players[seat].split_loss()
                else: # This is regular hand.
                    betAmt = tableObj.players[seat].bet
                    playerStatus = tableObj.players[seat].reg_loss()
                dealerWins += betAmt
                # The player lost their bet regardless of what else happens.
                playerHandText = "{0} lost ${1} to dealer's blackjack.".format(playerName, betAmt)
                playerHandSurf = SCOREFONT.render(playerHandText, True, TEXTCOLOR)
                playerHandRect = playerHandSurf.get_rect(topleft = (posX, posY))
                posY += LINESPACING12
                DISPLAYSURF.blit(playerHandSurf, playerHandRect)
                # Now, we need to check the player's status. If they busted,
                # the status must indicated that.
                if playerStatus:
                    # Player survived the round.
                    playerStatusText = "{0} is still solvent.".format(playerName)
                    playerStatusSurf = SCOREFONT.render(playerStatusText, True, TEXTCOLOR)
                    playerStatusRect = playerStatusSurf.get_rect(topleft = (posX, posY))
                    posY += LINESPACING12
                else: # Player busted their bank.
                    playerStatusText = "{0} is insolvent and was eliminated.".format(playerName)
                    playerStatusSurf = PROMPTFONT.render(playerStatusText, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                    playerStatusRect = playerStatusSurf.get_rect(topleft = (posX, posY))
                    posY += LINESPACING18
                    eliminatePlayer(seat)
                    # Reduce the player counter.
                    remainingPlayers -+ 1
                # The status printout can use a common blit command block.
                DISPLAYSURF.blit(playerStatusSurf, playerStatusRect)
                pygame.display.update()
                pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
            # End of hand filter
        # End of check for occupied seat
    # End of for loop through HANDLIST
    return remainingPlayers # dealerHasBlackjack

def dealerBusts(rounds):
    """
    This function handles the automatic wins for players with playable hands.
    It returns True if the dealer is solvent, or False otherwise.
    INPUTS: rounds, integer current number of the round of play
    OUTPUTS: None. All output is to the game screen.
    """
    # First, clear the status corner and reset the positionals. We need an
    # aggregator for the dealer's losses, in case this causes the dealer to
    # break their bank. We don't need a player counter because none of the
    # remaining players will be eliminated by winning these hands.
    clearStatusCorner()
    posX = LEFTMARGIN
    posY = TOPMARGIN
    dealerLosses = 0
    # We need find and process all of the playable hands.
    for hand in HANDLIST:
        seat, handType = hand.split(' ')
        print("dealerBusts: Status: Looking for playable hands. seat is {0}. handType is {1}. result is {2}.".format(seat, handType, tableObj.results[hand]))
        if isPlayerStillThere(seat):
            if tableObj.results[hand] == 'playable':
                # Change the result to 'win'
                tableObj.results[hand] = 'win'
                playerName = tableObj.players[seat].name
                if handType == 'split':
                    # This is a split hand.
                    betAmt = tableObj.players[seat].split_bet
                    # We do not need a status since players are not eliminated
                    # for winning bets.
                    tableObj.players[seat].split_win()
                else: # This is a regular hand.
                    betAmt = tableObj.players[seat].bet
                    tableObj.players[seat].win()
                dealerLosses += betAmt
                playerHandText = "{0} won their bet of ${1}.".format(playerName, betAmt)
                playerHandSurf = SCOREFONT.render(playerHandText, True, TEXTCOLOR)
                playerHandRect = playerHandSurf.get_rect(topleft = (posX, posY))
                posY += LINESPACING12
                DISPLAYSURF.blit(playerHandSurf, playerHandRect)
                pygame.display.update()
                pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
            # End of hand filter
        # End of check for occupied seat
    # End of for loop through HANDLIST
    # Now, we need to apply the dealer's losses and see if the dealer has
    # broken their bank.
    dealerStatus = tableObj.tableDealer.dealer_lost(dealerLosses)
    if dealerStatus:
        # The dealer survived busting their hand.
        refreshTable('dealer', rounds)
        posX = LEFTMARGIN
        posY = TOPMARGIN
        dealerStatusText = "Dealer remains solvent."
        dealerStatusSurf = PROMPTFONT.render(dealerStatusText, True, TEXTCOLOR)
        dealerStatusRect = dealerStatusSurf.get_rect(topleft = (posX, posY))
        DISPLAYSURF.blit(dealerStatusSurf, dealerStatusRect)
        pygame.display.update()
        pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
        return
    else: # Dealer busted their bank.
        DISPLAYSURF.fill(BLACK)
        posX = WINCENTERX
        posY = WINCENTERY
        dealerStatusText = "Dealer is now insolvent and has been eliminated."
        dealerStatusSurf = PROMPTFONT.render(dealerStatusText. True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
        dealerStatusRect = dealerStatusSurf.get_rect(topleft = (posX, posY))
        DISPLAYSURF.blit(dealerStatusSurf, dealerStatusRect)
        pygame.display.update()
        pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
        playersWinGame()
    return # dealersBusts   

def findDefunctPlayer():
    """
    This function checks all remaining players to see if any should be
    eliminated. It notifies the user of each deletion.
    INPUTS:
    OUTPUTS: remainingPlayers, integer from 0 to 3
    """
    # First, we need to clear the status corners, reset positionals, and 
    # start a player counter.
    clearStatusCorner()
    posX = LEFTMARGIN
    posY = TOPMARGIN
    remainingPlayers = 0
    for seat in TABLESEATS:
        if isPlayerStillThere(seat):
            # Increment player counter.
            remainingPlayers += 1
            # Now, we need to check their bank and their name.
            playerName = tableObj.players[seat].name
            playerBank = tableObj.players[seat].bank
            if playerBank <= 0:
                # This player busted their bank at some point.
                playerStatusTextFirst  = "{0} has a bank of {1}.".format(playerName, playerBank)
                playerStatusTextSecond = "This player has been eliminated."
                playerStatusSurfFirst  = PROMPTFONT.render(playerStatusTextFirst, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                playerStatusSurfSecond = PROMPTFONT.render(playerStatusTextSecond, True, ELIMINATIONCOLOR, ELIMINATIONBGCOLOR)
                playerStatusRectFirst  = playerStatusSurfFirst.get_rect(topleft = (posX, posY))
                posY += LINESPACING18
                playerStatusRectSecond = playerStatusSurfSecond.get_rect(topleft = (posX, posY))
                posY += LINESPACING18
                DISPLAYSURF.blit(playerStatusSurfFirst, playerStatusRectFirst)
                DISPLAYSURF.blit(playerStatusSurfSecond, playerStatusRectSecond)
                pygame.display.update()
                eliminatePlayer(seat)
                remainingPlayers -= 1
                pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
            # End of check for player insolvency
        # End of check for occupied seat
    # End of for loop through table seats
    return remainingPlayers # findDefunctPlayers                

def endOfRound(rounds):
    """
    This function clears out the bets and hands from the round. It finishs
    distributing wins and losses by the players and the dealer. It also
    gives the user an analysis of the viability of the remaining players to
    help the user decide who to withdraw (if any) at the start of the next
    round. This analysis is similar to the report main() prints out when the
    user chooses a dealer. The final thing it does is give the user the
    option to replace the CardShoe. If the CardShoe is down to 100 cards or
    less, it will do it automatically.
    INPUTS: rounds, integer number of the current round
    OUTPUTS: None. All output is to the game screen
    """
    # First, we start with resetting the data for the players. The Player
    # and Dealer Classes have an end_round() method that resets eveything
    # except the name and bank of both.
    for seat in TABLESEATS:
        if isPlayerStillThere(seat):
            # We cannot reset data that isn't there to begin with.
            tableObj.players[seat].end_round()
    # Now, run the end_round() method for the Dealer.
    tableObj.tableDealer.end_round()
    refreshTable('end', rounds)
    
    # Now, all of the bets, hands, and flags have been reset. The next step
    # is to analyze the viability of each player, so that the user can make
    # an informed decision about which players to withdraw at the beginining
    # of the next round.
    # Clear the status corner and reset positionals.
    clearStatusCorner()
    posX = LEFTMARGIN
    posY = TOPMARGIN
    for seat in TABLESEATS:
        if isPlayerStillThere(seat):
            playerName = tableObj.players[seat].name
            playerBank = tableObj.players[seat].bank
            tableMin = tableObj.min_bet
            # We need to calculate how many rounds the player can survive
            # with only a minimum ante bet.
            playerSurvival = 0
            while (playerSurvival <= 20) and (playerSurvival * tableMin < playerBank):
                playerSurvival += 1
            # The routine the main() function is a little less complete than
            # this one will be. First, we need to determine if any players
            # will be unable to make the ante next round.
            if playerBank < tableMin:
                warningTextFirst  = "{0} cannot afford the ante next round.".format(playerName)
                warningTextSecond = "Withdraw this player at the start of."
                warningTextThird  = "the next round to prevent elimination."
            elif 1 <= playerSurvival <= 20:
                # This player can ante up at least. They can survive up to
                # ten rounds as well.
                warningTextFirst  = "{0} can survive at least {1} rounds making".format(playerName, playerSurvival)
                warningTextSecond = "minimum bets. This is a small number."
                warningTextThird  = "Consider withdrawing this player soon."
            else: # The player is viable.
                warningTextFirst  = "{0} can survive more than {1} round making".format(playerName, playerSurvival)
                warningTextSecond = "minmum bets. This player should be viable"
                warningTextThird  = "for several more rounds."
            warningSurfFirst  = PROMPTFONT.render(warningTextFirst, True, TEXTCOLOR)
            warningSurfSecond = PROMPTFONT.render(warningTextSecond, True, TEXTCOLOR)
            warningSurfThird  = PROMPTFONT.render(warningTextThird, True, TEXTCOLOR)
            warningRectFirst  = warningSurfFirst.get_rect(topleft = (posX, posY))
            posY += LINESPACING18
            warningRectSecond = warningSurfSecond.get_rect(topleft = (posX, posY))
            posY += LINESPACING18
            warningRectThird  = warningSurfThird.get_rect(topleft = (posX, posY))
            posY += LINESPACING18
            DISPLAYSURF.blit(warningSurfFirst, warningRectFirst)
            DISPLAYSURF.blit(warningSurfSecond, warningRectSecond)
            DISPLAYSURF.blit(warningSurfThird, warningRectThird)
            pygame.display.update()
        # End of occupied seat filter.
    # End of for loop through seats.
    pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)

    # Now, we need to check the CardShoe to see if it has at least 100 cards
    # left in it. Each round, the user can ask for a new shoe (six decks of
    # 52 cards each). When the deck drop to 100 cards, it is replaced
    # automatically. The replaceDeck boolean allows us to use a common set of
    # display commands.
    # The analysis can run fairly far down the screen. So, it is better to
    # refresh the entire screen this time.
    refreshTable('end', rounds)
    posX = LEFTMARGIN
    posY = TOPMARGIN
    remainingCards = len(tableObj.deck)
    replaceDeck = False
    if remainingCards < 100:
        deckReplaceTextFirst  = "The casino replaces card shoes below 100"
        deckReplaceTextSecond = "cards remaining. This one has {0}.".format(remainingCards)
        deckReplaceTextThird  = "The card shoe will be replaced with a new one."
        replaceDeck = True
        # Flipping this flag to True means that the checkForYesNo will be
        # skipped further below.
    else:
        deckReplaceTextFirst  = "The current deck show has {0} card left.".format(remainingCards)
        deckReplaceTextSecond = "While this is higher than the 100 card"
        deckReplaceTextThird  = "minimum, I will replace it if you want me to."
    # Here is the common printout block.
    deckReplaceSurfFirst  = PROMPTFONT.render(deckReplaceTextFirst, True, TEXTCOLOR)
    deckReplaceSurfSecond = PROMPTFONT.render(deckReplaceTextSecond, True, TEXTCOLOR)
    deckReplaceSurfThird  = PROMPTFONT.render(deckReplaceTextThird, True, TEXTCOLOR)
    deckReplaceRectFirst  = deckReplaceSurfFirst.get_rect(topleft = (posX, posY))
    posY += LINESPACING18
    deckReplaceRectSecond = deckReplaceSurfSecond.get_rect(topleft = (posX, posY))
    posY += LINESPACING18
    deckReplaceRectThird  = deckReplaceSurfThird.get_rect(topleft = (posX, posY))
    posY += LINESPACING18
    DISPLAYSURF.blit(deckReplaceSurfFirst, deckReplaceRectFirst)
    DISPLAYSURF.blit(deckReplaceSurfSecond, deckReplaceRectSecond)
    DISPLAYSURF.blit(deckReplaceSurfThird, deckReplaceRectThird)
    pygame.display.update()
    if replaceDeck:
        tableObj.deck.replace_cardshoe()
        deckReplaceTextFourth = "Deck shoe has been replaced."
        deckReplaceSurfFourth = PROMPTFONT.render(deckReplaceTextFourth, True, TEXTCOLOR)
        deckReplaceRectFourth = deckReplaceSurfFourth.get_rect(topleft = (posX, posY))
        DISPLAYSURF.blit(deckReplaceSurfFourth, deckReplaceRectFourth)
        pygame.display.update()
        refreshTable('end', rounds)
        pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
    else: # The user can choose to replace it.
        deckReplaceTextFourth = "Would like me to replace the deck shoe?"
        deckReplaceSurfFourth = PROMPTFONT.render(deckReplaceTextFourth, True, TEXTCOLOR)
        deckReplaceRectFourth = deckReplaceSurfFourth.get_rect(topleft = (posX, posY))
        DISPLAYSURF.blit(deckReplaceSurfFourth, deckReplaceRectFourth)
        pygame.display.update()
        replaceDeck = checkForYesNo(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
        # Now, we will replace it depending on the players choice. Either way
        # we need to clear the screen and reset the positionals.
        refreshTable('end', rounds)
        posX = LEFTMARGIN
        posY = TOPMARGIN
        if replaceDeck:
            tableObj.replace_cardshoe()
            deckReplaceTextFifth = "Deck shoe has been replaced."
        else: # User kept the deck shoe as is.
            deckReplaceTextFifth = "Deck shoe has not been replaced."
        # Common display block.
        deckReplaceSurfFifth = PROMPTFONT.render(deckReplaceTextFifth, True, TEXTCOLOR)
        deckReplaceRectFifth = deckReplaceSurfFifth.get_rect(topleft = (posX, posY))
        DISPLAYSURF.blit(deckReplaceSurfFifth, deckReplaceRectFifth)
        pygame.display.update()
        pressSpaceToContinue(STATUSBLOCKWIDTH, STATUSBLOCKHEIGHT)
    
    # Finally, we need to return the hand results to None.
    for hand in HANDLIST:
        tableObj.results[hand] = None
    print("endOfRound: Hand Results are now {0}.".format(tableObj.results))
    return # endOfRound

def checkPlayerExperienceLevels():
    """
    This function checks the number of rounds the players have played and
    levels them up in listPlayers if they have played enough rounds. This
    function also informs the user of the changes.
    """

def playersWinGame():
    """
    This function will handle the players breaking the bank for the table
    they were playing at.
    """
    pass

def userLostGame():
    """
    This function will handle the case of all players being eliminated from
    the game. In that case, the user should be prompted about whether or not
    they want to keep a saved game file, if one exists. A thank you message
    should also be issued, then the game will spacebar pause and then exit.
    """
    pass

if __name__ == '__main__':
    main()
