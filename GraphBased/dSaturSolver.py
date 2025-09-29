from Sudoku import Sudoku  
from GraphBased.SudokuGraph import are_neighbors

def solve_sudoku_dsatur(s: Sudoku) -> tuple[bool, int]:
    n, N = s.size, s.length
    V = N * N
    steps = 0

    # Current assignments
    colors: dict[int, int] = {r * N + c: s.board[r][c] for r in range(N) for c in range(N) if s.fixed[r][c]}

    def select_vertex() -> int | None:
        best_v, best_key = None, (-1, -1)
        for v in range(V):
            if v in colors: 
                continue
            sat = len({colors[j] for j in colors if are_neighbors(v, j, N, n)})
            key = (sat, -v)
            if key > best_key:
                best_key, best_v = key, v
        return best_v

    def domain(v: int) -> list[int]:
        used = {colors[j] for j in colors if are_neighbors(v, j, N, n)}
        return [d for d in range(1, N + 1) if d not in used]

    def search() -> bool:
        nonlocal steps
        v = select_vertex()
        if v is None:
            return True # All cells have an assignment
        for d in domain(v):
            steps += 1 # Every cell check is a step
            if any(colors.get(j) == d and are_neighbors(v, j, N, n) for j in colors):
                continue # Is our assignment consistent?
            colors[v] = d
            if search():
                return True
            del colors[v] # backtrack
        return False

    ok = search()
    if not ok:
        return False, steps

    # Solution
    for i, d in colors.items():
        r, c = divmod(i, N)
        s.board[r][c] = d
        s.fixed[r][c] = True
    return True, steps