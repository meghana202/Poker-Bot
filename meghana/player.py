'''
Simple example pokerbot, written in Python.
'''
import random

from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import eval7

class Player(Bot):

    def __init__(self):
        pass

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        #game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        #round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        #my_cards = round_state.hands[active]  # your cards
        #big_blind = bool(active)  # True if you are the big blind
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        #previous_state = terminal_state.previous_state  # RoundState before payoffs
        #street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        #my_cards = previous_state.hands[active]  # your cards
        #opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        pass

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''

        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        # my_cards = round_state.hands[active]  # your cards
        # board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        # opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        # continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        # my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        # opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
    
        big_blind = bool(active)
        bb_amount = 0
        if big_blind == True: bb_amount = my_pip
        else: bb_amount = opp_pip

        legal_actions = round_state.legal_actions()
        my_cards = round_state.hands[active]

        actions, strength = self.card_analysis_preflop(my_cards)
        for action in actions:
            if action in legal_actions:
                if action == RaiseAction:
                    return RaiseAction(str(calculate_raise_size(strength, my_stack, bb_amount)))
                return action()
            
        action = random.choice(tuple(legal_actions))
        if action is RaiseAction:
            min_raise, max_raise = round_state.raise_bounds()
            bet_amt = random.randint(min_raise, max_raise)
            return RaiseAction(bet_amt)
        return action()

    def card_analysis_preflop(self, my_cards):
        
        card1_rank, card2_rank= my_cards[0][0], my_cards[1][0]
        card1_suit, card2_suit = my_cards[0][1], my_cards[1][1]
        ranks = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10}  
        premium_ranks = {'A', 'K', 'Q', 'J'}

        rank1 = ranks[card1_rank] if card1_rank in ranks else int(card1_rank)
        rank2 = ranks[card2_rank] if card2_rank in ranks else int(card2_rank)
    
        suited = (card1_suit == card2_suit)
    
        hand_strength = None
    
        if rank1 == rank2 and card1_rank in premium_ranks:
            hand_strength = "Premium"
        elif abs(rank1 - rank2) == 0 and rank1 >= 10:
            hand_strength = "Very Strong"
        elif abs(rank1 - rank2) <= 2 and suited:
            hand_strength = "Strong"
        elif abs(rank1 - rank2) <= 4 and (suited or rank1 == rank2):
            hand_strength = "Good"
        else:
            hand_strength = "Playable"

        tiers_actions = {
        "Premium": [RaiseAction, CallAction, FoldAction],
        "Very Strong": [RaiseAction, CallAction, FoldAction],
        "Strong": [RaiseAction, CallAction, FoldAction],
        "Good": [RaiseAction, CallAction, FoldAction],
        "Playable":[CallAction, FoldAction]
        }

        return tiers_actions[hand_strength], hand_strength
                
def calculate_raise_size(hand_strength, stack_size, big_blind):
    raise_size = 0

    if hand_strength == "Premium":
        raise_size = 4 * big_blind
    elif hand_strength == "Very Strong":
        raise_size = 3.5 * big_blind
    elif hand_strength == "Strong":
        raise_size = 3 * big_blind
    elif hand_strength == "Good":
        raise_size = 2.5 * big_blind
    
    raise_fraction = 0.1  
    raise_size += raise_fraction * stack_size
    
    return int(raise_size)

if __name__ == '__main__':
    run_bot(Player(), parse_args())
