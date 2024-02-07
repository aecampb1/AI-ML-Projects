"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    # Returns starting state of the board.
    return [[EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]


# todo
def player(board):
    # Returns player who has the next turn on a board.
    # count x and o on board
    count_X = sum(row.count(X) for row in board)
    count_O = sum(row.count(O) for row in board)

    if count_X > count_O:
        return O
    else:
        return X

# todo
def actions(board):
    # Returns set of all possible actions (i, j) available on the board.
    # Check for empty cells in the board
    possible_actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_actions.add((i, j))
    return possible_actions

# todo
def result(board, action):
    # Returns the board that results from making move (i, j) on the board.
    # make a copy of the board, unpack tuple
    new_board = copy.deepcopy(board)
    i, j = action

    # check if action valid
    if not (0 <= i < 3) or not (0 <= j < 3) or new_board[i][j] != EMPTY:
        raise ValueError("Invalid Action")

    new_board[i][j] = player(board)
    return new_board

# todo
def winner(board):
    # Returns the winner of the game, if there is one.
    # If X has won, returns X
    # If O has won, returns O
    # If neither has won, returns None

    # check rows
    for row in board:
        if row.count("X") == 3:
            return "X"
        elif row.count("O") == 3:
            return "O"

    # check columns
    for col in range(3):
        if all(board[row][col] == "X" for row in range(3)):
            return "X"
        elif all(board[row][col] == "O" for row in range(3)):
            return "O"

    # check diagonals
    if all(board[i][i] == "X" for i in range(3)) or all(
        board[i][2 - i] == "X" for i in range(3)
    ):
        return "X"
    elif all(board[i][i] == "O" for i in range(3)) or all(
        board[i][2 - i] == "O" for i in range(3)
    ):
        return "O"

    # if no winner
    return None


# todo
def terminal(board):
    # Returns True if game is over, False otherwise.
    # Check for winner
    if winner(board) is not None:
        return True
    # check for full board
    if all(cell is not None for row in board for cell in row):
        return True

    # if came incomplete
    return False


# todo
def utility(board):
    # Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    winner_result = winner(board)
    if winner_result == "X":
        return 1
    elif winner_result == "O":
        return -1
    else:
        return 0


# todo
def minimax(board):
    # Returns the optimal action for the current player on the board.
    # Return none if terminal board
    if terminal(board):
        return None

    current_player = player(board)
    if current_player == "X":
        _, action = max_value(board, float("-inf"), float("inf"))
    else:
        _, action = min_value(board, float("-inf"), float("inf"))

    return action


def max_value(board, alpha, beta):
    if terminal(board):
        return utility(board), None

    v = float("-inf")
    best_action = None

    for action in actions(board):
        value, _ = min_value(result(board, action), alpha, beta)
        if value > v:
            v = value
            best_action = action
        alpha = max(alpha, v)
        if beta <= alpha:
            break

    return v, best_action


def min_value(board, alpha, beta):
    if terminal(board):
        return utility(board), None

    v = float("inf")
    best_action = None

    for action in actions(board):
        value, _ = max_value(result(board, action), alpha, beta)
        if value < v:
            v = value
            best_action = action
        beta = min(beta, v)
        if beta <= alpha:
            break

    return v, best_action
