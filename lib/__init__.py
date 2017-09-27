from __future__ import print_function
import random
from CardShoe import CardShoe
from Player import Player
from Dealer import Dealer
from CasinoTable import CasinoTable

__doc__ = """
This is the library subpackage for Blackjack. The libraries include the following classes:

    CardShoe: takes 6 52-card standards decks and creates a random card shoe from them
    Player: objects tracking player's name, bank, hands (regular and split), bets, wins,
        losses, and ties in each round
    Dealer: special derived class from Player handling the Dealer's hands, bank, and wins,
        losses, and draws
    CasinoTable: covers dealing cards, player turns, dealer's turn, and wins/losses/ties,
        specific casino conditionals
    Casino: derived class from CasinoTable coming soon

This is written in Python 2.7.13 but will be ported to Python 3.6+ soon.
"""
