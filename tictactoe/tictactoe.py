"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    board: list[list[str | None]] = board
    n = 0
    for row in board:
        for i in row:
            if i != None:
                n += 1

    return X if n % 2 == 0 else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    a = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == None:
                a.add((i, j))
    return a


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    if action not in actions(board=board):
        raise "action invalid"

    p = player(board=board)

    i, j = action
    b = [[item for item in row] for row in board]
    b[i][j] = p
    return b


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    def win(p: list):
        assert len(p) >= 2
        for i in range(1, len(p)):
            u, v = p[i-1], p[i]
            if board[u[0]][u[1]] == None or board[v[0]][v[1]] == None:
                return False
            if board[u[0]][u[1]] != board[v[0]][v[1]]:
                return False

        return True

    j = [
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)],
    ]

    for p in j:
        if win(p):
            return board[p[0][0]][p[0][1]]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board=board) != None:
        return True

    if all([all(row) for row in board]):
        return True

    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    p = winner(board=board)
    if p == X:
        return 1
    if p == O:
        return -1

    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    
    if terminal(board=board):
        return None

    acts = list(actions(board=board))
    f = max if X == player(board=board) else min

    scores = [
        score(
            result(board=board, action=a)
        )
        for a in acts
    ]

    best = f(scores)
    for i in range(len(acts)):
        if scores[i] == best:
            return acts[i]
    
    raise "unreachable"

def score(board):
    if terminal(board=board):
        w = winner(board=board)
        if w != None:
            return 1 if w == X else -1
        
        return 0

    acts = actions(board=board)
    f = max if X == player(board=board) else min
    nexts = [
        score(result(board=board, action=a))
            for a in acts
    ]

    return f(nexts)