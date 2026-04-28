import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pk'))

from tic_tac_toe import TicTacToeGame

def main():
    game = TicTacToeGame()
    game.run()

if __name__ == "__main__":
    main()
