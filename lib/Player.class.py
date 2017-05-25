from __future__ import print_function

class Player(object):
    """
    This class creates Hands for a Blackjack player.
    
    Terms related to game play:
        players_turn: The part of a round of play in which players are playing their hands, in
            rotation around the "table"
        dealer_turn: The part of the round of play in which the dealer plays his/her hand
        round: A deal, followed by players deciding bets and card draws, followed by dealer's turn,
            and ending with settling wins and losses for the player hands
        game: A series of rounds of play until either all players run out of money or decide to
            stop playing and "cash out". After all players quit, a final tally of their money
            determines the winner of the game.
    
    Class Order Attributes:
        values: dictionary of the scoring for each rank of blackjack card (it was not in use
            in CardShoe class). It is a COA because it is needed for every player object.
        
    Attributes:
        name: stores the player's name
        hand: tracks the card tuples (rank, suit) of the cards in the player's regular hand
        soft_hand_score: integer value of the current "soft" score of the player's hand
        hard_hand_score: integer value of the "hard" score of the player's hand
        split_flag: boolean set to True if the player splits, False if not.
        split_hand: tracks a second hand created by a split
        soft_split_score: integer value of the current "soft" score of the player's split hand,
            if it exists
        hard_split_score: integer value of the current "hard" score of the player's split hand,
            if it exists
        bank: integer number of dollars the player currently has in chips
        bet: current amount bet on the outcome of the hand vs dealer's hand
        split_bet: tracks any bets applied to a card split hand
        insurance: tracks the amount of any side bets taken on the dealer getting blackjack. It
            takes a boolean for the Dealer's blackjack. It returns True for a positive bank,
            False if the Player's bank is zero or negative.
    
    Methods:
        __init__: Creates the player object, initializing all of the attributes. The bank has a
            default value of 1000 dollars.
        __str__: This method prints the player's name, the player's bank, bets, and primary hand.
            If the split_flag is True, it will print that data as well.
        __del__: prints a message while removing the player object
        __len__: prints out the len of the player's regular hand (This is used to determine
            player blackjack)
        print_split: This method does the same thing as __str__ except that it prints only the data
            for the split hand
        score_hand: takes a hand and returns the soft and hard scores for the hand as a tuple
            (soft, hard)
        add_card_to_hand: akes a card, adds it to the hand, calls score_hand to get the new hard 
            and soft scores, and returns 'blackjack', 'bust', or 'playable'
        add_card_to_split: takes a card, adds it to the split hand, calls score_hand to get a 
            new hard and soft scores for it, and returns 'bust' or 'playable'
        blackjack: takes the player's regular bet, mulitplies it by the Blackjack multiplier
            (supplied via argument), and clears the regular hand attributes
        win: adds the player's bet to their bank and clears the regular hand attributes
        split_win: add the player's split bet to the bank and clears the split hand attributes
        reg_loss: subtracts the player's bet from the bank and clears the regular hand
            attributes. Returns False if the player's bank is now empty, ending their game.
        split_loss: subtracts the player's split bet from the bank and clears the split hand
            attributes. Returns False if the player's bank is now empty, ending their game.
        tie: clears the regular hand and bet without deduction from the bank
        split_tie: clears the split hand and bet without deduction from the bank
        split_pair: moves one card over to the split_hand, prompts for a initial
            split_bet, and sets the split_flag to True. Adjusts the scores accordingly.
        split_check: checks for a pair in the initial deal. Returns True if so, False otherwise.
        end_round: verifies that all hands are empty, the split_flag has been reset, and all bets
            have been reset to zero (including insurance)
        update_bet: this method makes sure that the player has the money to cover the new amount
            of their regular bet and all other bets. If so, it returns 'success'. If not, it 
            returns an error code. The argument is the amount to increase the bet.
        update_split_bet: this method makes sure that the player has the money to cover the new
            amount of their split bet and all other bets. If so, it returns 'success'. If not,
            it returns an error code. The argument is the amount to increase the bet.
        update_ins: this method makes sure that the player has the money to cover the new amount
            of their insurance bet and all other bets. If so, it return 'success'. If not, it
            returns an error code.  The argument is the amount to increase it.
        total_bets: the calculates the total of all bets currently accepted for the player, 
            including an insurance bet.
        double_down: checks to see if the hand has 2 cards. if so, it offers an update to the 
            bet of up to double the original amount. A 0 amount will be considered an change of 
            heart. it loops until a valid amount is entered. it calls the appropriate bet method
            for the type of hand.
        
      
    """
    values = {'A': 1, '2' : 2, '3' : 3, '4' : 4, '5' : 5, '6' : 6, \
              '7' : 7, '8' : 8, '9' : 9, '10' : 10, 'J' : 10, 'Q' : 10,\
              'K' : 10 }
    
    
    def __init__(self, name, bank=1000):
        '''
        This method intializes all of the following attributes:
            name: takes a string to initialize the player's name
            bank: takes a non-negative integer and stores it (even for Dealer). This attribute
                has a default of $1000 dollars if not specified
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
    
    def __str__(self):
        '''
        This method prints out the full data on a Player in a readable format. If
        the split_flag is True, it adds the data for a split hand as well.
        '''
        print("Player:\t", self.name)
        print("Chips:\t${0}.00".format(self.bank))
        print("\n\tCurrent Hand: ", end='')
        # This suppresses the linefeed and flushes the buffer to make the ouput
        # look like a single line of code.
                                                      
        for rank, suit in self.hand:
            print("{0}-{1}  ".format(rank,suit), end='')
        print("\n\tSoft score for this hand: ", self.soft_hand_score)
        print("\tHard score for this hand: ", self.hard_hand_score)
        print("\n\tBet on this hand: $", self.bet)
        if self.split_flag == True:
            print("\n\tSplit Hand: ", end='')
            for rank, suit in self.split_hand:
                print("{0}-{1}  ".format(rank,suit), end='')
            print("\n\tSoft score for this hand: ", self.soft_split_score)
            print("\tHard score for this hand: ", self.hard_split_score)
            print("\n\tBet on this hand: $", self.split_bet)
        print("\nInsurance against Dealer Blackjack: $", self.insurance)
        return "Data on "+ self.name + " is complete"
    
    def __del__(self):
        '''
        This method removes a player from the game. After deleting it, it prints a message
        and returns True.
        '''
        print("Player has been removed from the game.")
        return True
    
    def __len__(self):
        '''
        This method prints out the length of the player's regular hand. This is used to help
        determine a possible blackjack.
        '''
        return len(self.hand)
    
    def print_split(self):
        '''
        This method prints the player data in a format similar to __str__, but it leaves out
        the regular hand. It accepts no arguments.
        '''
        if self.split_flag == False:
            print("Player {0} does not have a split hand.".format(self.name))
            return False
        print("Player:\t", self.name)
        print("Chips:\t${0}.00".format(self.bank))
        print("\n\tSplit Hand: ", end='')
        for rank, suit in self.split_hand:
            print("{0}-{1}  ".format(rank,suit), end='')
        print("\n\tSoft score for this hand: ", self.soft_split_score)
        print("\tHard score for this hand: ", self.hard_split_score)
        print("\n\tBet on this hand: $", self.split_bet)
        return
    
    def total_bets(self):
        '''
        This method returns a total of all bets placed by the player. It
        accepts no arguments.
        '''
        return self.bet + self.split_bet + self.insurance
    
    def score_hand(self, card_hand):
        '''
        This method accepts a card hand and returns the hard and soft scores for the hand.
        This is in the form of a tuple (soft, hard).
        '''
        soft_score = hard_score = 0
        aces = 0
        for (rank, suit) in card_hand:
            card_score = Player.values[rank]
            # The soft score will always be lower score because values treats Aces as a 1
            # point card. We increment both in case an each score in case an Ace occurred 
            # earlier in the hand. The values dictionary considers A = 1 score.
            soft_score += card_score
            hard_score += card_score
            if rank == 'A':
                # Increment the number of aces.
                aces += 1
        # Now, the hard_score is the minimum value that the hand can have. They will be
        # equal if there are no aces in the hand. They also have no meaning if the
        # hard_score exceeds 21 already. In both cases, they will be equal. For each Ace,
        # we add 10 to the soft_score, and check to see if it busts. If not, we increase
        # the soft_score. 
        if hard_score < 21 and aces != 0:
            for i in xrange(1, aces + 1):
                test_score = soft_score + 10
                if test_score <= 21:
                    soft_score = test_score
        
        # Now, we return the tuple.
        return (soft_score, hard_score)
    
    def add_card_to_hand(self, card):
        '''
        This method accepts a card tuple (rank, suit) as argument. It places this card into
        the Player.hand list. It calls the internal method score_hand to rescore the hard
        and soft scores of the hand. The hard score for a hand will be equal to the soft
        score if there are no aces in the hand. The soft_score can be greater than the hard
        score if scoring any ace in the hand as an 11 would result in a playable hand. In
        fact, blackjack (a natural 21) has a hard score of 11, while the soft score is 21.
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
        if self.hard_hand_score > 21:
            return 'bust'
        elif (self.hard_hand_score == 11) and (self.soft_hand_score == 21) and (len(self) == 2):
            return 'blackjack'
        else:
            return 'playable'
    
    def add_card_to_split(self, card):
        '''
        This method accepts a card tuple (rank, suit) as argument. It places this card into
        the Player.hand list. It calls the internal method score_hand to rescore the hard
        and soft scores of the hand. The hard score for a hand will be equal to the soft
        score if there are no aces in the hand. The soft_score can be greater than the hard
        score if scoring any ace in the hand as an 11 would result in a playable hand. This
        hand cannot have a blackjack result.
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
        This method cleans up after a player achieved a blackjack (natural 21 on the first
        two cards dealt). Casinos always has a better payout ratio for a player winning a
        blackjack (assuming the Dealer doesn't tie with the player).
        
        This method does not return a value. The multiplier needs to be a decimal or an
        integer, not a fraction.
        
        Nothing is done to the split result because no split can occur with a natural 21.
        '''
        winnings = int(multiplier * self.bet)
        self.bank += winnings
        self.bet = 0
        self.hand = []
        self.soft_hand_score = self.hard_hand_score = 0
        return
    
    def win(self):
        '''
        This method cleans up after a player wins with their regular hand. The split_hand
        has a separate method for this purpose.
        
        This method does not accept arguments nor return values.
        '''
        # There is no multiplier for a regular win.
        self.bank += self.bet
        self.bet = 0
        self.hand = []
        self.soft_hand_score = self.hard_hand_score = 0
        return
    
    def split_win(self):
        '''
        This method cleans up a split hand after the split hand wins. The regular hand is dealt
        with in other methods.
        
        This method does not accept arguments nor return values.
        '''
        self.bank += self.split_bet
        self.split_bet = 0
        self.split_hand = []
        self.soft_split_score = self.hard_split_score = 0
        return
    
    def reg_loss(self):
        '''
        This method cleans up a regular hand after the player loses, either to a bust or a lower
        score during the round than the dealer. It also deducts the bet from the player's bank.
        
        This method takes no arguments. It returns True while the players has a positive
        balance in the bank. A zero or negative balance returns False.
        
        Note: This method is predicated on the idea that other methods or functions have made
        certain that the player had enough in their bank to cover bets made.
        '''
        self.bank -= self.bet
        self.bet = 0
        self.hand = []
        self.soft_hand_score = self.hard_hand_score = 0
        if self.bank <= 0:
            return False
        else:
            return True
       
    def split_loss(self):
        '''
        This method cleans up a split hand after the player loses, either to a bust or a lower
        score during the round than the dealer. It also deducts the bet on the split hand from
        the player's bank.
        
        This method takes no arguments. It returns True while the players has a positive
        balance in the bank. A zero or negative balance returns False.
        
        Note: This method is predicated on the idea that other methods or functions have made
        certain that the player had enough in their bank to cover bets made.
        '''
        self.bank -= self.split_bet
        self.split_bet = 0
        self.split_hand = []
        self.soft_split_score = self.hard_split_score = 0
        if self.bank <= 0:
            return False
        else:
            return True
    
    def tie(self):
        '''
        This method clears the regular bet and hand if the hand ties with the Dealer. Ties do
        not normally result in casino wins.
        
        This method accepts no arguments and returns no values. The reason for the latter is that
        there is no deduction from the bank, nor gain in a tie.
        '''
        self.bet = 0
        self.hand = []
        self.soft_hand_score = self.hard_hand_score = 0
        return
    
    def split_tie(self):
        '''
        This method clears the regular bet and hand if the hand ties with the Dealer. Ties do
        not normally result in casino wins.
        
        This method accepts no arguments and returns no values. The reason for the latter is that
        there is no deduction from the bank, nor gain in a tie.
        '''
        self.split_bet = 0
        self.split_hand = []
        self.soft_split_score = self.hard_split_score = 0
        return
    
    def ins(self, dealer_blackjack):
        '''
        This method hands the bets taken on the Dealer getting a blackjack. This bet only happens
        when the Dealer's face up card is an Ace, 10, or face card. Other methods or functions will
        handle creating this bet when the conditions for it are met.
        
        This method takes a boolean indicating if the Dealer has a blackjack. If True, the player
        wins their insurance bet. If False, the player lost the insurance bet.
        
        This method returns a boolean. True indicates that the player still has money in the bank.
        False means they have zero or a negative balance and have to be eliminated from the game.
        
        Note: This method does not care if the insurance bet is zero. In that case, it has no
        effect on their bank balance.
        '''
        if dealer_blackjack == True:
            # The Dealer got blackjack. The player who has a non-zero insurance bet wins the bet.
            self.bank += self.insurance
        else:
            # The Dealer did not get blackjack. The insurance bet is deducted from the player's bank.
            self.bank -= self.insurance
        self.insurance = 0
        # In case the bet was deducted from the bank, we need to check it.
        if self.bank <= 0:
            return False
        else:
            return True
    
    def end_round(self):
        '''
        This method resets all data, except Player.name, and Player.bank. This method takes no
        arguments and returns no values. It also may not be needed for the game.
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
        This method increases the regular bet by the amount of the increase. It will add up all the
        other bets to make sure that player has enough money in the bank to cover it.
        INPUT: integer new_increase (or a float that will be truncated)
        OPTIONAL: min_bet and max_bet are not required (because of defaults), but a casino could
            override the value by including it.
        OUTPUT: string with the following meanings
            'success'   = the bet could be increased
            'bust'      = the bet exceeds the money in the bank
            'size'      = the bet is not allowed because it exceeds double the original bet
            'min'       = the bet is not enough to meet the casino minimums
            'max'       = the bet exceeds the max allowed initial bet
            'TypeError' = at least one numerical argument supplied was not a number
            'Unknown'   = an unknown error occurred
        
        Note: A zero max_bet means that there is no maximum initial bet amount.
        '''
        # The first step is to convert a possible floating point number into an integer.
        try:
            amt_to_increase = int(new_increase)
        except TypeError:
            print("The values is not a number")
            return 'TypeError'
        except:
            print("An unknown error has occurred")
            return 'Unknown'
        else:
            # If it could be converted, the sign needs to be stripped off the value.
            amt_to_increase = abs(amt_to_increase)
        
        # Next, the new amount needs to be checked to see against min and max bets.
        # Note, min and max bets only apply to the bets laid before the cards are 
        # dealt. So, Player.bet = 0 then.
        if self.bet == 0:
            if amt_to_increase < min_bet:
                print("The bet amount is too small.")
                return 'min'
            # A max_bet of zero means there is no maximum (besides the implicit all in).
            if (max_bet != 0) and (amt_to_increase > max_bet):
                print("The bet amount is too large.")
                return 'max'
        # A non-zero bet automatically is subject to the double down rule. A player
        # may not exceed twice their original bet on a "great" hand.
        elif self.bet < amt_to_increase:
            print("Double down exceeds casino allowed amount.")
            print("Players may not increase their bets by more than their original bet.")
            return 'size'
                
        # Now, the total amount of all bets needs be checked against the bank balance.
        # total_bets = self.bet + self.split_bet + self.insurance
        if (self.total_bets() + amt_to_increase) > self.bank:
            print("{0}'s total bets will exceed the bank of {1}".format(self.name, self.bank))
            return 'bust'
        self.bet += amt_to_increase
        print("{0} accepted. New bet amount on this hand is {1}.".format(amt_to_increase, self.bet))
        return 'success'
    
    def update_split_bet(self, new_increase, min_bet=1, max_bet=100):
        '''
        This method increases the regular bet by the amount of the increase. It will add up all the
        other bets to make sure that player has enough money in the bank to cover it.
        INPUT: integer new_increase (or a float that will be truncated)
        OPTIONAL: min_bet and max_bet are not required (because of defaults), but a casino could
            override the value by including it.
        OUTPUT: string with the following meanings
            'success'   = the bet could be increased
            'bust'      = the bet exceeds the money in the bank
            'size'      = the bet is not allowed because it exceeds double the original bet
            'min'       = the bet is not enough to meet the casino minimums
            'max'       = the bet exceeds the max allowed initial bet
            'TypeError' = at least one numerical argument supplied was not a number
            'Unknown'   = an unknown error occurred
        
        Note: A zero max_bet means that there is no maximum initial bet amount.
        '''
        # The first step is to convert a possible floating point number into an integer.
        try:
            amt_to_increase = int(new_increase)
        except TypeError:
            print("The values is not a number")
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
                print("The bet amount is too small.")
                return 'min'
            # A max_bet of zero means there is no maximum (besides the implicit all in).
            if (max_bet != 0) and (amt_to_increase > max_bet):
                print("The bet amount is too large.")
                return 'max'
        # A non-zero bet automatically is subject to the double down rule. A player
        # may not exceed twice their original bet on a "great" hand.
        elif self.split_bet < amt_to_increase:
            print("Double down exceeds casino allowed amount.")
            print("Players may not increase their bets by more than their original bet.")
            return 'size'
                
        # Now, the total amount of all bets needs be checked against the bank balance.
        # total_bets = self.bet + self.split_bet + self.insurance
        if (self.total_bets() + amt_to_increase) > self.bank:
            print("{0}'s total bets will exceed the bank of {1}".format(self.name, self.bank))
            return 'bust'
        self.split_bet += amt_to_increase
        print("{0} accepted. New bet amount on this hand is {1}.".format(amt_to_increase, self.split_bet))
        return 'success'
    
    def update_ins(self, ins_bet, min_bet=0, max_bet=200):
        '''
        This method accepts an insurance bet. This type of bet is a bet that the Dealer will
        have a blackjack if an Ace or a 10-score card is visible. This is a way for the player
        to win money even when the Dealer has a blackjack. There is generally no mininum bet,
        but there is often a maxiumum allowed bet. There are no opportunities to raise this bet
        not can the player place a second such bet if they split their hand.
        INPUT: integer ins_bet (or a float that will be truncated)
        OPTIONAL: min_bet and max_bet are not required (because of defaults), but a casino could
            override the value by including it.
        OUTPUT: string with the following meanings
            'success'   = the insurance bet was acceptable and applied
            'exists'    = the insurance bet has already been made
            'bust'      = the bet exceeds the money in the bank
            'min'       = the bet is not enough to meet the casino minimums
            'max'       = the bet exceeds the max allowed for an insurance bet
            'TypeError' = at least one numerical argument supplied was not a number
            'Unknown'   = an unknown error occurred
        '''
        # The first step is to convert a possible floating point number into an integer.
        try:
            ins_amt = int(ins_bet)
        except TypeError:
            print("The values is not a number")
            return 'TypeError'
        except:
            return 'Unknown'
        else:
            # If it could be converted, the sign needs to be stripped off the value.
            ins_amt = abs(ins_amt)
        
        # Next, we need to check for an existing insurance bet. If it exists already, no
        # changes are permitted.
        if (self.insurance != 0):
            print("An insurance bet has already been made.")
            return 'exists'
        if (ins_amt < min_bet):
            print("The bet amount is below the casino minimum for an insurance bet.")
            return 'min'
        if (ins_amt > max_bet):
            print("The bet amount exceeds the casino maximum for an insurance bet.")
            return 'max'
        # Now, the total amount of all bets needs be checked against the bank balance.
        if (self.total_bets() + ins_amt) > self.bank:
            print("{0}'s total bets will exceed the bank of {1}".format(self.name, self.bank))
            return 'bust'
        self.insurance += ins_amt
        print("{0} has been accepted as an acceptable insurance bet.".format(self.insurance))
        return 'success'
    
    def split_check(self):
        '''
        This method verifies that the player's initial deal supports a split. It returns True
        if the cards are a pair, False otherwise.
        '''
        if (self.hand[0][0] != self.hand[1][0]):
            return False
        else:
            return True
        
    def split_pair(self):
        '''
        This method moves the second card in the player's initial hand to the split_hand, sets
        the split_flag to True, and recalculates the hand scores.
        '''
        self.split_flag = True
        self.add_card_to_split(self.hand[1])
        self.hand.pop()
        (self.soft_hand_score, self.hard_hand_score) = self.score_hand(self.hand)
        (self.soft_split_score, self.hard_split_score) = self.score_hand(self.split_hand)
        return
    
    def double_down(self, card_hand, split):
        '''
        This method determines if the second card has been dealt to a hand. If so, it allows the
        player to "double down", the playe can add to their original bet up to an equal amount, 
        doubling the original bet. They do not have to make an additional bet, however. 0 is an
        acceptable amount.
        INPUT: card_hand, a list of card tuples (rank,suit), and split, boolean indicating if this
            is a split hand, True = split hand, False = normal hand
        '''
        (soft_score, hard_score) = self.score_hand(card_hand)
        if len(card_hand) == 2:
            if soft_score == hard_score:
                print("Player {0}: You have a hard {1} showing.".format(self.name, hard_score))
            else:
                print("Player {0}: You have a hard {1} or a soft {2} showing.".format(self.name, hard_score, soft_score))
            answer = raw_input("Would like to double down now? y/n")
            if answer[0].lower() == 'y':
                if split == True:
                    print("The bet on your split hand was (0). You may increase the bet up to that amount.".format(self.split_bet))
                    while True:
                        try:
                            new_bet = raw_input("Enter an amount between 0 and {0}. 0 indicates you changed your mind.".format(self.split_bet))
                        except:
                            continue
                        else:
                            bet_check = self.update_split_bet(new_bet,0)
                            if bet_check != 'success':
                                print("Please try again.")
                                continue
                        break
                else:
                    print("The bet on your original hand was (0). You may increase the bet up to that amount.".format(self.bet))
                    while True:
                        try:
                            new_bet = raw_input("Enter an amount between 0 and {0}. 0 indicates you changed your mind.".format(self.bet))
                        except:
                            continue
                        else:
                            bet_check = self.update_bet(new_bet,0)
                            if bet_check != 'success':
                                print("Please try again.")
                                continue
                        break
            else:
                print("The bet will remain unchanged.")
            print(self)
        return
