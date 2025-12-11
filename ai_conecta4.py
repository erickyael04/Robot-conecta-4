import numpy as np
import random
import math

# --------------------
# Configuración / constantes
# --------------------
ROWS = 6
COLS = 7
EMPTY = 0
WINDOW_LENGTH = 4
DEFAULT_DEPTH = 6
WIN_SCORE = 10**9

# --------------------
# Funciones de tablero
# --------------------

def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    col = int(col)
    # en nuestra representación asumimos fila 0 = top; la posición superior (fila ROWS-1)
    # indica si la columna está llena (usa misma convención que tu código previo)
    return board[ROWS - 1][col] == EMPTY


def get_next_open_row(board, col):
    col = int(col)
    # devuelve la primera fila disponible desde abajo (fila 0 = top)
    for r in range(ROWS):
        if board[r][col] == EMPTY:
            return r
    return None


def get_valid_locations(board):
    return [c for c in range(COLS) if is_valid_location(board, c)]


def winning_move(board, piece):
    # Horizontal
    for c in range(COLS - 3):
        for r in range(ROWS):
            if all(board[r][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True
    # Vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r + i][c] == piece for i in range(WINDOW_LENGTH)):
                return True
    # Diagonal (\)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True
    # Diagonal (/)
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r - i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True
    return False

# --------------------
# Heurística
# --------------------

def evaluate_window(window, piece):
    score = 0
    opp_piece = 1 if piece == 2 else 2

    count_piece = window.count(piece)
    count_opp = window.count(opp_piece)
    count_empty = window.count(EMPTY)

    if count_piece == 4:
        score += 10000
    elif count_piece == 3 and count_empty == 1:
        score += 150
    elif count_piece == 2 and count_empty == 2:
        score += 10

    # Bloqueos del oponente
    if count_opp == 3 and count_empty == 1:
        score -= 300
    elif count_opp == 2 and count_empty == 2:
        score -= 10

    return score


def score_position(board, piece):
    score = 0
    # Prioriza centro
    center_col = COLS // 2
    center_array = [int(i) for i in list(board[:, center_col])]
    center_count = center_array.count(piece)
    score += center_count * 6

    # Horizontal
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLS - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Vertical
    for c in range(COLS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Diagonales (\)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [int(board[r + i][c + i]) for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Diagonales (/)
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [int(board[r - i][c + i]) for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

# --------------------
# Utilidad: si con un movimiento ganas
# --------------------

def try_move_and_win(board, col, piece):
    if not is_valid_location(board, col):
        return False
    row = get_next_open_row(board, col)
    if row is None:
        return False
    b_copy = board.copy()
    drop_piece(b_copy, row, col, piece)
    return winning_move(b_copy, piece)

# --------------------
# Ordenamiento de movimientos por heurística (center first)
# --------------------

def order_moves(board, valid_locations, piece):
    scores = []
    for col in valid_locations:
        row = get_next_open_row(board, col)
        if row is None:
            s = -9999
        else:
            b_copy = board.copy()
            drop_piece(b_copy, row, col, piece)
            s = score_position(b_copy, piece)
            s -= abs(col - (COLS // 2)) * 1
        scores.append((s, col))
    scores.sort(reverse=True, key=lambda x: x[0])
    return [col for _, col in scores]

# --------------------
# Minimax con poda alfa-beta
# --------------------

def minimax(board, depth, alpha, beta, maximizingPlayer, ai_piece, player_piece):
    valid_locations = get_valid_locations(board)
    terminal = (winning_move(board, ai_piece) or winning_move(board, player_piece) or len(valid_locations) == 0)

    if depth == 0 or terminal:
        if terminal:
            if winning_move(board, ai_piece):
                return (None, WIN_SCORE + depth)
            elif winning_move(board, player_piece):
                return (None, -WIN_SCORE - depth)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, ai_piece))

    if maximizingPlayer:
        value = -math.inf
        best_col = random.choice(valid_locations) if valid_locations else None
        ordered = order_moves(board, valid_locations, ai_piece)
        for col in ordered:
            row = get_next_open_row(board, col)
            if row is None:
                continue
            b_copy = board.copy()
            drop_piece(b_copy, row, col, ai_piece)
            if winning_move(b_copy, ai_piece):
                return col, WIN_SCORE + depth
            _, new_score = minimax(b_copy, depth - 1, alpha, beta, False, ai_piece, player_piece)
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
    else:
        value = math.inf
        best_col = random.choice(valid_locations) if valid_locations else None
        ordered = order_moves(board, valid_locations, player_piece)
        for col in ordered:
            row = get_next_open_row(board, col)
            if row is None:
                continue
            b_copy = board.copy()
            drop_piece(b_copy, row, col, player_piece)
            if winning_move(b_copy, player_piece):
                return col, -WIN_SCORE - depth
            _, new_score = minimax(b_copy, depth - 1, alpha, beta, True, ai_piece, player_piece)
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

# --------------------
# Función pública requerida: devuelve solo la columna (int)
# --------------------

def get_best_move(board, color_robot, color_human, depth=DEFAULT_DEPTH):
    """
    Devuelve (int) la columna donde el robot debe jugar (0..6).
    - board: numpy.ndarray 6x7, fila0 = top
    - color_robot: 1 o 2
    - color_human: 1 o 2
    - depth: profundidad del minimax
    """
    if not isinstance(board, np.ndarray):
        raise ValueError("board debe ser numpy.ndarray 6x7")
    if board.shape != (ROWS, COLS):
        raise ValueError("board shape debe ser (6,7)")

    valid = get_valid_locations(board)
    if not valid:
        return None

    # 1) Intentar ganar inmediatamente
    for c in valid:
        if try_move_and_win(board, c, color_robot):
            return int(c)

    # 2) Bloquear al humano si puede ganar
    for c in valid:
        if try_move_and_win(board, c, color_human):
            return int(c)

    # 3) Usar minimax
    col, _ = minimax(board.copy(), depth, -math.inf, math.inf, True, color_robot, color_human)
    if col is None or col not in valid:
        ordered = order_moves(board, valid, color_robot)
        return int(ordered[0]) if ordered else int(random.choice(valid))
    return int(col)

# si se importa directamente, nada se ejecuta automáticamente
if __name__ == "__main__":
    # pequeño test rápido
    b = np.zeros((6,7), dtype=int)
    print("Best move on empty board:", get_best_move(b, color_robot=1, color_human=2, depth=4))


def check_winner(board):
    """
    Revisa si hay un ganador en la matriz de Conecta 4.
    Retorna:
        1 -> si gana amarillo
        2 -> si gana rojo
        0 -> si no hay ganador
    """

    ROWS = 6
    COLS = 7

    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            line = board[r, c:c + 4]
            if line[0] != 0 and np.all(line == line[0]):
                return int(line[0])

    # Vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            line = board[r:r + 4, c]
            if line[0] != 0 and np.all(line == line[0]):
                return int(line[0])

    # Diagonal ↘
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            line = np.array([board[r+i, c+i] for i in range(4)])
            if line[0] != 0 and np.all(line == line[0]):
                return int(line[0])

    # Diagonal ↗
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            line = np.array([board[r-i, c+i] for i in range(4)])
            if line[0] != 0 and np.all(line == line[0]):
                return int(line[0])

    return 0  # No winner
