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
        __init__: Creats a table, initializing the attributes. It will generate a CardShoe,
            a Dealer, and prompt for players up to table_size. It accepts an integer for
            dealer's starting bank, but has a default of 100,000. Starting bank can be
            overridden in a derived class.
        __str__: Prints out the table for the players to see. Normally, used after a full
            deal has been done.
        diagnostic_print: prints out all attributes to assist with code debugging
        rules: this announces the general rules of play, including using 'Break the bank'
            to defeat the house
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
            ○ dealer stands on a hard 17+
            ○ dealer stands on any 21 (blackjack or otherwise)
            ○ dealer must take a card on a soft 16 or less
            ○ dealer must stand on a hard 16 or less with a soft score that beats at least
                one players playable hand and is greater than 16.
            ○ dealer must take a card on a hard 16- with a soft score that does not beat any
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
    def __init__(self, starting_bank = 100000):
        '''
        This method creates several objects and attributes.
        
        For initial testing:
            blackjack multiplier will be set to ('3:2', 1.50)
            starting bank will be 10,000
            table_size will be 3 for testing and 5 for normal play.
            
        '''
        self.blackjack_multiplier = ('3:2', 1.50)
        print("This table has a blackjack payout of ", self.blackjack_multiplier[0])
        self.starting_bank = starting_bank
        self.table_size = 3
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
If all players busted in their turn, the dealer is required only to reveal their
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
            ○ dealer stands on a hard 17+ 
            ○ dealer stands on any 21 (blackjack or otherwise)
            ○ dealer must take a card on a soft 16-
            ○ dealer must stand on a hard 16- with a soft score that beats at least one players playable hand AND
                is greater than 16.
            ○ dealer must take a card on a hard 16- with a soft score that does not beat any playable player hands
        
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