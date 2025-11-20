'''
Dataset From: https://www.kaggle.com/datasets/rohanrao/sudoku?resource=download
'''

from Sudoku import Sudoku
import csv, time
from GraphBased.dSaturSolver import solve_sudoku_dsatur
import AlgX

def make_dataset(csv_path, limit = None):
    pairs = []
    with open(csv_path, newline = '') as f:     
        for i, row in enumerate(csv.DictReader(f)):
            if limit is not None and i >= limit: break
            puzzle = Sudoku(3)
            puzzle_string = row['puzzle'].strip()
            puzzle.fillFromString(puzzle_string)
            pairs.append((puzzle, row['solution'].strip(), puzzle_string))
    return pairs

def check_one(item, solver):
    _, solution, puzzle_string = item
    puzzle = Sudoku(3)
    puzzle.fillFromString(puzzle_string)
    start_time = time.perf_counter()
    solver(puzzle)
    time_length = time.perf_counter() - start_time
    got = ''.join(str(puzzle.board[r][c]) for r in range(puzzle.length) for c in range(puzzle.length))
    return (got == solution), time_length, got

def check_all(pairs, solver):
    results = [check_one(item, solver) for item in pairs]
    n = len(results)
    total = sum(time_length for _, time_length, _ in results)
    correct = sum(correct for correct, _, _ in results)
    return results, total, correct

'''
DSatur Example:

pairs = make_dataset("sudoku.csv", limit = 100)
_, total, _ = check_all(pairs, lambda S: solve_sudoku_dsatur(S))
print(f'Total Time: {total}')
'''