from __future__ import print_function
import string, os, pygame
from pygame.transform import scale
from pygame.locals import *
import pdb

class Textbox(object):
    """
    This class creates an interactive textbox on a Pygame display surface.
    These textboxes allow for filtering by three character types: alphabetical
    only, numerical only, or alphanumberics only. This makes it possible to
    control input for bets to numbers, while only allowing alphabetical
    characters for names. This class accepts the following arguments:

    Class Order Attributes:
        Filter constants (see below): Used to control what type(s) of
            characters are allowed in the textbox.
        FILTERDICT: Dictionary mapping filter types to the character sets.
            'alpha'       : ALPHAFILTER
            'number'      : NUMERICALFILTER
            'alphanum'    : ALPHANUMFILTER
            'punctuation' : PUNCTFILTER
            'white space' : WHITESPACEFILTER
            'any'         : PRINTABLEFILTER
        BLINKSPEED: The number of milliseconds for each part of the blink cycle.
        FPS: The number of frames per second the Textbox uses.
        OUTLINEWIDTH: Width of the Textbox outline in pixels. This is a default
            that can be overridden by a kwarg.
        DEFAULTFONT: This is set to freesansbold.ttf because that is included
            with Pygame. If pygame is installed properly, this font will be
            available, even if no others are available.
        DEFAULTBOXWIDTH: Default width of the textbox in characters.
        DEFAULTBOXHEIGHT: Default height of the textbox in pixels.
        DEFAULTOFFSET: This is maximum acceptable difference in width between
            the original textbox (self.rect) and the rendered version after
            a character has been added to the self.buffer. This creates an
            offset to adjust the content accordingly.
        Color List: A list of colors constants to make the code more readable.
            The values are standard names for these RGB color values.

    Attributes:
        rect: This is the Rect object for the textbox itself.
        buffer: Stores the string the user needs to input as a list of
            characters.
        finalBuffer: Stores the final contents of the buffer as a string.
        textSurf: Stores the surface created by pygame font.render() method
            applied to the user's text as it is entered in the box.
        textRect: Stores the rect object created by the surface.get_rect()
            method.
        warningSurf: Used to print warnings when invalid characters were typed
            or entered
        warningRect: Rect object to contain the warning surface
        screenRender: <I need to figure out what render_area's Rect object does>
            I think this is used when the buffer text is longer than entry box
        blink (boolean): True means flash, False turn of flash. Cycles back
            and forth to make the textbox seem to blink on and off.
        blinkTimer: Number of miliseconds between blink cycles.
        filter: Contains the string constant from FILTERDICT for the character
            filter (if any) that is needed. Default is PRINTABLEFILTER.
        defaults: Stores the values of kwargs (see below) as a dictionary.

    kwargs:
        id: This kwarg identifies which process called this class; so that
            the data can be sent back to it.
        command: Stores any internal method or external function or method
            that the game should execute from the text entered. Default
            is None.
        active: Controls if the box can be used currently, True = Yes, False
            = No. Default is True.
        fillColor: Color that will fill the textbox. Default is WHITE.
        fontColor: Color of the characters that appear when the user types
            text in the textbox. Default is BLACK.
        outlineColor: Color of the outline of the textbox. Default is BLACK.
        outlineWidth: Width of the box outline, in pixels. Has a class order
            attribute default of OUTLINEWIDTH.
        activeColor: Color of the textbox when it is active (if it applies).
            Default is BLUE.
        inactiveColor: Color of the textbox when it is inactive (if it
            applies). Default is GRAY.
        charFilter: String values that FILTERDICT transforms into a character
	    filter (see FILTERDICT below). Default is 'any' for any printable.
	boxFont: Font used in the textbox. Default is DEFAULTFONT (see below).
	warningFont: Font used to display warning text. Default is DEFAULTFONT (see
            below).
        warningColor: Color of text warnings for invalid characters entered or
            typed in the text box. Default is RED.
        boxWidth: Width, in characters, for the textbox. Default is class
            order attribute DEFAULTBOXWIDTH.
        enterClears: Boolean that controls whether or not the text in the box
            clears when enter/return is pressed. Default is False.
        enterDeactivates: Boolean that controls whether or not the textbox
            becomes inactive once enter is pressed. Default is True.

    Methods:
        __init__: Creates the initial Textbox object, setting any characters
            assigned to the Textbox. The default filter is any printable
            charcter (PRINTABLEFILTER).
        process_kwargs: Looks for arguments that override the default behavior
            and updates the defaults dictionary that stores them.
        getEvent: This method looks for KEYDOWNs and MOUSEBUTTONDOWN events
            that need to be acted on by the textbox.
        executeCommand: Sends the command back to the calling program.
        issueWarning: Creates a warning text that the charcter entered is
            not acceptable under the current filter.
        clearBox
        updateBox
        drawBox
    """
    # Class order attributes.
    # The first set are filters for the characters allowed in the Textbox
    # object. These filters use the string constants.
    ALPHAFILTER      = string.ascii_letters
    NUMERICALFILTER  = string.digits
    ALPHANUMFILTER   = ALPHAFILTER + NUMERICALFILTER
    PUNCTFILTER      = string.punctuation
    WHITESPACEFILTER = string.whitespace
    PRINTABLEFILTER  = string.printable

    # The next set are 
    BLINKSPEED       = 200  # Lenght of blink cycle in milliseconds
    FPS              = 30   # Minimum frames per second for Textbox
    OUTLINEWIDTH     = 2    # Defautl pixel width of box outline
    DEFAULTBOXWIDTH  = 10   # Default number characters displayable in textbox
    DEFAULTBOXHEIGHT = 100  # Default height of textbox in pixels
    DEFAULTOFFSET    = 6    # The maximum offset between original textbox
                            # and the text rendered inside it.

    # The default font is set to the one included with Pygame, just in case
    # there is no other accessible font.
    DEFAULTFONT      = 'freesansbold.ttf'
    DEFAULTFONTSIZE  = 12

    FILTERDICT = { 'alpha'       : ALPHAFILTER,
                   'number'      : NUMERICALFILTER,
                   'alphanum'    : ALPHANUMFILTER,
                   'punctuation' : PUNCTFILTER,
                   'whitespace'  : WHITESPACEFILTER,
                   'any'         : PRINTABLEFILTER }

    # Color List:
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

    
    def __init__(self, rect, **kwargs):
        """
        __init__ generates the Textbox object. The defaults for the kwargs
        can be found in the process_kwargs method.
        """
        # These are the attributes that need to be initialized.
        self.rect         = pygame.Rect(rect)
        self.buffer       = []
        self.finalBuffer  = None
        self.textSurf     = None
        self.textRect     = None
        self.warningSurf  = None
        self.warningRect  = None
        self.screenRender = None
        self.blink        = True
        self.blinkTimer   = 0.0
        # Note: filter is set in process_kwargs() as well.
        
        # Now, we shift control to the process_kwargs() method to change any
        # of the defaults that need to be modified.
        self.process_kwargs(kwargs)

        # Once it returns, we need to set the character filter.
        if self.charFilter in self.FILTERDICT:
            self.filter = self.FILTERDICT[self.charFilter]
        else:
            raise KeyError("Character filter type {} is not a valid character filter.".format(self.charFilter))
        # Now, we need to set up the fonts this module uses.
        if self.boxFont in pygame.font.get_fonts():
            self.boxFont = pygame.font.Font(self.boxFont, self.fontSize)
        else:
            self.boxFont = pygame.font.Font(self.DEFAULTFONT, self.fontSize)
        if self.warningFont in pygame.font.get_fonts():
            self.warningFont = pygame.font.Font(self.warningFont, self.fontSize)
        else:
            self.warningFont = pygame.font.Font(self.DEFAULTFONT, self.fontSize)
        
    def process_kwargs(self, kwargs):
        """
        This method takes the list of kwargs and changes the defaults
        dictionary to acccommodate the desired values. It also ensures that
        the remaining defaults are propagated appropriately. See main comment
        block for an explanation of these kwargs.

        The defaults are:
            'id'            : None (Used when textbox has to return a value)
            'command'       : None (Only used if the text is a game command)
            'active'        : True (False when the box cannot be used)
            'fillColor'     : WHITE (see color list above)
            'fontColor'     : BLACK
            'outlineColor'  : BLACK
            'outlineWidth'  : OUTLINEWIDTH
            'activeColor'   : BLUE
            'inactiveColor' : GRAY
            'charFilter'    : 'any' (Converts to PRINTABLEFILTER)
            'fontSize'      : DEFAULTFONTSIZE
            'boxFont'       : DEFAULTFONT
            'warningFont'   : DEFAULTFONT
            'warningColor'  : RED
            'boxWidth'      : DEFAULTBOXWIDTH
            'enterClears'   : False
            'enterDeactivates' : True
        All constants/class order attributes are in all caps. They can be
        found above.
        """
        defaults = {'id'            : None,
                    'command'       : None,
                    'active'        : True,
                    'fillColor'     : self.WHITE,
                    'fontColor'     : self.BLACK,
                    'outlineColor'  : self.BLACK,
                    'outlineWidth'  : self.OUTLINEWIDTH,
                    'activeColor'   : self.BLUE,
                    'inactiveColor' : self.GRAY,
                    'charFilter'    : 'any',
                    'fontSize'      : self.DEFAULTFONTSIZE,
                    'boxFont'       : self.DEFAULTFONT,
                    'warningFont'   : self.DEFAULTFONT,
                    'warningColor'  : self.RED,
                    'boxWidth'      : self.DEFAULTBOXWIDTH,
                    'enterClears'   : False,
                    'enterDeactivates' : True }
        for kwarg in kwargs:
            if kwarg in defaults:
                defaults[kwarg] = kwargs[kwarg]
            else:
                raise KeyError("Textbox accepts no keyword {}.".format(kwarg))
        self.__dict__.update(defaults)

    def terminate(self):
        """
        This method acts on detected QUIT events and terminates the program.
        """
        pygame.quit()
        sys.exit()

    def getEvent(self, event):
        """
        This method checks for mouse and keyboard events that are needed by
        this class to perform its operations. These events are KEYDOWN (keys
        pressed), and MOUSEBUTTONDOWN (mouse buttons pressed inside the entry
        box). The KEYDOWN needs to be an acceptable one from the character
        filter on the input or an exit event, which runs the terminate()
        method.
        """
        if event.type == KEYDOWN and self.active:
            if event.key in (K_RETURN, K_KP_ENTER):
                # If return or enter were pressed, we need to transfer
                # control to executeCommand to see if this Textbox is
                # sending a command to the game that called it.
                self.executeCommand()
            elif event.key == K_BACKSPACE:
                # If the key was a backspace, we need to remove a character
                # from the buffer.
                if self.buffer:
                    self.buffer.pop()
            elif event.unicode in self.filter:
                # The character is an acceptable one for this textbox. So,
                # it is added to the buffer.
                self.buffer.append(event.unicode)
            elif event.unicode not in self.filter:
                # In the case of an invalid character, like a digit for a
                # alphabetical, or whitespace in alphanumberics only, we
                # transfer control to the issueWarning method.
                self.issueWarning(event.unicode)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            # This event is a left button on the mouse was pressed. We need
            # to check if the position is inside the textbox or not. If so,
            # the textbox will become active.
            self.active = self.rect.collidepoint(event.pos)

    def executeCommand(self):
        if self.command:
            self.command(self.id, self.finalBuffer)
        # We need to change the status of the textbox if enterDeactivates is
        # set to True.
        self.active = not self.enterDeactivates
        # Likewise, if enterClears is True, we need to clear the textbox
        # contents.
        if self.enterClears:
            self.buffer = []

    def issueWarning(self, badChar):
        """
        This method creates the warning surfaces that warn users that they
        entered the wrong type(s) of characters.
        """
        if self.charFilter == 'any':
            message = "{} is not a valid character. Please use only printable characters.".format(badChar)
        else:
            message = "{} is not a valid character. Please use only {} characters.".format(badChar, self.charFilter)
        self.warningSurf = self.warningFont.render(message, True, self.warningColor)
        self.warningRect = self.warningSurf.get_rect()
    
    def updateBox(self):
        """
        This method updates the content of the textbox. As the user adds
        new characters, this method adds them to the buffer and displays them
        accordingly. newString is formed from current state of the buffer.
        It checks this against the finalBuffer to see if they match. If they
        do, no new valid characters have been added to the buffer. If they
        don't match, we need to update the finalBuffer and rect objects that
        print the Textbox on screen with the new character.
        """
        # Pull the buffer and make it into a string.
        newString = "".join(self.buffer)
        if newString != self.finalBuffer:
            # We need update the finalbuffer contents and render it on screen.
            self.finalBuffer = newString
            self.textSurf = self.boxFont.render(self.finalBuffer, True, self.fontColor)
            self.textRect = self.textSurf.get_rect(x = self.rect.x + self.OUTLINEWIDTH, centery = self.rect.centery)

            # The next stanza handles the offset if the new width of the
            # textbox is bigger than the space allotted for it.
            if self.textRect.width > self.rect.width - self.DEFAULTOFFSET:
                # The offset is sufficient that all characters in self.buffer
                # cannot be rendeered inside the textbox. An offset is needed.
                # pygame.Rect needs (left, top, width, height) as arguments.
                # Here, left = offset, top = 0, width = self.rect [the width
                # of the blank textbox], and height = the new textRect height.
                offset = self.textRect.width - (self.rect.width - self.DEFAULTOFFSET)
                self.screenRender = pygame.Rect(offset, 0, self.rect.width - self.DEFAULTOFFSET, self.textRect.height)
            else:
                # No offset is required yet.
                self.screenRender = self.textSurf.get_rect(topleft = (0,0))

        # Now, we need to check if it is time to cycle the blinking behavior.
        if pygame.time.get_ticks() - self.blinkTimer > self.BLINKSPEED:
            # We need to flip self.blink and reset self.blinkTimeer.
            # self.blink is a boolean. self.blinkTimer is a float based on
            # time in milliseconds.
            self.blink = not self.blink # Flips the value.
            self.blinkTimer = pygame.time.get_ticks() # Resets timer to now.

    def drawBox(self, displaySurf):
        """
        This method draws the textbox and its surfaces. It will include a
        warning surface if the one exists. Once the warning has been
        displayed, it will set it back to None again. outline_color is the
        actual color that will be rendered in the outline of the textbox.
        outline is the actual rectangle enclosing the textbox.
        """
        if self.active:
            outline_color = self.activeColor
        else:
            outline_color = self.outlineColor
        outline = self.rect.inflate(self.outlineWidth * 2, self.outlineWidth * 2)
        displaySurf.fill(outline_color, outline)
        displaySurf.fill(self.fillColor, self.rect)
        # If there are characters in self.buffer or self.finalBuffter,
        # self.textSurf will exist to render it.
        if self.textSurf:
            displaySurf.blit(self.textSurf, self.textRect, self.screenRender)
        # If there is self.warningSurf, we need to render it as well. After
        # blitting it, we can destroy those objects.
        if self.warningSurf:
            self.warningRect.center = (self.rect.centerx, self.rect.centery + self.DEFAULTBOXHEIGHT)
            displaySurf.blit(self.warningSurf, self.warningRect)
            self.warningSurf = None
            self.warningRect = None
            pygame.display.update()
        # Now, we need to blink the active textbox if it is active and it is
        # time to do so. self.blink = True means to blink it. self.active
        # indicates if this Textbox object is active. curse used to lay out
        # a rect object slightly off from the original one.
        if self.blink and self.active:
            curse = self.screenRender.copy()
            curse.topleft = self.textRect.topleft
            displaySurf.fill(self.fontColor, (curse.right + 1, curse.y, 2, curse.height))
