from __future__ import print_function
import random, os, pygame, inflection, collections
from pygame.locals import *
from lib import CardShoe, Player, Dealer, CasinoTable
import pdb

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


# Pygame Constants. All of these values are in pixels
FPS = 30
WINDOWWIDTH   = 1024                    # Width of game window
WINDOWHEIGHT  =  768                    # Height of game window
WINCENTERX    = int(WINDOWWIDTH / 2)    # X coordinate of window's center
WINCENTERY    = int(WINDOWHEIGHT / 2)   # Y coordinate of winwow's center
CARDWIDTH     =   45                    # Width of a card image
CARDSPACING   =    3                    # Spacing between cards (both axes)
CARDHEIGHT    =   70                    # Height of a card image
LINESPACING   =   15                    # Spacing between text Rect objects
TABLEWIDTH    =  700                    # width of playing table
TABLEHEIGHT   =  450                    # height of playing table
TABLERIM      =   40                    # width of band around table
STATIONWIDTH  =  250                    # width of dealer's station
STATIONHEIGHT =   60                    # height of dealer's station

DEALERSCARDS  =  220                    # Y position in front of dealer's
                                        # where Dealer's cards are dealt.
                                        # WINCENTERX is the X coordinate that
                                        # that cards bracket.

BGCOLOR   = DIMGRAY
TEXTCOLOR = WHITE

def main(): # main game function
    global FPSCLOCK, DISPLAYSURF, CARDIMAGES, BLANKCARD, BASICFONT, SCOREFONT, DATAFONT

    # Pygame initialization.
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    # The Surface object is stored in DISPLAYSURF, which is returned from
    # pygame.display.set_mode() function calls. This object is not drawn to
    # the screen until pygame.display.update() is called.
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    pygame.display.set_caption('Casino Blackjack')
    DISPLAYSURF.fill(BGCOLOR)

    # The next stanza sets the default text font for the game to GNU Free Sans
    # TTF. If it is not found in etc, it defaults to freesansbold.ttf which is
    # part of Pygame.
    try:
        BASICFONT = pygame.font.Font('etc/FreeSans.ttf', 12)
    except:
        # FreeSans.ttf could not be found or could not be used.
        BASICFONT = pygame.font.Font('freesansbold.ttf', 12)        

    # The next stanza sets the SCOREFONT for the game to GNU Free Serif TTF.
    # If it is not found in etc, it defaults to freesansbold.ttf which is
    # part of Pygame.
    try:
        SCOREFONT = pygame.font.Font('etc/FreeSerif.ttf', 12)
    except:
        # FreeSerif.ttf could not be found or could not be used.
        SCOREFONT = pygame.font.Font('freesansbold.ttf', 12)
    
    # The next stanza sets the DATAFONT for the game to GNU Free Serif TTF.
    # If it is not found in etc, it defaults to freesansbold.ttf which is
    # part of Pygame.
    try:
        DATAFONT = pygame.font.Font('etc/FreeMono.ttf', 14)
    except:
        # FreeMono.ttf could not be found or could not be used.
        DATAFONT = pygame.font.Font('freesansbold.ttf', 14)        

    # This stanza imports the table image and converts it into a Surface and
    # a Rect object so that it can be displayed on screen. 
    # tableSURF   = pygame.image.load('graphics/FivePlayerTable.png')
    # This stanza creates the table surface. It is composed of a brown oval
    # a green oval, a black rectangle (dealer's station), and areas where
    # player cards will be dealt. These Rect objects use the form:
    # pygame.Rect((left, top), (width, height)). The formulas are calculating
    # the X and Y distances to the (left, top) from the CENTER of the game
    # window.
    tableOuterRect = pygame.Rect((WINCENTERX - int(TABLEWIDTH / 2), WINCENTERY - int(TABLEHEIGHT / 2)), (TABLEWIDTH, TABLEHEIGHT))
    tableInnerRect = pygame.Rect((WINCENTERX - int((TABLEWIDTH - TABLERIM) / 2), WINCENTERY - int((TABLEHEIGHT - TABLERIM) / 2)), (TABLEWIDTH - TABLERIM + 1, TABLEHEIGHT - TABLERIM + 1))
    pygame.draw.ellipse(DISPLAYSURF, OLIVE, tableOuterRect, TABLERIM)
    pygame.draw.ellipse(DISPLAYSURF, LIME, tableInnerRect)
    dealerStationRect = pygame.Rect((WINCENTERX - int(STATIONWIDTH / 2), DEALERSCARDS - CARDSPACING - STATIONHEIGHT), (STATIONWIDTH, STATIONHEIGHT))
    pygame.draw.rect(DISPLAYSURF, BLACK, dealerStationRect)

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
    # (card) --> {'image'    : loaded graphics file of the tuple specified card
    #             'surface'  : a surface object made from the file, scaled to
    #                          45x70 pixels for display
    #             'rect'     : a rect object large enough to display the
    #                          Surface object}
    # BLANKCARD is the simpler process, but it lays out the steps in building
    # the full nested dictionary, CARDIMAGES.
    BLANKCARD = {}
    BLANKCARD['image']     = pygame.image.load('graphics/Blank.png')
    BLANKCARD['surface']   = BLANKCARD['image'].convert()
    BLANKCARD['rect']      = BLANKCARD['surface'].get_rect()
    BLANKCARD['rect']      = BLANKCARD['rect'].inflate(45, 70)
    
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
        CARDIMAGES[card]['surface'] = CARDIMAGES[card]['image'].convert()
        CARDIMAGES[card]['rect']    = CARDIMAGES[card]['surface'].get_rect()
        CARDIMAGES[card]['rect']    = CARDIMAGES[card]['rect'].inflate(45, 70)
    # Diagnostic print to see if these cards were setup correctly.
    # cardImagesDiagnosticPrint()
    
    # Defining the next item for the purpose of testing the printouts.
    tempDealer = {}
    tempDealer['name'] = "Fred"
    tempDealer['bank'] = 100000
    tempDealer['hand'] = [('A', 'D'), ('J', 'S')]
    # tempDealer['hand'] = [('A', 'D')]
    # tempDealer['hand'] = None
    tempDealer['soft score'] = 21
    tempDealer['hard score'] = 11
    tempDealer['visible card'] = tempDealer['hand'][1]
    # tempDealer['visible card'] = None
    tempDealer['visible soft score'] = 10
    tempDealer['visible hard score'] = 10
    tempDealer['dealer turn'] = None
    printTableDealer(tempDealer, 'diagnostic')

    # Update the screen before recycle.
    pygame.display.update()
    FPSCLOCK.tick()

def cardImagesDiagnosticPrint(adjX=0, adjY=0):
    """
    This function prints out all 52 cards to verify spacing and apperance.
    INPUT: optional posX and posY adjustments, defaults are 30 (LINESPACING)
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

def diagnosticPrint(output = ''):
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
    When player(s) pick a table to play at, a tableObject is created. Before
    that, it does not exist. The tableObject has a Dealer object and up to
    five player objects that manage their hands, banks, and betting options.
    Since this is partly a diagnostic function, we cannot assume that any of
    these objects exist.
    INPUT: option 'v' or 'verbose' argument (all other strings are ignored)
    OUTPUT: A quick visual printout of the contents of the active objects in
        the current game. If the verbose option is requested, it will also
        issue the dianostic_print() methods for the classes CasinoTable,
        Player, Dealer, and CardShoe. The latter outputs should go to the
        terminal output.
    """
    # First, clear the screen.
    DISPLAYSURF.fill(BGCOLOR)
    posY = LINESPACING
    
    # See if a table object exists.
    if tableObject and type(tableObject) == 'CasinoTable':
        tableObjectInfoSurf = BASICFONT.render('A CasinoTable object exists', True, TEXTCOLOR)
        tableObjectInfoRect = tableObjectInfoSurf.get_rect()
        tableObjectInfoRect.center = (WINCENTERX, posY)
        DISPLAYSURF.blit(tableObjectInfoSurf, tableObjectInfoRect)
        posY += LINESPACING
        if output == 'v' or output == 'verbose':
            tableObject.diagnostic_print()

        # Checking tableObject for a Dealer object. If it does, the __str__()
        # method will provide a dictionary with all of the Dealer's data,
        # including cards, both visible and masked. The dictionary's structure:
        #   'name'               : dealer's name (aka "Dealer")
	#   'bank'               : dealer's bank
	#   'hand'               : dealer's hand or None (a list)
	#   'soft score'         : soft score for dealer's hand or None
	#   'hard score'         : hard score for dealer's hand or None
	#   'visible card'       : a tuple of the hand[0] or None
	#   'visible soft score  : soft score of the visible card
	#   'visible hard score  : hard score of the visible card
	#   'dealer turn'        : set to None
	# We send this data object to printTableDealer to print it out to
	# avoid as much duplication of code as possible.
        if tableObject.tableDealer and type(tableObject.tableDealer) == 'Dealer':
            tableObjectInfoSurf = BASICFONT.render('A Dealer object was found inside the CasinoTable', True, TEXTCOLOR)
            tableObjectInfoRect = tableObjectInfoSurf.get_rect()
            tableObjectInfoRect.center = (WINCENTERX, posY)
            DISPLAYSURF.blit(tableObjectInfoSurf, tableObjectInfoRect)
            posY += LINESPACING
            tableDealer = print(tableObject.tableDealer)
            printTableDealer(tableDealer, 'diagnostic')

        if tableObject.players:
            pass

    else: # tableObject is not defined.
        tableObjectInfoSurf = BASICFONT.render('No CasinoTable object found', True, TEXTCOLOR)
        tableObjectInfoRect = tableObjectInfoSurf.get_rect()
        tableObjectInfoRect.center = (WINCENTERX, posY)
        DISPLAYSURF.blit(tableObjectInfoSurf, tableObjectInfoRect)
        posY += LINESPACING


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
    posY = 2 * LINESPACING
    if output == 'dealer turn':
        outputTypeSurf = DATAFONT.render("Dealer's Turn", True, TEXTCOLOR)
    elif output == 'diagnostic':
        outputTypeSurf = DATAFONT.render("Diagnostic Printout", True, TEXTCOLOR)
    else: # Default behavior as 'player turn'.
        outputTypeSurf = DATAFONT.render("Players' Turn", True, TEXTCOLOR)
    outputTypeRect = outputTypeSurf.get_rect()
    outputTypeRect.center = (WINCENTERX, posY)
    DISPLAYSURF.blit(outputTypeSurf, outputTypeRect)
    posY += 2 * LINESPACING
    dealerNameSurf = BASICFONT.render("Dealer's Name: %s" % (tableDealer['name']), True, TEXTCOLOR)
    dealerNameRect = dealerNameSurf.get_rect()
    dealerNameRect.center = (WINCENTERX, posY)
    DISPLAYSURF.blit(dealerNameSurf, dealerNameRect)
    posY += LINESPACING
    dealerBankSurf = BASICFONT.render("Dealer's Bank: %s" % (tableDealer['bank']), True, TEXTCOLOR)
    dealerBankRect = dealerBankSurf.get_rect()
    dealerBankRect.center = (WINCENTERX, posY)
    DISPLAYSURF.blit(dealerBankSurf, dealerBankRect)
    posY += LINESPACING

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
        posY += LINESPACING

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
        posY += LINESPACING
        dealerSoftScoreSurf = SCOREFONT.render("Dealer's soft score: %s" % (tableDealer['soft score']), True, TEXTCOLOR)
        dealerSoftScoreRect = dealerSoftScoreSurf.get_rect()
        dealerSoftScoreRect.center = (WINCENTERX, posY)
        DISPLAYSURF.blit(dealerSoftScoreSurf, dealerSoftScoreRect)
        posY += LINESPACING
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
        posY += LINESPACING
    
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
            visCard = tableDealer['visible card']
            dealerVisCardSurf = CARDIMAGES[visCard]['surface']
            dealerVisCardRect = CARDIMAGES[visCard]['rect']
            dealerVisCardRect.topleft = (posXVisCard, posYVisCard)
            DISPLAYSURF.blit(dealerVisCardSurf, dealerVisCardRect)
            dealerVisHardScoreSurf = SCOREFONT.render("Dealer is showing a hard score: %s" % (tableDealer['visible hard score']), True, TEXTCOLOR)
            dealerVisHardScoreRect = dealerVisHardScoreSurf.get_rect()
            dealerVisHardScoreRect.center = (WINCENTERX, posY)
            DISPLAYSURF.blit(dealerVisHardScoreSurf, dealerVisHardScoreRect)
            posY += LINESPACING
            dealerVisSoftScoreSurf = SCOREFONT.render("Dealer is showing a soft score: %s" % (tableDealer['visible soft score']), True, TEXTCOLOR)
            dealerVisSoftScoreRect = dealerVisSoftScoreSurf.get_rect()
            dealerVisSoftScoreRect.center = (WINCENTERX, posY)
            DISPLAYSURF.blit(dealerVisSoftScoreSurf, dealerVisSoftScoreRect)
            posY += LINESPACING
                
    pygame.display.update()
    FPSCLOCK.tick()
    return # printTableDealer
    
if __name__ == '__main__':
    main()
