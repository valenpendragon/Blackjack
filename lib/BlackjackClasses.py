from __future__ import print_function
import random, os, pygame, inflection
from pygame.locals import *

# from abc import ABCMeta, abstractmethod

class CardShoe(object):
    '''
    This class is used to simulate a six deck shoe.
        
    Class Order Attributes:
        suits: a tuple of the suits used in normal playing card decks
            S (spades), D (diamonds), H (hearts), and C (clubs). Tuple
            are used because these values are constants.
        ranks: a tuple of the ranks of playing cards in ascending order Ace 
            through King, represented by A, 1, 2, 3,...., 9, 10, J, Q, K.
            Tuples are used here for the same reason.

    Note: The "cards" themselves are tuples of (rank, suit). Six 52 card
        decks of them are created for the Shoe. The first one is a sequential
        order list. To increase the entropy of the randomizing process, a
        randomly chosen single card is removed from the sequential "Shoe"
        and inserted into the list shuffled_deck (see below). This process
        continues until all 312 cards have been removed from the sequential
        deck.
    
    Attributes
        shuffled_deck : a randomly shuffled shoe created from decks.
        length: the number of cards in the shoe after initialization
    
    Methods:
        __init__ : Initializes shuffled_deck to create a card shoe.
        __len__: returns the number of cards remaining in the shoe.
        __str__: returns a string listing the number of cards remaining
            in the shoe.
        __del__: returns a message the deck show has been removed as it 
            deletes the CardShoe object
        remove_top: removes the top card (index 0) from the shuffled deck
            and returns the tuple of the card (rank, suit)
        diagnostic_print: prints out the entire CardShoe object, including
            all class order attributes, and current attributes
        
    '''
    suits = ('S', 'D', 'H', 'C')
    ranks = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
    
    def __init__(self):
        """
        __init__ creates the CardShoe object in the following manner:
        A sequentially generate list of cards [tuples of the form (rank,
        suit)] are generated for a list called decks. Decks is a local
        variable. To increase the entropy in the randomization process,
        the "cards" are randomly chosen one at a time, instead of randomizing
        the entire Shoe at once. There is no other return value.

        To help prevent cheating, __init__ takes no arguments.
        """

        # The following nested for loops generate 6 52 "card decks" of tuples
        # (rank, suit). Each 52 card set is in sequential order by the tuples
        # suits and ranks, starting with (A, S) and ending with (K, C).
        decks = []
        for i in xrange(0, 6):
            for s in CardShoe.suits:
                for r in CardShoe.ranks:
                    decks.append((r,s))
        
        # To create a shuffled card shoe, we need to take a random card from
        # decks and move it into the shoe. We keep doing that until the deck
        # is fully randomized. It could have been done with a direct call
        # random.shuffle(decks), but this process adds more entropy to the
        # system without using much memory or CPU.
        self.shuffled_deck = []
        while len(decks) > 0:
            # card is another local variable. It is a tuple pulled using a
            # random index of the remaining elements in decks.
            # card_index is that random index created using random.randint().
            card_index = random.randint(0,len(decks) - 1)
            self.shuffled_deck.append(decks[card_index])
            del decks[card_index]
        # Now, CardShoe.shuffled_deck contains a shuffled six deck shoe.
        # This length is the number of cards in the initialized deck. It
        # should be 312 cards (r, s).
        self.length = len(self.shuffled_deck)
    
    def __len__(self):
        """
        This method returns the number of cards left in the shoe. This is
        used by other Classes to offer players the option to reshuffle earlier
        in the game. It is also used by CasinoTable classes to determine when
        the Shoe should be automatically reshuffled between rounds.
        """
        return len(self.shuffled_deck)
    
    def __str__(self):
        """
        # This method returns a string indicating that the deck has been
        # initialized and the current number of "cards" remaining in it.
        """
        return "Deck: A shuffled shoe containing "+ str(len(self.shuffled_deck)) + " cards."
    
    def __del__(self):
        """
        This method removes a deck shoe from the game. It, then, returns a
        string indicating that the deck shoe has been deleted.
        """
        return "The current deck shoe has been removed from the game."
    
    def remove_top(self):
        '''
        This method removes the top card from the deck and returns the tuple
        (rank, suit) of the card. The top card has index 0. It does not accept
        any arguments.
        '''
        top_card = self.shuffled_deck[0]
        self.shuffled_deck.pop(0)
        return top_card

    def diagnostic_print(self):
        '''
        This method allows the programmer to print out all of the attributes,
        including class order attributes, for the defined object to help debug
        code. It is not normally used with running program.
        '''
        print("Class Order Attributes:")
        print("Ranks: ", self.ranks)
        print("Suits: ", self.suits)
        print("Number of cards in Shoe: ", self.length)
        print("Shuffled_Shoe: ", self.shuffled_deck)
        return


class Player(object):
    """
    This class creates Hands for a Blackjack player.
    
    Terms related to game play:
        players_turn: The part of a round of play in which players are playing
            their hands in rotation around the "table"
        dealer_turn: The part of the round of play in which the dealer plays
            its hand. Dealer is a computer player.
        round: Rounds have the following sequence of events:
            Opening Bets and Deals
                1) initial bets taken
                2) hands are dealt to Dealer and Players
                3) insurance bets are taken if dealer has a potential blackjack
                4) initial player Blackjacks are paid out
            Player Turn Begins
            Going around the table for each of step below:
                5) remaining players decide on additiaonl bets and splits
                6) players decide on card draws, removing hands that bust
            Dealer Turn Begins
                7) Dealer reveals hold card. Blackjack beats all remaining
                    players.
            If any players remain after Blackjacks and busts, the game
            continues:
                8) Dealer stands if any of the following are true:
                    a) Dealer has a hard 17 or greater
                    b) Dealer has a hard score less than 17, but has a soft
                        score (due to an Ace) of 17 or more that beats at
                        least one player's hand
                    c) Dealer busts at any point
                9) Dealer must take a card while any of the following
                    conditions exist:
                    a) Dealer has a soft score under 17
                    b) Dealer has a hard score under 17 with a soft score 17 or
                        greater, but the soft score beats no other player's
                        hand
                10) Remaining players win if Dealer busts or stands at a score
                    below their score
                11) Ties result in returned bets
                12) Dealer loses any bets if its score is lower than a player's
                    score
                        
        game: A series of rounds of play until either all players run out of
            money or decide to stop playing and "cash out".
    
    Class Order Attributes:
        values: dictionary of the scoring for each rank of blackjack card
            (it was not in use in CardShoe class). It is a COA because it is
            needed for every player object.
        
    Attributes:
        name: stores the player's name
        hand: tracks the card tuples (rank, suit) of the cards in the player's
            regular hand
        soft_hand_score: integer value of the current "soft" score of the
            player's hand
        hard_hand_score: integer value of the "hard" score of the player's
            hand
        split_flag: boolean set to True if the player splits, False if not.
        split_hand: tracks a second hand created by a split
        soft_split_score: integer value of the current "soft" score of the
            player's split hand, if it exists
        hard_split_score: integer value of the current "hard" score of the
            player's split hand, if it exists
        bank: integer number of dollars the player currently has in chips
        bet: current amount bet on the outcome of their hand vs dealer's hand
        split_bet: tracks any bets applied to a split hand
        insurance: tracks the amount of any side bets taken on the dealer
            getting blackjack (requires Dealer shows an Ace or 10 value card
            for its visible card)
    
    Methods:
        __init__: Creates the player object, initializing all of the
            attributes. The bank has a default value of 10,000 dollars.
        __str__: This method originally printed out the basic data on a Player's
            bets, hands, and scores. As of the Pygame coversion, it now returns
            a dict object containing the following:
                'name'            : player's name
                'bank'            : player's bank
                'hand'            : player's regular hand or None
                'split hand'      : player's split hand or None
                'soft score'      : soft score for player's hand or None
                'hard score'      : hard score for player's hand or None
                'soft score split hand' : soft score for split hand or None
                'hard score split hand' : hard score for split hand or None
                'regular bet'     : bet amount on regular hand or None
                'split hand bet'  : bet amount on split hand or None
                'insurance bet'   : bet amount on dealer blackjack or None
        __del__: removes the player object and returns a string indicating that
        __len__: prints out the len of the player's regular hand (This is
            used to determine player blackjack and splits)
        print_split: This method originally printed out player data and split
            hand data and bets. It now returns the same dict object as the
            __str__ method.
        score_hand: takes a hand and returns the soft and hard scores for
            the hand as a tuple (soft, hard)
        add_card_to_hand: takes a card as an argument, adds it to the hand,
            calls score_hand to get the new hard and soft scores, and returns
            'blackjack', 'bust', or 'playable'
        add_card_to_split: takes a card as an argument, adds it to the hand,
            calls score_hand to get the new hard and soft scores, and returns
            'bust' or 'playable'
        blackjack: takes the player's regular bet, mulitplies it by the
            Blackjack multiplier (supplied via argument) and adds it to their
            bank
        win: adds the player's bet to their bank
        split_win: add the player's split bet to the bank
        reg_loss: subtracts the player's bet from the bank. Returns False
            if the player's bank is now empty.
        split_loss: subtracts the player's split bet from the bank. Returns
            False if the player's bank is now empty, ending their game.
        tie: clears self.bet without deduction from the bank. This is needed
            for Dealer methods.
        split_tie: clears the bet on the split hand without deduction from
            the bank. This is needed for Dealer methods.
        ins: tracks a side bet taken on the dealer getting blackjack. It
            takes a boolean for the Dealer's blackjack. It returns True for
            a positive bank, False if the Player's bank is zero or negative.
        split_pair: moves one card over to the split_hand, prompts for a
            initial split_bet, and sets the split_flag to True. Adjusts the
            scores accordingly.
        split_check: checks for a pair in the initial deal. Returns True if
            so, False otherwise.
        end_round: resets all hands to empty, the split_flag to False, and all
            bets to zero (including insurance). This method is used to clean
            up after the Dealer's turn ends the round.
        update_bet: This method requires an integer for the new bet amount.
            It makes certain the player has the money in their bank to cover
            the new amount of their regular bet and all other bets. If so,
            it returns 'success'. If not, it returns an error code.
            The argument is the amount to increase the bet.
        update_split_bet: This method performs the same operation as
            update_bet, only on the split hand bets.
        update_ins: This method requires an integer amount of the insurance
            bet to be made. It verifies that the player has enough money in
            their bank to cover all of their bets, including the insurance
            bet. It returns 'success' if the player can cover the new bet,
            an error code if not.
        total_bets: This method calculates the total of all bets currently
            accepted for the player, including an insurance bet.
        double_down: This method takes a bet amount (integer) and split
            (boolean). Based on split (boolean), it calls either update_bet or
            update_split_bet with  whatever 'bet_amt' contains (with 0 as min
            and current bet as max arguments). It returns the string that the
            bet update methods return for each action.
        diagnostic_print: This method prints out all of the attributes and
            object stored in this object. Normally, this is used for code
            diagnostics only.
        
      
    """
    values = {'A' : 1,  '2' : 2,  '3' : 3, '4' : 4, '5' : 5, \
              '6' : 6,  '7' : 7,  '8' : 8, '9' : 9, '10' : 10, \
              'J' : 10, 'Q' : 10, 'K' : 10 }
    
    
    def __init__(self, name, bank=10000):
        '''
        This method intializes all of the following attributes:
            name: takes a string to initialize the player's name
            bank: takes a non-negative integer and stores it (even for
                Dealer). This attribute has a default of $10000 dollars
                if not specified in the call.
            hand: creates an empty list
            soft_hand_score: integer set to 0
            hard_hand_score: integer set to 0
            split_flag: boolean set to False
            split_hand: creates an empty list
            soft_split_score: integer set to 0
            hard_split_score: integer set to 0
            bet: integer set to 0
            split_bet: integer set to 0
            insurance: integer set to 0
            
        '''
        self.name = name
        self.bank = bank
        self.hand = []
        self.soft_hand_score = 0
        self.hard_hand_score = 0
        self.split_flag = False
        self.split_hand = []
        self.soft_split_score = 0
        self.hard_split_score = 0
        self.bet = 0
        self.split_bet = 0
        self.insurance = 0
        return
    
    def __str__(self):
        '''
        This method returns the full data on a player in dict data format.
        The layout of the data is:
            'name'            : player's name
            'bank'            : player's bank
            'hand'            : player's regular hand or None
            'split hand'      : player's split hand or None
            'soft score'      : soft score for player's hand or None
            'hard score'      : hard score for player's hand or None
            'soft score split hand' : soft score for split hand or None
            'hard score split hand' : hard score for split hand or None
            'regular bet'     : bet amount on regular hand or None
            'split hand bet'  : bet amount on split hand or None
            'insurance bet'   : bet amount on dealer blackjack or None
            
        "hands" are set to None if they do not exist, including split_hand.
        The split_flag is used to check for the latter. Bets and scores are
        set to None if they are zero.
        '''

        playerData = {}
        playerData['name'] = self.name
        playerData['bank'] = self.bank

        # Determine if a hand was dealt to the player or still exists.
        if len(self.hand) != 0:
            playerData['hand']        = self.hand
            playerData['soft score']  = self.soft_hand_score
            playerData['hard score']  = self.hard_hand_score
            playerData['regular bet'] = self.bet
        else:
            # The regular hand has not been dealt or has been removed already.
            playerData['hand']        = None
            playerData['soft score']  = None
            playerData['hard score']  = None
            playerData['regular bet'] = None

        # Determine if a split hand was dealt to the player or still exists.   
        if (self.split_flag == True) and (len(self.split_hand) != 0):
            playerData['split hand']            = self.split_hand
            playerData['soft score split hand'] = self.soft_split_score
            playerData['hard score split hand'] = self.hard_split_score
            playerData['split hand bet']        = self.split_bet
        else:
            # A split hand has not been dealt or has been removed already.
            playerData['split hand']            = None
            playerData['soft score split hand'] = None
            playerData['hard score split hand'] = None
            playerData['split hand bet']        = None

        # Check for an insurance bet.
        if self.insurance != 0:
            playerData['insurance bet'] = self.insurance
        else:
            playerData['insurance bet'] = None
        return playerData
    
    def __del__(self):
        '''
        This method removes a player from the game. After deleting the player,
        it returns a string indicating that the player object has been deleted.
        '''
        name = self.name
        return "{0} has been removed from the game.".format(name)
    
    def __len__(self):
        '''
        This method prints out the length of the player's regular hand. This
        is used to help determine a possible blackjack.
        '''
        return len(self.hand)
    
    def print_split(self):
        '''
        This method replicates __str___() method. It originally printed only
        the split hand data, but that need changed with the switch to a pygame
        interface.
        '''
        playerData = self.__str__()
        return playerData
    
    def total_bets(self):
        '''
        This method returns a total of all bets placed by the player. It
        accepts no arguments.
        '''
        return self.bet + self.split_bet + self.insurance
    
    def score_hand(self, card_hand):
        '''
        This method accepts a card hand and returns the hard and soft scores
        for the hand. This is in the form of a tuple (soft, hard).
        Normally, soft and hard scores are equal, but Aces have two possible
        scores. The hard score always treats Aces as 1 point card. That means
        that soft scores >= hard scores.
        Note: This method makes no attempt to determine if a hand is still
        playable. It only checks to see if Aces allow for more than one playable
        score. If so, it will try to find the highest playable score. Keep in
        mind that blackjacks have a soft score of 21 and a hard score of 11.
        '''
        # We need to track Aces and both scores. They start out equal.
        soft_score = hard_score = 0
        aces = 0
        for (rank, suit) in card_hand:
            card_score = Player.values[rank]
            # We increment both scores by the value in values, which treats
            # Aces as a 1 point card. If no aces are present, the scores will
            # remain equal.
            soft_score += card_score
            hard_score += card_score
            if rank == 'A':
                # Increment the number of aces.
                aces += 1
        
        # The hard_score is the minimum value that the hand can have, but it
        # may not be the only playable value. If there is at least one Ace, we
        # we have to determine if scoring one or more Aces as 11 will result in
        # a playable score. The only case we care about is a playable hard score
        # with at least one Ace.
        if hard_score < 21 and aces != 0:
            for i in xrange(1, aces + 1):
                # This for loop takes the soft score and adds 10 to it, tests
                # it to see if it is still playable. If so, it changes the soft
                # score to match it. It does this until all Aces are exhausted.
                # The largest playable score will be containted in soft_score
                # after it completes its run.
                test_score = soft_score + 10
                if test_score <= 21:
                    soft_score = test_score
        
        # Now, we return the tuple.
        return (soft_score, hard_score)
    
    def add_card_to_hand(self, card):
        '''
        This method accepts a card tuple (rank, suit) as argument. It places
        this card into the Player.hand list. It calls the internal method
        score_hand to rescore the hard and soft scores of the hand. The hard
        score for a hand will be equal to the soft score if there are no aces
        in the hand. The soft_score can be greater than the hard score if
        scoring any ace in the hand as an 11 would result in a playable hand.
        In fact, blackjack (a natural 21) has a hard score of 11, while the
        soft score is 21 with the first two cards that were dealt.
        INPUT: card, a tuple of (rank, suit)
        OUTPUT: This function returns the following:
            'blackjack'  = the soft score is 21, the hard score is 11, and the
                           len(hand) is 2 (meaning the starting deal was a
                           blackjack).
            'bust'       = the hard_score is greater than 21
            'playable'   = at least one score is less than or equal to 21.
                           If one is 21, the hand is "longer" than 2 cards,
                           making it ineligible for blackjack.
        '''
        self.hand.append(card)
        (self.soft_hand_score, self.hard_hand_score) = self.score_hand(self.hand)
        if self.hard_hand_score > 21:
            return 'bust'
        elif (self.hard_hand_score == 11) and \
             (self.soft_hand_score == 21) and \
             (len(self) == 2):
            return 'blackjack'
        else:
            return 'playable'
    
    def add_card_to_split(self, card):
        '''
        This method accepts a card tuple (rank, suit) as argument. It places
        this card into the Player.split_hand list. It calls the internal
        method score_hand to rescore the hard and soft scores of the split
        hand. The hard score for a hand will be equal to the soft score if
        there are no aces in the hand. The soft_score can be greater than the
        hard score if scoring any ace in the hand as an 11 would result in
        a playable hand. This hand cannot have a blackjack result because it
        it created from the second card dealt.
        INPUT: card, a tuple of (rank, suit)
        OUTPUT: This function returns the following:
            'bust'       = the hard_score is greater than 21
            'playable'   = at least one score is less than or equal to 21
        '''
        self.split_hand.append(card)
        (self.soft_split_score, self.hard_split_score) = self.score_hand(self.split_hand)
        if self.hard_split_score > 21:
            return 'bust'
        else:
            return 'playable'
        
    def blackjack(self, multiplier):
        '''
        This method handles the player's winnings for a blackjack (natural 21
        on the first two cards dealt). Casinos always have a better payout
        ratio for a player winning a blackjack.
        Note: This is an automatic player win, regardless of whether or not
        Dealer has a blackjack as well.
        
        This method erases the original bet and clears the hand since this
        part of the round takes place immediately after the second card was
        dealt and before the Player Turn begins.
        
        This method does not return a value. The multiplier needs to be a
        decimal or an integer, not a fraction.
        
        Nothing is done to the split result because no split can occur with
        a natural 21. (Splits are offered when a pair is dealt to a player.)
        '''
        winnings = int(multiplier * self.bet)
        self.bank += winnings
        self.hand = []
        self.soft_hand_score = self.hard_hand_score = 0
        self.bet = 0
        return
    
    def win(self):
        '''
        This method handles the player's winnings after a win with their
        regular hand. The split_hand has a separate method for this purpose.
        
        This method does not accept arguments nor return values.
        '''
        # There is no multiplier for a regular win.
        self.bank += self.bet
        return
    
    def split_win(self):
        '''
        This method handles the player's winnings after a win with their
        split hand. The regular hand has a separate method for this purpose.
        
        This method does not accept arguments nor return values.
        '''
        # There is no multiplier for a win with a split hand.
        self.bank += self.split_bet
        return
    
    def reg_loss(self):
        '''
        This method deducts player's losses from bets on their regular hand,
        either to a bust or a lower hand score during the round than the
        dealer.
        
        This method takes no arguments. It returns True while the players has
        a positive balance in the bank. A zero or negative balance returns
        False.
        
        Note: This method is predicated on the idea that other methods or
        functions have made certain that the player had enough in their bank
        to cover any bets made.
        '''
        self.bank -= self.bet
        self.hand = []
        if self.bank <= 0:
            return False
        else:
            return True
       
    def split_loss(self):
        '''
        This method deducts the player's losses on the split hand, either
        to a bust or a lower score during the round than the dealer.
        
        This method takes no arguments. It returns True while the players
        has a positive balance in the bank. A zero or negative balance
        returns False.
        
        Note: This method is predicated on the idea that other methods or
        functions have made certain that the player had enough in their
        bank to cover any bets made.
        '''
        self.bank -= self.split_bet
        self.split_hand = []
        if self.bank <= 0:
            return False
        else:
            return True
    
    def tie(self):
        '''
        This method clears the regular bet if the hand ties with the Dealer.
        Ties do not normally result in casino wins. This is due to the
        realization by gaming commissions and club owners that coming away
        richer than you started at Blackjack tables is hard enough without
        the Dealer winning ties.
        
        This method accepts no arguments and returns no values. The reason
        for the latter is that there is no deduction from the bank, nor gain
        in a tie.
        '''
        self.bet = 0
        return
    
    def split_tie(self):
        '''
        This method clears the split bet if the split hand ties with the
        Dealer. Ties do not normally result in casino wins. This is due to the
        realization by gaming commissions and club owners that coming away
        richer than you started at Blackjack tables is hard enough without
        the Dealer winning ties.
        
        This method accepts no arguments and returns no values. The reason
        for the latter is that there is no deduction from the bank, nor gain
        in a tie.
        '''
        self.split_bet = 0
        return
    
    def ins(self, dealer_blackjack):
        '''
        This method handles bets taken on the Dealer getting a blackjack.
        This bet only happens when the Dealer's face up card is an Ace, 10,
        or face card. Other methods or functions handle creating this bet
        when the conditions for it are met.
        
        This method takes a boolean indicating if the Dealer has a blackjack.
        If True, the player wins their insurance bet. If False, the player
        lost the insurance bet.
        
        This method returns a boolean. True indicates that the player still
        has money in the bank. False means they have zero or a negative
        balance.
        
        Note: This method does not care if the insurance bet is zero. In that
        case, it has no effect on their bank balance.
        '''
        if dealer_blackjack == True:
            # The Dealer got blackjack. The player who has a non-zero
            # insurance bet wins the bet. Otherwise, self.insurance = 0.
            self.bank += self.insurance
        else:
            # The Dealer did not get blackjack. The insurance bet is
            # deducted from the player's bank.
            self.bank -= self.insurance

        # In case the bet was deducted from the bank, we need to check it.
        if self.bank <= 0:
            return False
        else:
            return True
    
    def end_round(self):
        '''
        This method resets all data, except Player.name, and Player.bank. This method takes no
        arguments and returns no values. It is used at the end of a round, after the Dealer's
        turn.
        '''
        self.hand = []
        self.soft_hand_score = 0
        self.hard_hand_score = 0
        self.split_flag = False
        self.split_hand = []
        self.soft_split_score = 0
        self.hard_split_score = 0
        self.bet = 0
        self.split_bet = 0
        self.insurance = 0
        return
    
    def update_bet(self, new_increase, min_bet=1, max_bet=100):
        '''
        This method increases the regular bet by the amount of the increase.
        It will add up all the other bets to make sure that player has enough
        money in the bank to cover it.
        INPUT: integer new_increase (or a float that will be truncated)
        OPTIONAL: min_bet and max_bet are not required (because of defaults),
            but a casino could override the value by including it.
        OUTPUT: string with the following meanings
            'success'   = the bet could be increased
            'bust'      = the bet exceeds the money in the bank
            'size'      = the bet is not allowed because it exceeds double the
                        original bet
            'min'       = the bet is not enough to meet the casino minimums
            'max'       = the bet exceeds the max allowed initial bet
            'TypeError' = at least one 'numerical' argument supplied was not a
                        number
            'Unknown'   = an unknown error occurred
        
        Note: A zero max_bet means that there is no maximum initial bet amount.
        '''
        # The first step is to convert a possible floating point number into an
        # integer.
        try:
            amt_to_increase = int(new_increase)
        except TypeError:
            return 'TypeError'
        except:
            return 'Unknown'
        else:
            # If it could be converted, the sign needs to be stripped off the
            # value.
            amt_to_increase = abs(amt_to_increase)
        
        # Next, the new amount needs to be checked against min and max bets.
        # Note: min and max bets only apply to the bets laid before the cards
        # are dealt. So, Player.bet = 0 then.
        if self.bet == 0:
            if amt_to_increase < min_bet:
                return 'min'
            # A max_bet of zero means there is no maximum (besides the implicit
            # all in).
            if (max_bet != 0) and (amt_to_increase > max_bet):
                return 'max'
        # A non-zero bet automatically is subject to the double down rule. A
        # player may not exceed twice their original bet on a "great" hand.
        elif self.bet < amt_to_increase:
            return 'size'
                
        # Now, the total amount of all bets needs be checked against the bank
        # balance. total_bets() = self.bet + self.split_bet + self.insurance
        if (self.total_bets() + amt_to_increase) > self.bank:
            return 'bust'
        self.bet += amt_to_increase
        return 'success'
    
    def update_split_bet(self, new_increase, min_bet=1, max_bet=100):
        '''
        This method increases the split bet by the amount of the increase. It
        will add up all the other bets to make sure that player has enough
        money in the bank to cover it.
        INPUT: integer new_increase (or a float that will be truncated)
        OPTIONAL: min_bet and max_bet are not required (because of defaults),
            but a casino could override the value by including it.
        OUTPUT: string with the following meanings
            'success'   = the bet could be increased
            'bust'      = the bet exceeds the money in the bank
            'size'      = the bet is not allowed because it exceeds double the
                        original bet
            'min'       = the bet is not enough to meet the casino minimums
            'max'       = the bet exceeds the max allowed initial bet
            'TypeError' = at least one 'numerical' argument supplied was not a
                        number
            'Unknown'   = an unknown error occurred
        
        Note: A zero max_bet means that there is no maximum initial bet amount.
        '''
        # The first step is to convert a possible floating point number into an integer.
        try:
            amt_to_increase = int(new_increase)
        except TypeError:
            return 'TypeError'
        except:
            return 'Unknown'
        else:
            # If it could be converted, the sign needs to be stripped off the value.
            amt_to_increase = abs(amt_to_increase)
        
        # Next, the new amount needs to be checked to see against min and max bets.
        # Note, min and max bets only apply to the bets laid before the cards are 
        # dealt. So, Player.bet = 0 then.
        if self.split_bet == 0:
            if amt_to_increase < min_bet:
                return 'min'
            # A max_bet of zero means there is no maximum (besides the implicit all in).
            if (max_bet != 0) and (amt_to_increase > max_bet):
                return 'max'
        # A non-zero bet automatically is subject to the double down rule. A player
        # may not exceed twice their original bet on a "great" hand.
        elif self.split_bet < amt_to_increase:
            return 'size'
                
        # Now, the total amount of all bets needs be checked against the bank balance.
        # total_bets = self.bet + self.split_bet + self.insurance
        if (self.total_bets() + amt_to_increase) > self.bank:
            return 'bust'
        self.split_bet += amt_to_increase
        return 'success'
    
    def update_ins(self, ins_bet, min_bet=0, max_bet=200):
        '''
        This method accepts an integer insurance bet. This is a bet that the
        Dealer has a hidden blackjack. It can only be made if the Dealer's
        visible card is an Ace or a 10-score card. This is a way for the player
        to win money even when the Dealer has a blackjack. There is generally
        no mininum bet, but there is often a maxiumum allowed bet. There are no
        opportunities to raise this bet nor can the player place a second such
        bet if they split their hand.
        INPUT: integer ins_bet (or a float that will be truncated)
        OPTIONAL: min_bet and max_bet are not required (because of defaults),
            but a casino could override the value by including it.
        OUTPUT: string with the following meanings
            'success'   = the insurance bet was acceptable and applied
            'exists'    = the insurance bet has already been made
            'bust'      = the bet exceeds the money in the bank
            'min'       = the bet is not enough to meet the casino minimums
            'max'       = the bet exceeds the max allowed for an insurance bet
            'TypeError' = at least one 'numerical' argument supplied was not a
                        number
            'Unknown'   = an unknown error occurred
        '''
        # The first step is to convert a possible floating point number into an
        # integer.
        try:
            ins_amt = int(ins_bet)
        except TypeError:
            return 'TypeError'
        except:
            return 'Unknown'
        else:
            # If it could be converted, the sign needs to be stripped off the
            # value.
            ins_amt = abs(ins_amt)
        
        # Next, we need to check for an existing insurance bet. If it exists
        # already, no changes are permitted.
        if (self.insurance != 0):
            return 'exists'
        if (ins_amt < min_bet):
            return 'min'
        if (ins_amt > max_bet):
            return 'max'
        # Now, the total amount of all bets needs be checked against the bank
        # balance.
        if (self.total_bets() + ins_amt) > self.bank:
            return 'bust'
        self.insurance += ins_amt
        return 'success'
    
    def split_check(self):
        '''
        This method verifies that the player's initial deal supports a split.
        It returns True if the cards are a pair, False otherwise.
        '''
        if (self.hand[0][0] != self.hand[1][0]):
            return False
        else:
            return True
        
    def split_pair(self):
        '''
        This method moves the second card in the player's initial hand to the
        split_hand, sets the split_flag to True, and recalculates the hand
        scores.
        '''
        self.split_flag = True
        self.add_card_to_split(self.hand[1])
        self.hand.pop()
        (self.soft_hand_score, self.hard_hand_score) = self.score_hand(self.hand)
        (self.soft_split_score, self.hard_split_score) = self.score_hand(self.split_hand)
        return
    
    def double_down(self, bet_amt, split):
        '''
        Originally, this method actually asked the player if they wanted to
        double down, then recorded their bet amount. The bet was checked to
        see if it exceeded their ante bet at the beginning of the round or the
        initial bet on their split hand. With Pygame, this method tests takes
        a bet amount (integer) and a split flag (boolean) and determines if
        the bet is a valid amount using update_bet or update_split_bet
        methods. Return values are below.
        INPUT: bet_amt: integer, split: boolean
        OUTPUT: string with one of the following messages:
            'success'   = the bet was a valid amount and was applied
            'bust'      = the bet exceeds the money in the bank
            'size'      = the bet is not allowed because it exceeds double the
                        original bet
            'TypeError' = at least one 'numerical' argument supplied was not a
                        number
            'Unknown'   = an unknown error occurred
        Note: double_down will not return 'min' or 'max' because the table
        min and max do not apply to this bet. Only 'size' matters. Neither
        bets can be more than double the original bet.
        '''
        # First, we check the split boolean to see if this is the split hand.
        # Regular and split hands use different methods because their
        # attributes have to be handled differently.
        if split:
            # It is a split hand.
            bet_check = self.update_split_bet(bet_amt, 0, self.bet)
        else:
            # It is a regular hand.
            bet_check = self.update_bet(bet_amt, 0, self.bet)
        return bet_check
    
    def diagnostic_print(self):
        '''
        This method is used to print out all object attributes in a readable format. It is 
        used to help debug issues with game code, not for looking under the hood.
        '''
        print("Class Order Attributes:")
        print("Values Dictionary: ", Player.values)
        print("Player Attributes: ")
        print("Name: ", self.name)
        print("Hand: ", self.hand)
        print("Soft Score: ", self.soft_hand_score)
        print("Hard Score: ", self.hard_hand_score)
        print("Split Flag: ", self.split_flag)
        print("Split Hand: ", self.split_hand)
        print("Soft Score for Split Hand: ", self.soft_split_score)
        print("Hard Score for Split Hand: ", self.hard_split_score)
        print("Remaining Bank: ", self.bank)
        print("Bet on Hand: ", self.bet)
        print("Bet on Split Hand: ", self.split_bet)
        print("Insurance Bet: ", self.insurance)
        return


class Dealer(Player):
    """
    This is a derived class from base clase Player. The purpose of this class
    is to create a special type of player, called the Dealer. The dealer has
    no split hands, has rules about taking cards after reaching a hard score
    of 17, and places no actual bets.
    
    Class Order Attributes:
        name = 'Dealer'
        
    Inherited Class Order Attributes:
        values
        
    Attributes:
        hand: tracks the card tuples (rank, suit) of the cards in the Dealer's
            hand (a list)
        bank: tracks dealers bank (integer)
        soft_hand_score: integer value of the current "soft" score of the
            Dealer's hand
        hard_hand_score: integer value of the "hard" score of the player's
            hand
        visible_card: single tuple showing hand[1] once it is dealt
        visible_soft_score: integer soft score of the visible card
        visible_hard_score: integer hard score of the visible card (only
            differs on Aces)
        blackjack_flag: True if the dealer's visible card is an Ace or a 10
            value card, False otherwise
    
    Inherited Attributes (from Player class):
        hand, soft_hand_score, hard_hand_score
    
    Methods:
        __init__: initializes the attributes specific to dealer objects. Will 
            accept an integer to set dealer's starting bank to a value other
            than 100,000 default.
        __str__: This method originally printed out the name "Dealer" a "face
            down" card, a single revealed card for the Dealer, and the
            score(s) for that card. It was only used during player turns. As
            of the Pygame coversion, it now returns a dict object containing
            the following:
                'name'               : dealer's name (aka "Dealer")
                'bank'               : dealer's bank
                'hand'               : dealer's hand or None (a list)
                'visible card'       : a tuple of the hand[1]
                'visible soft score  : soft score of the visible card
                'visible hard score  : hard score of the visible card
                'soft score'         : soft score for dealers's hand or None
                'hard score'         : hard score for dealers's hand or None
                'dealer turn'        : set to None
        dealer_print: This method originally printed out the dealer's fully
            revealed hand and changing hand scores during the Dealer's turn.
            Now, this method calls __str__, then changes the following item:
                'dealer turn'        : set to True
        add_card_to_hand: adds a card to the dealer's hand, updates 
            visible_card (a hand) and its scores on second deal, updates
            the actual hand scores,  sets the blackjack_flag for the right
            ranks of visible_card, and returns 'playable', 'blackjack', 
            or 'bust' when finished. Like the Player version, it uses the
            inherited score_hand() method for scoring visible and actual
            hands.
        end_round: resets hand data and flags at the end of a round
        dealer_lost: The argument is the total of all bets that the dealer lost 
            this round, including insurance and player blackjacks. If the
            losses break the bank, it returns False. Otherwise, it returns
            True.
        dealer_wins: The argument is the total of all bets the dealer won
            this round, including insurance bets. It is added to the dealer's
            bank.
        diagnostic_print: This method prints out all attributes of the Dealer
            object, including class order attributes. It is intended to help
            debug coding errors.
        
    Inherited Methods (from Player class):
        __len__, __del__, score_hand

    """
    def __init__(self, name='Dealer', bank=100000):
        '''
        This method creates the following attributes for Dealers:
            hand: creates an empty list
            bank: set to 100,000 (by default, but can be changed via an
                optional argument)
            soft_hand_score: set to 0
            hard_hand_score: set to 0
            visible_card: empty list
            visible_soft_score: set to 0
            visible_hard_scort: set to 0
            blackjack_flag: set to False
        
        INPUT: bank, integer, defaults to 100,000 (dealer's starting bank)
               name, string, defaults to 'Dealer' (dealer's name)
        '''
        self.name = name
        self.hand = []
        self.bank = bank
        self.soft_hand_score = self.hard_hand_score = 0
        self.visible_card = []
        self.visible_soft_score = self.visible_hard_score = 0
        self.blackjack_flag = False
        return        
    
    def __str__(self):
        '''
        This method originally printed out the Dealer's name ("Dealer"), a
        face down card, a visible card (self.visible_card), and the score(s)
        for the visible card (self.visible_soft_score and
        self.visible_hard_score). This method was used during the player
        turns.

        The dealer_print method actually printed out the dealer's full hand
        and the scores for that hand as the Dealer player its hand during the
        Dealer's turn.

        In the Pygame conversion, it returns the following dict object:
                'name'               : dealer's name (aka "Dealer")
                'bank'               : dealer's bank
                'hand'               : dealer's hand or None (a list)
                'soft score'         : soft score for dealer's hand or None
                'hard score'         : hard score for dealer's hand or None
                'visible card'       : a tuple of the hand[1] or None
                'visible soft score  : soft score of the visible card
                'visible hard score  : hard score of the visible card
                'dealer turn'        : set to None

        The method dealer_print also calls this method to create the dict
        object, but then changes 'dealer turn' before returning the object.        

        'hand' and 'visible card' are set to None if the Dealer has an empty
        hand, as are the scores. (Note, Dealers have no split_hand, nor any
        bets.)
        '''

        dealerData = {}
        dealerData['name'] = self.name
        dealerData['bank'] = self.bank

        # Determine if a hand was dealt to the Dealer or still exists.
        if len(self.hand) != 0:
            dealerData['hand']        = self.hand
            dealerData['soft score']  = self.soft_hand_score
            dealerData['hard score']  = self.hard_hand_score
            dealerData['visible card']       = self.visible_card
            dealerData['visible soft score'] = self.visible_soft_score
            dealerData['visible hard score'] = self.visible_hard_score
        else:
            # The Dealer has not been dealt a hand or it has already been
            # removed by another method.
            dealerData['hand']        = None
            dealerData['soft score']  = None
            dealerData['hard score']  = None
            dealerData['visible card']       = None
            dealerData['visible soft score'] = None
            dealerData['visible hard score'] = None

        # 'dealer turn' is always None from this method.
        dealerData['dealer turn'] = None
        return dealerData

    def dealer_print(self):
        '''
        This method originally printed out full data on the Dealer, its hand,
        and the scores on that hand during the Dealer's turn.

        With the Pygame conversion, this method calls self.__str__() to
        create the dealerData dict object (see above), then it changes
        the following value:
            'dealer turn'   : set to True
        '''
        dealerData = self.__str__()
        dealerData['dealer turn'] = True
        return dealerData
     
    def add_card_to_hand(self, card):
        '''
        Functionality carried over from Player.add_card_to_hand():
        
        This method accepts a card tuple (rank, suit) as argument. It places
        this card into the Dealer.hand list. It calls the internal method
        score_hand() to rescore the hard and soft scores of the hand with the
        new card. The hard score for a hand will be equal to the soft score
        if there are no aces in the hand. The soft_score can be greater than
        the hard score if scoring any ace in the hand as an 11 would result
        in a playable hand. Note: Blackjack (a natural 21) has a hard score
        of 11 and a soft score of 21.
        
        New functionality specific to Dealer class:
        
        On second deal, assign the second card to attribute visible_card and
        run score_hand on this card to get soft and hard visible scores.
        This method sets the blackjack_flag to True if the visible_card is an
        Ace, a face card, or a 10. This condition allows players to place an
        'insurance bet' on whether or not the Dealer might have Blackjack
        based on the visible card.
        
        INPUT: card, a tuple of (rank, suit)
        OUTPUT: This function returns the following:
            'blackjack'  = the soft score is 21, the hard score is 11, and the
                           len(hand) is 2 (meaning the starting deal was a
                           blackjack)
            'bust'       = the hard_score is greater than 21
            'playable'   = at least one score is less than or equal to 21.
                           If either score is 21, the hand must be contain
                           more than 2 cards since it is not a blackjack.

        With the Pygame conversion, no functionality changes were required.
        '''
        self.hand.append(card)
        (self.soft_hand_score, self.hard_hand_score) = self.score_hand(self.hand)
        # If this is the second card dealt to the Dealer, add it to the
        # visible card and score it.
        if len(self.hand) == 2:
            self.visible_card.append(card)
            (self.visible_soft_score, self.visible_hard_score) = self.score_hand(self.visible_card)
            # For a visible Ace, face card, or 10, the blackjack flag must
            # to be set to True so that insurance bets can be placed on it.
            # self.values is a dict constant with the values of all of the
            # card ranks in it. Aces are listed as a score of 1 there.
            (rank, suit) = card
            if (Dealer.values[rank] == 1) or (Dealer.values[rank] == 10):
                self.blackjack_flag = True
        if self.hard_hand_score > 21:
            return 'bust'
        elif (self.hard_hand_score == 11) and (self.soft_hand_score == 21) and (len(self) == 2):
            return 'blackjack'
        else:
            return 'playable'
        
    def end_round(self):
        '''
        This method resets all data, except Dealer.name, and Dealer.bank. This
        method takes no arguments and returns no values. It servers the same
        purpose as Player.end_round(), ensuring all flags, hands, and scores
        are reset between rounds.
        '''
        self.hand = []
        self.soft_hand_score = 0
        self.hard_hand_score = 0
        self.blackjack_flag = False
        self.visible_card = []
        self.visible_soft_score = 0
        self.visible_hard_score = 0
        return

    def dealer_lost(self, remaining_bets):
        '''
        This method requires an integer of the total of all player winnings
        this round. The method deducts this total bet from the dealer's bank.
        If the losses break the bank, it returns False. Otherwise, it returns
        True.

        With Pygame conversion, all print statements have been removed.
        '''
        losses = remaining_bets
        self.bank -= losses
        if self.bank <= 0:
            return False
        else:
            return True
    
    def dealer_won(self, player_bets):
        '''
        This method accepts an integer of the total of all player losses for
        this round. This method adds the wins to the dealer's bank. There is
        no return value.
        '''
        wins = player_bets
        self.bank += wins
        return
    
    def diagnostic_print(self):
        '''
        This method prints out all of the Dealer object attributes to help
        debug code. It is not intended for use outside of debugging programs.
        '''
        print("Class Order Attribute: ")
        print("Name: ", Dealer.name)
        print("Values Dictionary: ", Dealer.values)
        print("Dealer Object Attributes:")
        print("Dealer's Hand: ", self.hand)
        print("Soft Score: ", self.soft_hand_score)
        print("Hard Score: ", self.hard_hand_score)
        print("Visible Card: ", self.visible_card)
        print("Visible Soft Score: ", self.visible_soft_score)
        print("Visible Hard Score: ", self.visible_hard_score)
        print("Blackjack Flag: ", self.blackjack_flag)
        print("Dealer's Remaining Bank: ", self.bank)
        return


class CasinoTable(object):
    """
    This class simulates an actual casino table.
    
    Class Order Attributes:
        None currently
    
    Attributes:
        blackjack_multiplier: tuple storing ('ratio', float multiplier)
            ratio is a string that prints out a ratio, like 3:2, or 6:5
                which represents the payout ratio for a player blackjack
            multiplier is a floating point two decimal approximation of the
                ratio used to calculate the actual winnings
            This tuple is used to store and manage the table mulitiplier
        table_size: integer indicating the max number of players (other than
            dealer) for this table object (3 or 5, normally)
        tableSeats: ordinal dictionary for seat number to ordinal (to reduce
            CPU overhead calculating it all the time)
        deck: a CardShoe object that can be recreated via replace_cardshoe()
            method
        tableDealer: a Dealer object, initialized by a name and starting
            bank amount
        dealerLosses: helps track losses during a round
        players: a dict object of the form {'seat ordinal': playerObj},
            where seat ordinal is literall 1st, 2nd, ... up to the table_size
            and playerObject is the player object created from a name and bank
    
    Methods:
        __init__: Accepts several arguments that have defaults (playerNames,
            blackjack_multiplier, dealer's name, and dealer's bank. From this
            data, it creates a CasinoTable object: generates a tableDealer,
            a CardShoe (312 card random deck), calculates table_size, generates
            playerObjects for all human players, and builds tableSeats (an
            ordinal dictionary for seating).
        __str__: Returns the CasinoTable object. Assumes an upstream function
            or method will render the contents in Pygame.
        diagnostic_print: prints out all attributes to assist with code
            debugging (unchanged in Pygame version)
        rules: Returns the contents of the Blackjack-rules.txt file or an
            error message if the file is not found.
        deal_round: Deals a round of cards to each player, printing out the table when 
            completed. It checks for player blackjacks and pays them out. it also checks
            the dealer's blackjack_flag and offers insurance bets.
        initial_bets: Before any cards are dealt, this method ask for initial bets for each
            player for the round. It uses Player.update_bet for error checking and has
            defaults for min_bet and max_bet which a derived class for a specific casino
            can override.
        pairs_check: Runs through the players looking for pairs by calling Player.split_check.
            It offers splits and additional cards to those players who wish to split their 
            hands. It will take a split_bet as well, using Player.update_split_bet. 
            Like initial_bets, it has defaults for min_bet and max_bet that a derived class
            for a specifiic casino could override.
        double_down: This method offers players the option to increase their bets on their 
            hands if they have playable hands and did not have blackjack already. 
            Player.double_down(card_hand, flag) does the error checking on the amount. The 
            min is zero (taken as second thoughts), the max is the original bet, doubling it.
            The Player methods verify that hands still have two cards and the bet amounts are
            correct.
        hit_or_stand: this method asks the players if they want a hit or stand. it handles
            any busts that happen to players using the Player.reg_loss or Player.split_loss.
            Dropped the player deletion from this method, due to issues incrementing through
            the player list. This method returns codes 'none' or 'playable'.
        dealer_autowin: When the Dealer doesn't need to play its hand, this method performs
            the hold card reveal for the dealer.
        dealer_turn: this method plays the dealer's hand according to the rules:
            * dealer stands on a hard 17+
            * dealer stands on any 21 (blackjack or otherwise)
            * dealer must take a card on a soft 16 or less
            * dealer must stand on a hard 16 or less with a soft score that beats at least
                one players playable hand and is greater than 16.
            * dealer must take a card on a hard 16- with a soft score that does not beat any
                playable player hands.
            then, it determines all remaining wins and losses, using max_min_score and Player
            and Dealer class win/lose/tie methods to handle the changes to banks.
        max_min_score: this method pulls out the max and min hand scores after eliminating
            hands that busted or blackjacked. It returns a tuple (max,min).
        end_round: calls the end_round() methods in Dealer and Player classes to clear the
            bets, hands, and so on. It will also ask if the players want a new CardShoe and
            calls replace_cardshoe to get one. Dealer replace card shoes at 100 cards or less.
            If any players have a bank less than the min_bet for the table, they will be
            eliminated (including any who busted their bank).
        replace_cardshoe: deletes the CardShoe object called deck and initializes a new deck
        start_round: Asks if any players wish to quit before anteing up. Returns True if at
            least one player remains, False otherwise.
        
    """
    def __init__(self,
                 playerNames          = list({'name' : 'Fred', 'bank' : 50000}),
                 blackjack_multiplier = ('3:2', 1.50),
                 name = 'Sarah',
                 bank = 100000):
        '''
        This method requires several arguments from the calling program, even
        though it has clear defaults for each one. These inputs are:
        INPUT:
            playerNames: a list of dict objects of the form {'name': string,
                'bank': amount} for each player. This list will be accepted
                as the seating order of the players.
                Default: one player {'name' : 'Fred', 'bank' : 50000}
            blackjack_multiplier: a tuple ('string', float), the 'string' is a
                text ratio equivalent to the value of the float (the value used
                calculate player blackjack instant wins.
                Default: ('3:2', 1.50)
            name: string, the name of the dealer for this table
                Default: 'Sarah'
            bank: integer, the initial bank for this table's dealer
                Default: 100,000

        This method will generate the following attributes from its input:
            tableDealer: a Dealer class object
            players:     a dict object mapping 'seat ordinal' to playerObject
            table_size:  maximum number of players seatable at the table
            tableSeats:  dictionary of seat number to 'seat ordinal', using
                         dict comprehensions
            deck:        a CardShoe object (6 full 52 card decks shuffled
                         together)            
        '''
        # The table_size attribute can be built by using len on the
        # playerNames list.
        self.table_size    = len(playerNames)
        
        # The Dealer object is created by calling the class with the name and
        # bank amount provided in the arguments.
        self.tableDealer   = Dealer(name, bank)
        self.dealerLosses  = 0

        # The ordinale dictionary is created with a dictionary comprehension.
        self.tableSeats    = {x: str(x) + inflection.ordinal(x) for x in range(1, self.table_size + 1)}

        # Now, we need a for loop to create the player objects from the list
        # supplied in playerNames. Player.__init__() also has a default bank
        # in case one is not specified. We have to use the numbers to call the
        # ordinals we need. seat below is an integer, while ordinal it the
        # orginal number, e.g. 1st, 2nd, etc.
        self.players = {}
        for seat, ordinal in self.tableSeats.iteritems():
            self.players[ordinal] = Player(playerNames[seat]['name'], playerNames[seat]['bank'])            
        return
    
    def __str__(self):
        '''
        This method returns the CasinoTable object.
        '''
        return self
    
    def diagnostic_print(self):
        '''
        This method prints out every attribute for debugging purposes, calling
        the same named method in the classes for each object.
        '''
        print("Blackjack multiplier: ", self.blackjack_multiplier)
        print("Starting bank: ", self.starting_bank)
        print("Maximum Number of Human Players (table size): ", self.table_size)
        print("Actual Number of Players (table index): ", self.table_index)
        self.deck.diagnostic_print()
        for i in xrange(0, self.table_index):
            self.players[i].diagnostic_print()
        print("Completed diagnostic print of CasinoTable.")
        return
    
    def rules(self):
        '''
        Pulls a copy of the rules from a Blackjack-Rules.txt and returns the
        copy. If this file is not found, it returns an error message.
        '''
        if os.path.exists('./etc/BlackJack-Rules.txt'):
            f = open('./etc/BlackJack-Rules.txt', 'r')
            contents = f.read()
            f.close()
            return contents
        else:
            return 'File, BlackJack-Rules.txt, was not found. Check installation of Blackjack.'
        return

    def deal_round(self):
        '''
        This method deals a card to each player, including the dealer. At the end, it prints
        out the table for reference. The last card goes to the dealer. If any player gets
        a blackjack, it will pay out their bets. If the dealer has a potential for
        blackjack, it will offer the opportunity to make an insurance bet.
        
        There is no return value from this method.
        '''
        for i in xrange(1, self.table_index):
            print("Dealing a card to ", self.players[i].name)
            card = self.deck.remove_top()
            # These blocks were used to test the player blackjack payout or splitting hands.
            # if len(self.players[i]) == 0 and i == 2:
            #     card = ('A', 'S')
            # elif len(self.players[i]) == 1 and i == 2:
            #     card = ('10', 'D')
            # if len(self.players[i]) == 1 and i == 1:
            #    card = self.players[i].hand[0]
            result = self.players[i].add_card_to_hand(card)
            if result == 'blackjack':
                print("Congratulations Player {0}, you have a Blackjack!!!".format(self.players[i].name))
                winnings = int(self.players[i].bet * self.blackjack_multiplier[1])
                print("You have won $", winnings)
                self.players[i].blackjack(self.blackjack_multiplier[1])
                self.players[0].dealer_lost(winnings)
        print("Dealing a card to ", self.players[0].name)
        card = self.deck.remove_top()
        # Used to test blackjack_flag
        # card = ('10', 'H')
        self.players[0].add_card_to_hand(card)
        if self.players[0].blackjack_flag == True:
            print(self)
            rank, suit = card
            print("Dealer received a {0}-{1}".format(rank, suit))
            print("Players wishing to place an insurance bet for a Dealer Blackjack may do so now.")
            for i in xrange(1, self.table_index):
                answer = raw_input("{0}, would you like to make an insurance bet? (y/n)".format(self.players[i].name))
                if answer[0].lower() == 'y':
                    while True:
                        try:
                            bet_amt = raw_input("Indicate an amount up the table max:")
                        except:
                            print("That was an invalid result.")
                            continue
                        else:
                            bet_result = self.players[i].update_ins(bet_amt)
                            if bet_result != 'success':
                                continue
                            else:
                                print("Bet has been recorded. Good luck.")
                                break
        print(self)
        return
    
    def initial_bets(self, min_bet = 10, max_bet = 200):
        '''
        The method calls for the initial bets from each player before dealing the first two
        card to each player as the round starts.
        
        INPUT: integer min_bet and max_bet. These arguments have defaults in case the
            method call does not supply them.
            
        This method returns no values.
        '''
        print("Please place your initial bet. This will serve as a maximum raise amount after")
        print("the cards have been dealt.")
        for i in xrange(1, self.table_index):
            # The CasinoTable.end_round() method checks to see if any player's bank busted
            # or if they have insufficient funds to meet the table minimum. They should be
            # eliminated already.
            while True:
                print("The table minimum is ${0} and maximum is ${1}.".format(min_bet, max_bet))
                bet = raw_input("Player {0}, you have {1} remaining. What would you like to bet? ".format(self.players[i].name, self.players[i].bank))
                # Call the update_bet method for the player in question. It has all kinds of
                # error trapping functionality.
                result = self.players[i].update_bet(bet, min_bet, max_bet)
                if result == 'success':
                    break
                else:
                    print("Please try again.")
                    continue
        print("All starting bets are in.")
        return
    
    def pairs_check(self, min_bet = 10, max_bet = 200):
        '''
        This method runs a check of all players with playable hands to see if anyone has a pair. It
        calls Player.split_check() to verify it. If a player does have a pair, it offers to split the hand.
        If the player agrees, it uses Player.split_pair to create the split_hand and set the split_flag.
        It then ask for a bet on the new hand, then deals a second card to each hand. It skips any player
        with a blank hand (because a blank hand indicates a blackjack).
        
        This method also needs arguments for min_bet and max_bet.
        '''
        for i in xrange(1, self.table_index):
            # This conditional covers the  possibility of a player blackjack. Blackjack methods
            # clear up the player's hand as a signal to other methods that nothing needs to be
            # done with that player.
            if len(self.players[i]) != 0:
                result = self.players[i].split_check()
                if result == True:
                    answer = raw_input("Player {0}, you have a pair showing. Would you like to split your hand? (y/n)".format(self.players[i].name))
                    if (answer[0].lower() == 'y'):
                        print("Splitting your hand per your request.")
                        self.players[i].split_pair()
                        print("Here is the result of the split.")
                        self.players[i].print_split()
                        print("Before I can deal you another card for each hand, you need to place a separate bet on your split hand.")
                        while True:
                            print("The same rules apply to this hand. The table minimum is ${0} and maximum is ${1}.".format(min_bet, max_bet))
                            bet = raw_input("Player {0}, you have {1} remaining. What would you like to bet? ".format(self.players[i].name, self.players[i].bank))
                            # Call the update_split_bet method for the player in question. It has all kinds of
                            # error trapping functionality.
                            result = self.players[i].update_split_bet(bet, min_bet, max_bet)
                            if result == 'success':
                                break
                            else:
                                print("Please try again.")
                                continue
                        print("Thank you for your bet. Dealing cards to each hand.")
                        card = self.deck.remove_top()
                        # All hands should be playable since they only have two cards. So, the results
                        # do not need to be tracked here. The hit/stand part of the player turn will 
                        # catch all of that.
                        self.players[i].add_card_to_hand(card)
                        card = self.deck.remove_top()
                        self.players[i].add_card_to_split(card)
                        print("Here are your new hands and their scores.")
                        print(self.players[i])
        return
    
    def double_down(self):
        '''
        This method runs around the table, calling Player.double_down() to check that they have two cards
        in the hand and to ask if they want to double down on their current bet on that hand. The reason
        it checks to see if they have 2 cards in that hand is that a blackjack would have already been
        resolved by this point and the hand reset to an empty list.
        
        The Player class method is as follows: Player.double_down(card_hand, flag).
        
        The card_hand is either the Player.hand or Player.split_hand attribute that needs to be examined.
        The second argument is a boolean telling the method if the hand is the regular or split hand.
        True = split hand, False = regular hand. The updated bets are handled by Player.double_down and
        the Player.update_bet and Player.update_split, which handles betting errors.
        
        After all player's bets have been updated, it prints the CasinoTable again.
        '''
        for i in xrange(1, self.table_index):
            # This checks the regular hand and offers a double down bet.
            self.players[i].double_down(self.players[i].hand, False)
            if self.players[i].split_flag == True:
                # There is a split hand that must be checked and a double down bet offered.
                self.players[i].double_down(self.players[i].split_hand, True)
        # Now that all bets have been updated, reprint the table. The print(Player) method skips
        # the hands and bets of any player with an already empty hand.
        print(self)
        return
    
    def hit_or_stand(self):
        '''
        This method is used to beging the player turn. During the player turn, the method asks each player
        who has a playable hand if they want an additional card. A "hit" response gets a dealt card. It
        does this by taking the top card and calling Player.add_card_to_hand or, for the split hand,
        add_card_to_split. These methods rescore the hand and return False if the player busts. If the
        hand is playable, it will return True to hit_or_stand, which will ask the player if they want yet
        another card.This continues until either the player busts or the player replies "stand".
        
        If the player busts, hit_or_stand calls Player.reg_loss or Player.split_loss to wrap up the lost
        bets. Player winnings will be handled by CasinoTable.dealer_turn().
        
        The player must reply either "hit" or "stand". All other responses will be ignored and will loop
        back to get one of the two acceptable responses. Once a player stands, their part of the player
        turn is over.
        
        Breaking the bank does not mean the end of the player's game at this point, since they could
        win an insurance bet or a split hand. It will remove them if they do not have a split hand or
        and insurance bet, however.
        
        OUTPUT: string indicating the status of the game at the end of the players turn
            'none' = all players were eliminated in this round or all hands were e
            'playable' = at least one hand remains to challenege the Dealer
        '''
        # This will increment as playable hands survive the players turn.
        playable_hands = 0
        for i in xrange(1, self.table_index):
            # First, we need to check the hand. An non-empty hand will be playable after being dealt two
            # cards. Empty hands already collected their blackjack winnings. A blackjack has no split
            # hand either.
            if len(self.players[i]) != 0:
                while True:
                    print(self.players[i])
                    answer = raw_input("Player {0}, would like another card for your original hand? (hit/stand): ".format(self.players[i].name))
                    if (answer.lower() != 'hit') and (answer.lower() != 'stand'):
                        print("Please respond with 'hit' or 'stand.")
                        continue
                    elif answer.lower() == 'hit':
                        card = self.deck.remove_top()
                        rank, suit = card
                        print("New card is {0}-{1}".format(rank, suit))
                        result = self.players[i].add_card_to_hand(card)
                        if (result == 'bust'):
                            print(self.players[i])
                            loss_result = self.players[i].reg_loss()
                            self.players[0].dealer_won(self.players[i].bet)
                            if loss_result == False:
                                if (self.players[i].split_flag == False) and (self.players[i].insurance == 0):
                                    # The player's bank is zero or negative from the first hand. If they
                                    # have no split hand nor an insurance bet, they are eliminated at
                                    # this point.
                                    print("Player {0} has broken their bank and will be eliminated from the game".format(self.players[i].name))
                                    print("at the end of the round.")
                                    break
                                else: 
                                    print("Player {0} busted, but may survive the round on a split hand or insurance bet.".format(self.players[i].name))
                                    break
                            else:
                                print("Player {0} busted, but still has ${1} remaining.".format(self.players[i].name, self.players[i].bank))
                                break
                        else:
                            # The hand is playable. Loop back and ask them if they want to hit or stand.
                            continue
                    else: # answer.lower() == 'stand'
                        playable_hands += 1
                        print("Player {0} stands. Good luck in the Dealer's turn.".format(self.players[i].name))
                        break
            # Now, we need to deal with a split hand, if it exists.
            if self.players[i].split_flag == True:
                print("Entering split hand algorithm.")
                while True:
                    print(self.players[i])
                    answer = raw_input("Player {0}, would like another card for your split hand? (hit/stand): ".format(self.players[i].name))
                    if (answer.lower() != 'hit') and (answer.lower() != 'stand'):
                        print("Please respond with 'hit' or 'stand.")
                        continue
                    elif answer.lower() == 'hit':
                        card = self.deck.remove_top()
                        rank, suit = card
                        print("New card is {0}-{1}".format(rank, suit))
                        result = self.players[i].add_card_to_split(card)
                        if (result == 'bust'):
                            print(self.players[i])
                            loss_result = self.players[i].split_loss()
                            self.players[0].dealer_won(self.players[i].split_bet)
                            if loss_result == False:
                                if (self.players[i].insurance == 0):
                                    # The player's bank is zero or negative from losses this turn. If they
                                    # have no insurance bet, they are eliminated at this point.
                                    print("Player {0} has broken their bank and been eliminated from the game.".format(self.players[i].name))
                                    break
                                else: 
                                    print("Player {0} busted, but may survive the round on an insurance bet.".format(self.players[i].name))
                                    break
                            else:
                                print("Player {0} busted, but still has ${1} remaining.".format(self.players[i].name, self.players[i].bank))
                                break
                        else:
                            # The hand is playable. Loop back and ask them if they want to hit or stand.
                            continue
                    else: # answer.lower() == 'stand'
                        playable_hands += 1
                        print("Player {0} stands. Good luck in the Dealer's turn.".format(self.players[i].name))
                        break
            i += 1
        # This ends the players turn.
        print("The player turn is complete. The table stands at:")
        print(self)
        if self.table_index == 0:
            print("No players remain in the game. The house wins.")
            return 'none'
        if playable_hands == 0:
            # No playable hands remain.
            return 'none'
        else:
            return 'playable'
    
    def dealer_autowin(self):
        '''
        This method is used when CasinoTable.hit_or_stand() returns "redeal". In that case, the dealer has 
        already resolved blackjack wins and all subsequent busts that eliminated the remaining hands in the
        round. It simply prints out the dealer's actual hand.
        
        This method retuns no values.
        '''
        self.players[0].dealer_print()
        print("The Dealer does not need to play its hand since all player hands have been resolved.")
        return
    
    def max_min_score(self):
        '''
        This method extracts the minimum and maximum scores for player's hands from the remaining hands. It
        ignores any removed hands. It looks at the soft_hand_score, which is the highest playable score a
        hand of Blackjack can have.
        
        If self.table_index < 2, no human players remain in the game. It will return (0,0) as an error.
        
        It returns a tuple in the form (max, min).
        '''
        max_score = min_score = 0
        if self.table_index < 2 :
            # No human players remain in the game.
            return (max_score, min_score)
        # At least one human player remains in the game. We need the scores off of one of their hands.
        
        # print("Max: {0}.   Min: {1}".format(max_score, min_score))
        for i in xrange(1, self.table_index):
            # print(self.players[i])
            if (len(self.players[i]) != 0):
                if self.players[i].soft_hand_score > max_score:
                    max_score = self.players[i].soft_hand_score
                # The next if statement should ensure that min_score is also non-zero if a hand still exists.
                if (min_score == 0) and (self.players[i].soft_hand_score != 0):
                    min_score = self.players[i].soft_hand_score
                if (0 < self.players[i].soft_hand_score < min_score):
                    min_score = self.players[i].soft_hand_score
            # print("Max: {0}.   Min: {1}".format(max_score, min_score))
            if (len(self.players[i].split_hand) != 0):
                if self.players[i].soft_split_score > max_score:
                    max_score = self.players[i].soft_split_score
                # The next if statement should ensure that min_score is also non-zero if a hand still exists.
                if (min_score == 0) and (self.players[i].soft_split_score != 0):
                    min_score = self.players[i].soft_split_score
                if (0 < self.players[i].soft_split_score < min_score):
                    min_score = self.players[i].soft_split_score                
            # print("Max: {0}.   Min: {1}".format(max_score, min_score))
        return (max_score, min_score)       
    
    def dealer_turn(self):
        '''
        This method performs the dealer turn. It is used when CasinoTable.hit_or_stand() method returns
        "playable", indicating at least one playable hand remains, besides the dealer. It uses the 
        method Dealer.dealer_print() instead of Dealer.__str__() so that the hold card stays revealed.
        
        The standard casino rules for the Dealer's turn are as follows:
            * dealer stands on a hard 17+ 
            * dealer stands on any 21 (blackjack or otherwise)
            * dealer must take a card on a soft 16-
            * dealer must stand on a hard 16- with a soft score that beats at least one players playable hand AND
                is greater than 16.
            * dealer must take a card on a hard 16- with a soft score that does not beat any playable player hands
        
        If the Dealer has blackjack, the insurance bets will be paid out, if any. The remaining players
        lose automatically. If a tie occurs, even on a non-blackjack 21, no remaining players, including
        the Dealer, lose their bets. If the Dealer's hand score is higher than a player's, dealer wins.
        If any player has a higher hand score than the Dealer's, that player wins.
        
        Variables:
            dealer_blackjack = boolean True for a blackjack, False otherwise
            dealer_stand = boolean True once the dealer must stand, False otherwise
            dealer_bust  = boolean True once the dealer busts, False otherwise
            dealer_winnings = aggregate of the dealer's wins applied near the end of the dealer's turn, separate
                from blackjack wins/losses and player busts
            dealer_losses   = aggregate of the dealer's wins applied near the end of the dealer's turn, separate
                from blackjack wins/losses and dealer busts
            min_score = minimum still playable score, extracted while skippng empty hands
            max_score = maximum still playable score, extracted while skippng empty hands
            hand_results = list of string tuples of the form (name, index, outcome, hand_type), where name is
                the player's name, index is their index in the players list, outcome is a string with values:
                'lose' = player's hand lost against the dealer's hand
                'win'  = player's hand won against the dealer's hand
                'tie'  = player's hand tied the dealer's hand
            and hand_type is a string as follows:
                'reg'  = player's hand initial hand in the round
                'split'= player's split hand
        '''
        dealer_blackjack = False
        dealer_stand = False
        dealer_bust = False
        hand_results = []
        dealer_winnings = 0
        dealer_losses = 0
        print("Turning over Dealer's hold card.")
        self.players[0].dealer_print()
        
        # First, we need to check for a Dealer Blackjack.
        if (len(self.players) == 2) and (self.players[0].soft_hand_score == 21) and (self.players[0].hard_hand_score == 11):
            dealer_blackjack = True
            # Setting the dealer_stand boolean to True stops the Dealer from playing 
            # their hand.
            dealer_stand = True
            print("Dealer has a blackjack. All remaning hands lose, regardless of score.")
            for i in xrange(1, self.table_index):
                # Skip resolved hands and non-existent hands.
                if (len(self.players[i]) == 0) and (len(self.players[i].split_hand) == 0):
                    continue
                if len(self.players[i]) != 0:
                    # Mark hand as lost.
                    hand_results.append((self.players[i].name, i, 'lose', 'reg'))
                if len(self.players[i].split_hand) != 0:
                    # Mark hand as lost.
                    hand_results.append((self.players[i].name, i, 'lose', 'split'))
        # Dealer has a normal playable hand. Wins beat the Dealer's final score.
        # Ties are a draw, and players lose if they score less than the Dealer.
        # print("Hand results (blackjack): ", hand_results)
        max_score, min_score = self.max_min_score()
        while (dealer_stand == False):
            self.players[0].dealer_print()
            if self.players[0].hard_hand_score > 21:
                # Dealer busts.
                print("Dealer busted with a hard score of {0}".format(self.players[0].hard_hand_score))
                dealer_bust = True
                dealer_stand = True
                for i in xrange(1, self.table_index):
                    # Skip resolved hands and non-existent hands.
                    if (len(self.players[i]) == 0) and (len(self.players[i].split_hand) == 0):
                        continue
                    if len(self.players[i]) != 0:
                        # Mark hand as winnner.
                        hand_results.append((self.players[i].name, i, 'win', 'reg'))
                    if len(self.players[i].split_hand) != 0:
                        # Mark hand as winner.
                        hand_results.append((self.players[i].name, i, 'win', 'split'))                
                continue
            if self.players[0].hard_hand_score > 16:
                # Dealer must stand on a hard 17 or higher.
                print("Dealer's hard score is {0}, which is greater than 17. Dealer stands.".format(self.players[0].hard_hand_score))
                dealer_stand = True
                continue
            if (self.players[0].hard_hand_score <= 16) and (self.players[0].soft_hand_score > min_score) \
                and (self.players[0].soft_hand_score > 16):
                # Dealer must stand on a soft hand score that beats at least one player and has a score
                # above 16.
                dealer_stand = True
                continue
            # Dealer takes a card.
            card = self.deck.remove_top()
            rank, suit = card
            print("Dealer draws {0}-{1}.".format(rank, suit))
            self.players[0].add_card_to_hand(card)
        # print("Hand results (dealer turn): ", hand_results)
        print("Dealer's turn is complete. Determining any remaining wins and losses.")
        # Now, we have to finish out the hand results. This can be skipped if dealer_blackjack = True
        # or dealer_bust = True. The win/lose/tie data has already been created for both conditions.
        # Remember also that soft scores are always the highest playable score that a hand can have,
        # regardless of the cards dealt.
        if (dealer_blackjack == False) and (dealer_bust == False):
            for i in xrange(1, self.table_index):
                # Again, skip resolved and non-existent hands.
                if (len(self.players[i]) == 0) and (len(self.players[i].split_hand) == 0):
                    continue
                if (len(self.players[i]) != 0):
                    if (self.players[i].soft_hand_score < self.players[0].soft_hand_score):
                        # Player loses to a higher score.
                        hand_results.append((self.players[i].name, i, 'lose', 'reg'))
                    elif (self.players[i].soft_hand_score == self.players[0].soft_hand_score):
                        # Tie result. No one loses their bets.
                        hand_results.append((self.players[i].name, i, 'tie', 'reg'))
                    else:
                        # Player wins.
                        hand_results.append((self.players[i].name, i, 'win', 'reg'))
                if len(self.players[i].split_hand) != 0:
                    if (self.players[i].soft_split_score < self.players[0].soft_hand_score):
                        # Player loses split hand to a higher score.
                        hand_results.append((self.players[i].name, i, 'lose', 'split'))
                    elif (self.players[i].soft_split_score == self.players[0].soft_hand_score):
                        # Tie result. No one loses their bets.
                        hand_results.append((self.players[i].name, i, 'tie', 'split'))
                    else:
                        # Player wins.
                        hand_results.append((self.players[i].name, i, 'win', 'split'))        
        # print("Hand results (dealer scoring): ", hand_results)
        
        # Now to notify the player and total up the wins and losses, starting with the insurance bets.
        # The Player.ins(boolean) method handles this loss by sending the dealer_blackjack flag. It
        # automatically returns the right results. True means the player is still in the game, False,
        # they broke their bank and will be eliminated in the end_round.
        if self.players[0].blackjack_flag == True:
            for i in xrange(1, self.table_index):
                if dealer_blackjack == False:
                    dealer_winnings += self.players[i].insurance
                    print("Player {0}: You have lost your insurance bet of {1}.".format(self.players[i].name, self.players[i].insurance))
                else:
                    dealer_losses += self.players[i].insurance
                    print("Player {0}: You have won your insurance bet of {1}.".format(self.players[i].name, self.players[i].insurance))
                ins_result = self.players[i].ins(dealer_blackjack)
                if ins_result == False:
                    print("Player {0} has broken his bank and will be eliminated at the end of the round.".format(self.players[i].name))
            print("Insurance bets are complete.")
        else:
            print("There were no insurance bets this round.")
        
        for i in xrange(0, len(hand_results)):
            # Each entry in hand_results is a tuple of the form (name, index in players list, outcome, type of hand).
            # The list is ordered and built in the order the players are "seated" at the casino table. The boolean
            # flag for players breaking their bank has to be reset for each hand.
            player_loss = True
            name, num, outcome, hand_type = hand_results[i]
            if (hand_type == 'reg'):
                if (outcome == 'win'):
                    print("Dealer lost to Player {0} with a score of {1} to {2}.".format(name, self.players[0].soft_hand_score, self.players[num].soft_hand_score))
                    dealer_losses += self.players[num].bet
                    self.players[num].win()
                elif (outcome == 'tie'):
                    print("Dealer and Player {0} tied this hand. No losses either way.".format(name))
                    self.players[num].tie()
                else: # Player lost this round.
                    print("Player {0} lost to Dealer with a score of {1} to {2}.".format(name, self.players[num].soft_hand_score, self.players[0].soft_hand_score))
                    dealer_winnings += self.players[num].bet
                    player_loss = self.players[num].reg_loss()
            else: # hand_type == 'split'
                if (outcome == 'win'):
                    print("Dealer lost to Player {0}'s split hand with a score of {1} to {2}.".format(name, self.players[0].soft_hand_score, self.players[num].soft_split_score))
                    dealer_losses += self.players[num].split_bet
                    self.players[num].split_win()
                elif (outcome == 'tie'):
                    print("Dealer and Player {0}'s split hand this round. No losses either way.".format(name))
                    self.players[num].split_tie()
                else: # Player's split hand lost this round.
                    print("Player {0}'s split hand lost to Dealer with a score of {1} to {2}.".format(name, self.players[num].soft_split_score, self.players[0].soft_hand_score))
                    dealer_winnings += self.players[num].split_bet
                    player_loss = self.players[num].split_loss()
            if player_loss == False:
                print("Player {0} has broken their bank and will be eliminated at the end of the round.".format(name))
            else:
                print("Player {0} still has ${1} remaining in the bank after this hand.".format(name, self.players[num].bank))
        
        # Now, we apply the wins and losses to the bank to see if the bank remains in the game.
        self.players[0].dealer_won(dealer_winnings)
        dealer_result = self.players[0].dealer_lost(dealer_losses)
        if dealer_result == False:
            # The Dealer broke their bank.
            print("The Dealer has broke their bank. The game will end at the end of this round.")
        return
    
    def end_round(self, min_bet = 10):
        '''
        This method cleans up at the end of a round of play. Any players, dealer included, who broke their
        banks during play are eliminated. It calls Dealer.end_round() and Player.end_round() to clear hands
        hand scores, and flags. It also offers the option to replace the CardShoe, an action recommended
        once the shoe gets down to less half the original cards (156). This method automatically replaces
        the CardShoe once deck drops to 100 cards or less.
        
        It accepts an integer min_bet that will eliminate a player because their bank cannot sustain the
        next round of betting.
        
        This method returns True if the dealer is eliminated or all players have been eliminated. Both
        conditions end the game. It uses the end_game boolean to signal that.
        '''
        end_game = False
        for i in xrange(0, self.table_index):
            self.players[i].end_round()
            
        if self.players[0].bank <= min_bet:
            del(self.players[0])
            print("The Dealer has been eliminated from the game. The player with the highest bank wins.")
            name = self.players[0].name
            high_bank = self.players[0].bank
            for i in xrange(1, self.table_index - 1):
                if high_bank < self.players[i].bank:
                    name = self.players[i].name
                    high_bank = self.players[i].bank
            print("The winner is Player {0} with a bank of {1}. All players beat the bank, but you won the game.".format(name, high_bank))
            end_game = True
        else:
            print("The Dealer remains solvent. Eliminating other players who have broken their banks.")
            i = 1
            while True:
                if self.players[i].bank <= min_bet:
                    print("Eliminating Player {0} because their bank is unable to make the minimum bet.".format(self.players[i].name))
                    del(self.players[i])
                    self.table_index -= 1
                else:
                    print("Player {0} is still solvent with ${1} remaining in their bank.".format(self.players[i].name, self.players[i].bank))
                    i += 1
                if i == self.table_index:
                    # The index has reached the end of the players list.
                    break
                else:
                    continue
        
        if (len(self.players) == 1) and (self.players[0].name.lower() == 'dealer'):
            print("All human players have been eliminated. The game is over and the House won.")
            end_game = True
        if end_game ==False:
            # We need to test if the deck has too few cards remaining. It should be replaced once it down
            # to less than 100 cards since this is a text game with a running tally of cards played.
            if len(self.deck) <= 100:
                print("The card shoe has too few cards for the games to remain random. Replacing the shoe.")
                self.replace_cardshoe()
                print("New card shoe is ready.")
                print(self.deck)
            else:
                print("You may request a new card shoe between rounds. It is recommended once a card shoe drops below 150 cards.")
                print(self.deck)
                while True:
                    try:
                        answer = raw_input("Would you like to replace the Card Shoe? (y/n)")
                    except:
                        print("Please try again.")
                        continue
                    if (answer[0].lower() != 'y') and (answer[0].lower() != 'n'):
                        print("Please try again.")
                        continue
                    else:
                        break
                if answer[0].lower() == 'y':
                    self.replace_cardshoe()
                    print("New card shoe is ready.")
                else:
                    print("The deck shoe will not be replaced.")
        # This prints out who is left and how much money they have left. All hands and bets have been reset.
        print(self)
        return end_game            
        
    def replace_cardshoe(self):
        '''
        This method deletes the current shoe and initializes a new one. This is recommended once a shoe
        drops to 50% (156) of the original cards. It returns no values.
        '''
        del(self.deck)
        self.deck = CardShoe()
        return

    def start_round(self):
        '''
        This method begins a new round. The previous round (or __init__) already cleared some attributes and updated
        others. So, that does not need to be done. Instead, this round determines which players wish to remain in 
        the game.
        
        Theoretically, this method could be used to add new players at available stations as well.
        
        This method accepts no values. It returns True if enough players remain to continue playing. It returns
        False if not.
        '''
        print("Now, each player needs to decide if they want to stay or cash out.")
        for i in xrange(1, self.table_index):
            failsafe = 0
            while True:
                # The following statements ensure that this does not become a continuous loop should input errors
                # persist.
                failsafe += 1
                if failsafe > self.table_size :
                    break
                try:
                    answer = raw_input("Player {0}, would you like to stay in the game? (y/n)".format(self.players[i].name))
                except:
                    print("An error occurred. Please try again.")
                    continue
                else:
                    if (answer[0].lower() != 'y') and (answer[0].lower() != 'n'):
                        print("Invalid response. Please try again.")
                        continue
                    elif answer[0].lower() == 'n':
                        print("It was a pleasure. Please stop by the bank windows to cash out.")
                        del(self.players[i])
                        self.table_index -= 1
                    else:
                        print("Thank you.")
                    break
        if self.table_index <= 1:
            print("That ends the game. Thank you for playing.")
            return False
        else:
            print("Preparing to deal the next round.")
            return True
