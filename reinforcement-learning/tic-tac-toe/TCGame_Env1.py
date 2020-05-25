from gym import spaces
import numpy as np
import random
from itertools import groupby
from itertools import product

class TicTacToe:
    def __init__(self):
        # Initialize for a 3*3 TicTacToe board
        self.board = [0]*9
        
        # RL is considered as player 1 and as per the problem statement, it has options [1, 3, 5, 7, 9]
        self.player1 = None
        # Environment is considered as player 2 and as per the problem statement, it has options [2, 4, 6, 8]
        self.player2 = None

    # Reset board
    def reset_board(self):
        self.board = [0] * 9

    # Check if board is completed (won)
    def calc_reward(self):
        # Check rows
        for i in range(3):
            if (self.board[i * 3] + self.board[i * 3 + 1] + self.board[i * 3 + 2]) == 15:
                return 1.0, True
        
        # Check columns
        for i in range(3):
            if (self.board[i + 0] + self.board[i + 3] + self.board[i + 6]) == 15:
                return 1.0, True
        
        # Check diagonals
        if (self.board[0] + self.board[4] + self.board[8]) == 15:
            return 1.0, True
        if (self.board[2] + self.board[4] + self.board[6]) == 15:
            return 1.0, True

        # If board is filled with no result, it is Draw
        if not any(space == 0 for space in self.board):
            return 0.0, True

        return 0.0, False

    # Get the list of possible actions in a given state
    def find_blank_spots(self):
        blank_spots =  [spots + 1 for spots, spot in enumerate(self.board) if spot == 0]
        return blank_spots

    # Pick an empty spot based upon player1/player2
    def pick_spot(self, isX):
        # Shuffle the remaining spots for a given player and randomly pick one
		# Player 1 (RL)
        if(isX):
            self.player1.options = random.sample(self.player1.options, len(self.player1.options))
            return self.player1.options.pop()
        # Player 2 (Env)
        else:
            self.player2.options = random.sample(self.player2.options, len(self.player2.options))
            return self.player2.options.pop()

    # Take a step and process reward
	# Here, "reward" value is a binary 0 or 1 and "done" is True if game ends (win, lose, draw) and False otherwise
    def step(self, isX, move):
        self.board[move-1]= self.pick_spot(isX)
        reward, done = self.calc_reward()
        return reward, done

    # Start training
    def start_training(self, player1, player2, iterations, odd=True, verbose = False):
        self.player1=player1
        self.player2=player2
        print ("Training Started")

        for i in range(iterations):
            if verbose: print("trainining ", i)
            self.player1.begin_game()
            self.player2.begin_game()
            self.reset_board()
            done = False

            # As per the problem statement, RL player will always start the game
            isX = odd
            while not done:
                if isX:
                    move = self.player1.epslion_greedy(i, self.board, self.find_blank_spots())
                else:
                    move = self.player2.epslion_greedy(i, self.board, self.find_blank_spots())

                # Take a step
                reward, done = self.step(isX, move)

                if (reward == 1):  # One of the players have won the game. As per the problem statement, a reward of 10 is awarded for the RL agent winning the game and -10 otherwise
                    if (isX):
                        self.player1.update_Q(10, self.board, self.find_blank_spots())
                        self.player2.update_Q(-10, self.board, self.find_blank_spots())
                    else:
                        self.player1.update_Q(-10, self.board, self.find_blank_spots())
                        self.player2.update_Q(10, self.board, self.find_blank_spots())
                elif (done == False):  # A move is made and the game did not end yet. Reward -1 for the move
                    if (isX):
                        self.player1.update_Q(-1, self.board, self.find_blank_spots())

                else: #(reward == 0):  Game is drawn (no more blank spots left)
                    self.player1.update_Q(reward, self.board, self.find_blank_spots())
                    self.player2.update_Q(reward, self.board, self.find_blank_spots())


                isX = not isX  # switch players to take their turn alternatively
            self.player1.deltas.append(self.player1.biggest_change)
            self.player2.deltas.append(self.player2.biggest_change)
        print ("Training Completed")

    # Save Q states for both players
    def save_states(self):
        self.player1.save_Q("oddPolicy")
        self.player2.save_Q("evenPolicy")

    # Get saved Q states for both players
    def get_Q(self):
        return self.player1.Q, self.player2.Q


