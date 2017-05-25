class Dealer(Player):
    """
    This is a derived class from base clase Player. The purpose of this class is to create a special type
    of player, called the Dealer. The dealer has no split hands, has rules about taking cards after reaching
    a hard score of 17, and places no actual bets.
    
    Class Order Attributes:
        name = 'Dealer'
        
    Inherited Class Order Attributes:
        values
        
    Attributes:
        hand: tracks the card tuples (rank, suit) of the cards in the Dealer's hand
        soft_hand_score: integer value of the current "soft" score of the Dealer's hand
        hard_hand_score: integer value of the "hard" score of the player's hand
        visible_card: single tuple showing hand[0]
        visible_score: integer score of the visible card
        blackjack_flag: True if the dealer's visible card is an Ace or a 10 value card,
            False otherwise
    
    Inherited Attributes (from Player class):
        hand, soft_hand_score, hard_hand_score
    
    Methods:
        __init__: initializes the attributes specific to dealer objects
        __str__: Prints Dealer (self.name), dealer's visible_card, and the 
            score for the visible card. Used during player turns.
        dealer_print: prints the actual hand and score in a format similar
            to the print(Player) function. Used during dealer's turn.
        add_card_to_hand: adds a card to the dealer's hand, updates 
            visible_card (a hand) and its scores on second deal, updates
            the actual hand scores,  sets the blackjack_flag for the right
            ranks of visible_card, and returns 'playable', 'blackjack', 
            or 'bust' when finished. Like the Player version, it uses the
            inherited score_hand() method for scoring visible and actual hands.
        end_round: resets to start hand data and flags
            dealer_bust: This method accepts accepts an integer of the total bets
            of players not eliminated during the player turns in this round. The
            method deducts this total bet from the dealer's bank.
        dealer_bust: accepts an integer of the total bets of players not eliminated during
            the player turns in this round. The method deducts this total bet from the dealer's
            bank. If the losses break the bank, it returns False. Otherwise, it returns True.
        
    Inherited Methods (from Player class):
        __len__, __del__, score_hand

    """
    name = 'Dealer'
    
    def __init__(self):
        '''
        This method creates the following attributes for Dealers:
            hand: creates an empty list
            soft_hand_score: set to 0
            hard_hand_score: set to 0
            visible_card: empty list
            visible_score: set to 0
            blackjack_flag: set to False
        '''
        self.hand = []
        self.bank = 100000
        self.soft_hand_score = self.hard_hand_score = 0
        self.visible_card = []
        self.visible_soft_score = self.visible_hard_score = 0
        self.blackjack_flag = False
        return        
    
    def __str__(self):
        '''
        This method prints out the Dealer's info, concealing the facebown card and its score.
        It is used to show this derived class during the player turns so that a separate
        method would not be needed to print the table out. Another method,
        Dealer.dealer_print() prints out the full Dealer data during the dealer's turn.
        '''
        print("Dealer")
        print("Dealer's Bank:\t${0}.00".format(self.bank))
        print("\n\tDealer shows: ", end='')
        # This suppresses the line feed.
        
        if len(self) >= 1:
            print("Facedown", end='')
        if len(self) >= 2:
            (rank,suit) = self.visible_card[0]
            print("  {0}-{1}".format(rank, suit), end='')
        if self.visible_soft_score == self.visible_hard_score:
            print("\n\tDealer has {0} showing".format(self.visible_hard_score))
        else:
            print("\n\tDealer has a hard {0} or a soft {1} showing".format(self.visible_hard_score, self.visible_soft_score))
        return "Dealer complete"
    
   
    def dealer_print(self):
        '''
        This method is used during the dealer's turn to print out the full hand and
        hand scores.
        '''
        print("Player:\t", self.name)
        print("Bank:\t${0}.00".format(self.bank))
        print("\n\tCurrent Hand: ", end='')
        # This suppresses the linefeed and flushes the buffer to make the ouput
        # look like a single line of code.
                                                      
        for rank, suit in self.hand:
            print("{0}-{1}  ".format(rank,suit), end='')
        print("\n\tSoft score for this hand: ", self.soft_hand_score)
        print("\tHard score for this hand: ", self.hard_hand_score)
        return "Data on "+ self.name + " is complete"
    
    def add_card_to_hand(self, card):
        '''
        Functionality carried over from Player.add_card_to_hand():
        
        This method accepts a card tuple (rank, suit) as argument. It places this card into
        the Dealer.hand list. It calls the internal method score_hand to rescore the hard
        and soft scores of the hand. The hard score for a hand will be equal to the soft
        score if there are no aces in the hand. The soft_score can be greater than the hard
        score if scoring any ace in the hand as an 11 would result in a playable hand. In
        fact, blackjack (a natural 21) has a hard score of 11, while the soft score is 21.
        
        New functionality specific to Dealer class:
        
        On second deal, assign the second card to visible_card and run score_hand on this
        card to get soft and hard visible scores. Sets the blackjack_flag to True if 
        visible_card is an Ace, a face card, or a 10.
        
        INPUT: card, a tuple of (rank, suit)
        OUTPUT: This function returns the following:
            'blackjack'  = the soft score is 21, the hard score is 11, and the len(hand)
                           is 2 (meaning the starting deal was a blackjack)
            'bust'       = the hard_score is greater than 21
            'playable'   = at least one score is less than or equal to 21. If one is 21,
                           the hand is "longer" than 2 cards
        '''
        self.hand.append(card)
        (self.soft_hand_score, self.hard_hand_score) = self.score_hand(self.hand)
        # If this is the second card dealt to the Dealer, add it to the visible card
        # and score it.
        if len(self) == 2:
            self.visible_card.append(card)
            (self.visible_soft_score, self.visible_hard_score) = self.score_hand(self.visible_card)
            # For a visible Ace, face card, or 10, the blackjack flag needs to be set to
            # True so that insurance bets can be placed on it.
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
        This method resets all data, except Dealer.name, and Dealer.bank. This method takes no
        arguments and returns no values. It may not be needed in the game.
        '''
        self.hand = []
        self.soft_hand_score = 0
        self.hard_hand_score = 0
        self.blackjack_flag = False
        self.visible_card = []
        self.visible_soft_score = 0
        self.visible_hard_score = 0
        return

    def dealer_bust(self, remaining_bets):
        '''
        This method accepts accepts an integer of the total bets of players not eliminated during
        the player turns in this round. The method deducts this total bet from the dealer's bank.
        If the losses break the bank, it returns False. Otherwise, it returns True.
        '''
        losses = remaining_bets
        self.bank -= losses
        if self.bank <= 0:
            print("The Dealer's bank has been broken. The player with highest bank wins the game.")
            return False
        else:
            print("The Dealer remains solvent. The game may continue.")
            return True
