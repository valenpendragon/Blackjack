import random
# from abc import ABCMeta, abstractmethod

class CardShoe(object):
    '''
    This class is used to simulate a six deck shoe.
        
    Class Order Attributes:
        suits: a list of the suits used in normal playing card decks
            S (spades), D (diamonds), H (hearts), and C (clubs). ['S', 'D',
            'H', 'C']
        ranks: a list of the ranks of playing cards in ascending order Ace 
            through King, represented by A, 1, 2, 3,...., 9, 10, J, Q, K.
            ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 
            'Q', 'K']
    
    Attributes
        shuffled_deck : a randomly shuffled shoe created from decks.
        length: the number of cards in the shoe after initialization
    
    Methods:
        __init__ : Initializes shuffled_deck to create a card shoe.
        __str__: prints out the number of cards remaining in the shoe.
        __del__: prints a message the deck show has been removed as it 
            deletes the CardShoe object
        remove_top: removes the top card (index 0) from the shuffled deck
            and returns the tuple of the card (rank, suit)
        diagnostic_print: prints out the entire CardShoe object, including
            all class order attributes, and current attributes
        
    '''
    suits = ['S', 'D', 'H', 'C']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    def __init__(self):
        # decks is created as a set of indexes used to create a shuffled
        # six deck shoe. It is a local variable, not an attribute. It is
        # an ordered list of tuples of the form (rank, suit), where rank
        # is taken from the list CardShoe.rank and suit from list 
        # CardShoe.suits.
        # To prevent cheating, __init__ takes no arguments. Instead,
        # it creates an empty shuffled_deck itself.
        decks = []
        for i in xrange(0, 6):
            for s in CardShoe.suits:
                for r in CardShoe.ranks:
                    decks.append((r,s))
        
        # To create a shuffled card shoe, we need to take a random card from
        # decks and move it into the shoe. We keep doing that until the deck
        # is fully randomized.
        self.shuffled_deck = []
        while len(decks) > 0:
            # card is another local variable. It is a tuple pulled using a
            # random index of the remaining elements in decks.
            # card_index is that random index created using random.randint().
            card_index = random.randint(0,len(decks) - 1)
            self.shuffled_deck.append(decks[card_index])
            del decks[card_index]
        # Now, CardShoe.shuffled_deck contains a shuffled six deck shoe.
        # This length is the number of cards in the initialized deck.
        self.length = len(self.shuffled_deck)
    
    def __len__(self):
        # This len method will print out the number of cards left in the shoe.
        return len(self.shuffled_deck)
    
    def __str__(self):
        # This prints out a statement indicating that the deck has been
        # initialized and the current entries remaining in it.
        return "A shuffled shoe containing "+ str(len(self.shuffled_deck)) + " cards."
    
    def __del__(self):
        print("The current deck shoe has been removed from the game.")
        return True
    
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
        This method allows the programmer to print out all of the attributes, including
        class order attributes, for the defined object to help debug code. It is not 
        normally used with running program.
        '''
        print("Class Order Attributes:")
        print("Ranks: ", self.ranks)
        print("Suits: ", self.suits)
        print("Number of cards in Shoe: ", self.length)
        print("Shuffled_Shoe: ", self.shuffled_deck)
        return