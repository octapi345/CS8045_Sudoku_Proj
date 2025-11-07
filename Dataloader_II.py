import csv, time, os
from tqdm import tqdm
from Sudoku import Sudoku
from GraphBased.dSaturSolver import solve_sudoku_dsatur
import SimAl
import AlgX

FILES = {
    "size2.csv": 2,
    "size3.csv": 3,
    "size4.csv": 4,
    "size5.csv": 5,
}
LIMIT = None

def _char_to_val(ch: str) -> int:
    ch = ch.strip()
    if not ch or ch in {'0', '.'}:
        return 0
    if ch.isdigit():
        return int(ch)
    u = ch.upper()
    if 'A' <= u <= 'Z':
        return 10 + (ord(u) - ord('A'))
    raise ValueError(f"Bad symbol '{ch}'")

def _load_into_sudoku(s: Sudoku, raw: str) -> None:
    N = s.length
    if len(raw) != N * N:
        raise ValueError(f"Expected {N*N} chars, got {len(raw)}")
    p = 0
    for i in range(N):
        for j in range(N):
            v = _char_to_val(raw[p])
            s.board[i][j] = v
            s.fixed[i][j] = (v != 0)
            p += 1

def load_puzzles(csv_path: str, size: int, limit: int | None):
    puzzles, bad = [], 0
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            if limit and idx >= limit:
                break
            try:
                s = Sudoku(size)
                _load_into_sudoku(s, row["puzzle"].strip())
                puzzles.append(s)
            except Exception:
                bad += 1
    return puzzles, bad

def _clone_sudoku(s: Sudoku) -> Sudoku:
    c = Sudoku(s.size)
    c.board = [r[:] for r in s.board]
    c.fixed = [r[:] for r in s.fixed]
    return c

def run_batch_two_solvers(puzzles, desc: str):
    ds_total = ax_total = 0.0
    ds_solved = ax_solved = 0
    for S0 in tqdm(puzzles, desc=desc, unit="puzzle"):
        S_ds = _clone_sudoku(S0)
        t0 = time.perf_counter()
        ok_ds, _ = solve_sudoku_dsatur(S_ds)
        ds_total += time.perf_counter() - t0
        if ok_ds and S_ds.isComplete():
            ds_solved += 1
        S_ax = _clone_sudoku(S0)
        t1 = time.perf_counter()
        AlgX.run(S_ax)
        ax_total += time.perf_counter() - t1
        if S_ax.isComplete():
            ax_solved += 1
    n = len(puzzles)
    return ds_solved, ds_total, ax_solved, ax_total, n

def run_batch_algx(puzzles, desc: str):
    ax_total = 0.0
    ax_solved = 0
    for S0 in tqdm(puzzles, desc=desc, unit="puzzle"):
        S_ax = _clone_sudoku(S0)
        t1 = time.perf_counter()
        AlgX.run(S_ax)
        ax_total += time.perf_counter() - t1
        if S_ax.isComplete():
            ax_solved += 1
    n = len(puzzles)
    return ax_solved, ax_total, n

def run_batch_simanneal(puzzles, desc: str):
    sa_total = 0.0
    sa_solved = 0
    for S0 in tqdm(puzzles, desc=desc, unit="puzzle"):
        S_sa = _clone_sudoku(S0)
        t1 = time.perf_counter()

        solver = SimAl.SimulatedAnnealing(S_sa)
        solver.solve(display=False)

        sa_total += time.perf_counter() - t1
        if S_sa.isComplete():
            sa_solved += 1
    n = len(puzzles)
    return sa_solved, sa_total, n


if __name__ == "__main__":
    g_ds_solved = g_ax_solved = g_ds_time = g_ax_time = g_count = 0
    g_sa_solved = g_sa_time = 0


    for fname, size in FILES.items():
        if not os.path.exists(fname):
            print(f"Skipping {fname} (not found)")
            continue
        puzzles, bad = load_puzzles(fname, size, LIMIT)
        print(f"{fname}: loaded {len(puzzles)} puzzles (skipped {bad})")

        desc = f"Solving {fname} (n={size})"
        #ax_solved, ax_total, n = run_batch_algx(puzzles, desc)
        ds_solved, ds_total, ax_solved, ax_total, n = run_batch_two_solvers(puzzles, desc)
        sa_solved, sa_total, _ = run_batch_simanneal(puzzles, desc + " [SA]")

        
        g_ds_solved += ds_solved
        g_ax_solved += ax_solved
        g_ds_time += ds_total
        g_ax_time += ax_total
        g_sa_solved += sa_solved
        g_sa_time += sa_total

        g_count += n

        N = size * size
        print(f"(n={size}, {N}x{N})")
        print(f"  DSatur: {ds_solved}/{n} | {ds_total:.3f}s | {ds_total/n:.4f}s avg")
        print(f"  AlgX  : {ax_solved}/{n} | {ax_total:.3f}s | {ax_total/n:.4f}s avg\n")
        print(f"  SimAnn: {sa_solved}/{n} | {sa_total:.3f}s | {sa_total/n:.4f}s avg\n")


    if g_count:
        print("Overall:")
        print(f"  DSatur: {g_ds_solved}/{g_count} | {g_ds_time:.3f}s | {g_ds_time/g_count:.4f}s avg")
        print(f"  AlgX  : {g_ax_solved}/{g_count} | {g_ax_time:.3f}s | {g_ax_time/g_count:.4f}s avg")
        print(f"  SimAnn: {g_sa_solved}/{g_count} | {g_sa_time:.3f}s | {g_sa_time/g_count:.4f}s avg")
