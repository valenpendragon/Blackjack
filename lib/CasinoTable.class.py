class CasinoTable(object):
    """
    This class simulates an actual casino table.
    
    Class Order Attributes:
        None currently
    
    Attributes:
        blackjack_multiplier: tuple storing ('ratio', float multiplier)
            ratio is a string that prints out a ratio, like 3:2, or 6:5 which represents
                the payout ratio for a player blackjack
            multiplier is a floating point two decimal approximation of the ratio used to
                calculate the actual winnings
            This tuple is used to storage and manage the table mulitiplier
        starting_bank: integer overrides the default of 100,000 if the bank is larger or
            smaller, if non-zero
        table_size: integer indicating the max number of players (other than dealer) for
            this table object (3 or 5, normally)
        table_index: the actual max index for the players list
        deck: a CardShoe object that can be recreated via replace_cardshoe method
        players: list of players associated with the table.
            players[0]: a Dealer object initialized with starting bank, if non-zero, or the
                default of 100,000 otherwise
            players[1+]: Player objects up to the max number the table allows (table_size)
    
    Methods:
        __init__: Creats a table, initializing the attributes It will generate a CardShoe,
            a Dealer, and prompt for players up to table_size. It accepts an integer for
            dealer's starting bank, but has a default of 100,000 (10,000 during testing).
        __str__: Prints out the table for the players to see. Normally, used after a full
            deal has been done.
        diagnostic_print: prints out all attributes to assist with code debugging
        deal_round: Deals a round of cards to each player, printing out the table when 
            completed. It checks for player blackjacks and pays them out. it also checks
            the dealer's blackjack_flag and offers insurance bets.
    """
    def __init__(self, starting_bank = 10000):
        '''
        This method creates several objects and attributes.
        
        For initial testing:
            blackjack multiplier will be set to ('3:2', 1.50)
            starting bank will be 10,000
            table_size will be 1. It will be increased to 3, then to 5.
            
        '''
        self.blackjack_multiplier = ('3:2', 1.50)
        print("This table has a blackjack payout of ", self.blackjack_multiplier[0])
        self.starting_bank = starting_bank
        self.table_size = 2
        print("This table allows {0} player(s).".format(self.table_size))
        self.table_index = self.table_size + 1
        self.players = []
        self.deck = CardShoe()
        self.players.append(Dealer(self.starting_bank))
        for i in xrange(1, self.table_index):
            player_num = i
            name = raw_input("Please give the name for Player {0}. Type 'none' when finished.".format(player_num))
            if name != 'none':
                self.players.append(Player(name))
                
            else:
                self.table_index = i
        return
    
    def __str__(self):
        '''
        This method prints out the table. It is used after deals; so, all players can 
        see their cards as they receive them.
        '''
        print(self.deck)
        for i in xrange(0, self.table_index):
            print(self.players[i])
        return 'Table complete'
    
    def diagnostic_print(self):
        '''
        This method prints out every attribute for debugging purposes, calling the same
        named method in the classes for each object.
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
        This prints out a quick list of the rules, including table rules, for the current
        game. Most people do not know that full rules of Blackjack.
        '''
        print("The rules of Casino Blackjack (infodump but important one):")
        print("""The first myth to 'dash' is that ties do not automatically give the house
a win. A blackjack is a 21 accomplished with the first two cards dealt to any
player. A blackjack for a player is an automatic win with an extra table multiplier,
even if the dealer has one.\n
A blackjack for the dealer is an automatic win against any player without
a blackjack. However, if the dealer has an ace, a 10, or a face card showing,
players will be given the opportunity to place an 'insurance' bet that the
dealer has a blackjack. So, players can still 'win' against a dealer blackjack.
If a player other than the dealer has a pair, they will be offered the option
to split the pair into two hands. The second hand is called a 'split hand'.
With a split, blackjack is no longer possible, but you can still beat the dealer
twice potentially.\n
In a tie score with the dealer, the hand is considerd a draw. Neither the
dealer nor the tying player loses the bet.\n
All cards are drawn from a six deck shoe. This is literally a random
rearrangement of six fifty-two card decks. Two cards are dealt to each player,
including the dealer. The dealer's first card is dealt facedown, but all others
are dealt face up. They are also given a score as cards are added to the hands.\n
Scoring is the face value of the card. Face cards are worth 10 points. Aces
can be 1 or 11. The soft score checks to see if a playable hand can be made with
at least one ace scored as 11. The hard score treats any ace as a 1. Blackjack
has a soft score of 21 and a hard score of 11 with the first two dealt cards.
With hands that have no aces, both scores will be equal.\n
Betting and the round takes place as as follows:
\tBefore any cards are dealt, an initial bet is made by each player.
It must be at least the table minimum and not greater than the table maximum.
After two cards have been dealt, players have the option of doubling down if they
do not have a blackjack already (see previous rules about automatic wins). Doubling
down means that the player may bet up to their original bet, doubling the bet, even
if the amount of the new bet goes over the table limit. A zero bet at this point is
taken as the player changing their minds about doubling down. If a player has a pair
and opts to split their hand, a new bet must be made on the new hand subject to the
same rules. Two cards, one for each hand, are dealt, and the player may double down
on either hand if they wish.\n
Once two cards have been dealt and initial blackjacks and splits are taken care
of, each player in turn is asked if they want a 'hit' or 'stand'. Each time a player
replies 'hit', they will be dealt another card and their new hand rescored. So long
as their 'hard' score remains 21 or less, their hand is considered playable. If their
hard score exceeds 21, they bust and lose automatically, even if the dealer busts
later in the round. Once a player replies 'stand', that hand will receive no further
cards. If the player has a split hand, the process repeats for their second hand.\n
Once all players have either busted or stopped with a playable hand, the dealer's
turn begins. First, the dealer reveals the facedown or 'hold' card. If the dealer has
a blackjack, all remaining hands lose, and any players with insurance bets win those
bets. If the dealer does not have a blackjack, the dealer must take 'hits' (dealt
cards) until their hard score reaches at least 17 or busts. If the dealer has a soft
score between 17 and 21 and a hard score under 17, the dealer will take additional
cards until their hard score exceeds 17 or their soft score beats at least one
remaining player's score. Any time the dealer busts, all players with playable hands
win their bets automatically.\n
If all pleyers busted in their turn, the dealer is required only to reveal their
hold card, as the dealer wins is automatically. All insurance bets will still payout
on a dealer blackjack.\n
Players at the table may leave after a round and they get a score at the end which is
equal to their remaining bank.\n
Now, this is a video game. To make it a little more interesting, players may stay in
the game until the dealer's bank is broken. Then, the player with the highest bank
wins, but, in reality, all of the players at the table just 'Beat the Bank'.""")
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
            result = self.players[i].add_card_to_hand(card)
            if result == 'blackjack':
                print("Congratulations Player {0}, you have a Blackjack!!!".format(self.players[i].name))
                winnings = int(self.players[i].bet * self.blackjack_multiplier[1])
                print("You have won $", winnings)
                self.players[i].blackjack(self.blackjack_multiplier[1])
                self.players[0].dealer_losses(winnings)
        print("Dealing a card to ", self.players[0].name)
        card = self.deck.remove_top()
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
