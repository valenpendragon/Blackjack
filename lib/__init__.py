from __future__ import print_function
import random
from BlackjackClasses import CardShoe, Player, Dealer, CasinoTable
from PygameTexboxClass import Textbox
__doc__ = """
This is the library subpackage for Blackjack. The libraries include the
following classes:

    CardShoe: takes 6 52-card standards decks and creates a random card shoe
        from them
    Player: objects tracking player's name, bank, hands (regular and split),
        bets, wins, losses, and ties in each round
    Dealer: special derived class from Player handling the Dealer's hands,
        bank, and wins, losses, and draws
    CasinoTable: covers dealing cards, player turns, dealer's turn, and
        wins/losses/ties, specific casino conditionals
    Textbox: uses pygame and the string module to create interactive textboxes
        that accept only specified characters (number for bets, text for
        names)

These libraries are written in Python 2.7.14 and pygame 1.9.2. Textbox was
written with help from Sean McKiernan (Mekire on GitHub).
"""
