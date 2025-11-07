import numpy as np
from collections import Counter
import math, random

all_digits = {
    2: list(range(1, 5)),
    3: list(range(1, 10)),
    4: [str(x) for x in list(range(1, 10)) + list("ABCDEFG")],
    5: [str(x) for x in list(range(1, 10)) + list("ABCDEFGHIJKLMNO")]
}

def available_numbers(n, taken):
    """Return remaining numbers available given filled cells."""
    master = all_digits[n]
    master_arr = np.array(master * (n**2))
    clue_arr = taken
    clueCount = Counter(clue_arr)
    fullCount = Counter(master_arr)
    remainCount = fullCount - clueCount
    result = np.array([val for val, cnt in remainCount.items() for _ in range(cnt)])
    return result


class SimulatedAnnealing:
    def __init__(self, sudoku_init, t_sched=None, t_init=10):
        self.sudoku = sudoku_init
        self.grid = np.array(sudoku_init.board)
        self.fixed = np.array(sudoku_init.fixed)
        self.length = sudoku_init.length  # total grid size (e.g., 9, 16, 25)
        self.n = int(math.sqrt(self.length))  # subgrid dimension (3, 4, 5)
        
        self.possible_numbers = available_numbers(self.n, self.grid.flatten())
        self.populate()
        
        self.T_init = t_init
        self.T = self.T_init
        self.iters = 1
        self.decay = 0.9999 if t_sched is None else t_sched
        self.error_count = 99999999
        self.T_min = 1e-7
        
        self.num_goodswaps = 0
        self.num_badswaps = 0
        self.num_rejectedswaps = 0
        
    def populate(self):
        """Fill each subgrid with random non-fixed values."""
        for box_row in range(self.n):
            for box_col in range(self.n):
                numbers = set(all_digits[self.n])
                for r in range(self.n * box_row, self.n * box_row + self.n):
                    for c in range(self.n * box_col, self.n * box_col + self.n):
                        if self.fixed[r][c]:
                            numbers.discard(self.grid[r][c])
                for r in range(self.n * box_row, self.n * box_row + self.n):
                    for c in range(self.n * box_col, self.n * box_col + self.n):
                        if not self.fixed[r][c]:
                            self.grid[r][c] = numbers.pop()
                        
    def swap(self):
        """Swap two unfixed cells in a random subgrid and apply simulated annealing acceptance."""
        box = random.randint(0, self.n**2 - 1)
        row_start, col_start = self.n * (box // self.n), self.n * (box % self.n)
        candidates = [
            (r, c)
            for r in range(row_start, row_start + self.n)
            for c in range(col_start, col_start + self.n)
            if not self.fixed[r][c]
        ]
        if len(candidates) < 2:
            return self.swap()
        (r1, c1), (r2, c2) = random.sample(candidates, 2)
        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
        
        currErr = self.error_count
        newErr = self.sudoku.numErrors(grid=self.grid.tolist())
        delta = newErr - currErr
        
        if delta < 0:
            self.sudoku.board = self.grid.tolist()
            self.error_count = newErr
            self.num_goodswaps += 1
        else:
            prob = math.exp(-delta / self.T)
            if random.random() < prob:
                self.sudoku.board = self.grid.tolist()
                self.error_count = newErr
                self.num_badswaps += 1
            else:
                self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
                self.num_rejectedswaps += 1
        
        self.iters += 1
        self.T *= self.decay

    def solve(self, display=False):
        while self.error_count > 0:
            self.swap()
            if self.iters % 1000 == 0 and display:
                print(f"Iter {self.iters}, Errors {self.error_count}, Temp {self.T:.4f}")
            if self.iters % 20000 == 0:
                self.T *= 1.05
            if self.iters % 80000 == 0:
                self.T = 5
        #print(f"Solved in {self.iters} iterations.")
        return self.iters
