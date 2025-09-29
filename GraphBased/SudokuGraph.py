from Sudoku import Sudoku

SudokuGraph = tuple[int, tuple[int, ...]]

def are_neighbors(i: int, j: int, N: int, n: int) -> bool:
    if i == j:
        return False
    r1, c1 = divmod(i, N)
    r2, c2 = divmod(j, N)
    return (r1 == r2) or (c1 == c2) or ((r1 // n == r2 // n) and (c1 // n == c2 // n)) # Same row, column, box

def sudoku_to_graph(s: Sudoku) -> SudokuGraph:
    labels = tuple(s.board[r][c] for r in range(s.length) for c in range(s.length))
    return (s.size, labels)