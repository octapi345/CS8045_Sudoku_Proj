import numpy as np
import math, random

all_digits = {
    2: list(range(1, 5)),
    3: list(range(1, 10)),
    4: list(range(1, 17)),
    5: list(range(1, 26))
}

def _to_int(val):
    if isinstance(val, (int, np.integer)):
        return int(val)
    if isinstance(val, str):
        val = val.strip().upper()
        if not val or val in {'0', '.'}:
            return 0
        if val.isdigit():
            return int(val)
        if 'A' <= val <= 'Z':
            return 10 + (ord(val) - ord('A'))
    raise ValueError(f"Bad symbol '{val}'")

class SimulatedAnnealing:
    def __init__(self, sudoku_init, t_init=5.0, decay=0.99995, max_plateau=15000, max_reheats=5):
        self.sudoku = sudoku_init
        self.grid = np.array(sudoku_init.board)
        self.grid = np.vectorize(_to_int)(self.grid)
        self.fixed = np.array(sudoku_init.fixed)
        self.length = sudoku_init.length
        self.n = int(math.sqrt(self.length))

        # annealing parameters
        self.T_init = t_init
        self.T = self.T_init
        self.decay = decay
        self.N_plateau = max_plateau
        self.max_reheats = max_reheats

        # tracking variables
        self.iters = 0
        self.iters_since_improvement = 0
        self.reheats = 0
        self.best_error = float('inf')

        # initial population
        self.populate_strict_boxes()
        self.error_count = self.compute_total_errors()

    def populate_strict_boxes(self):
        """Fill each n x n box with all numbers 1..N exactly once."""
        for br in range(self.n):
            for bc in range(self.n):
                numbers = list(range(1, self.length + 1))
                # Remove fixed numbers
                for r in range(br*self.n, (br+1)*self.n):
                    for c in range(bc*self.n, (bc+1)*self.n):
                        if self.fixed[r, c]:
                            if self.grid[r, c] in numbers:
                                numbers.remove(self.grid[r, c])
                # Fill remaining positions
                positions = [(r, c) for r in range(br*self.n, (br+1)*self.n)
                             for c in range(bc*self.n, (bc+1)*self.n)
                             if not self.fixed[r, c]]
                random.shuffle(positions)
                random.shuffle(numbers)
                for (r, c), val in zip(positions, numbers):
                    self.grid[r, c] = val

    def compute_total_errors(self):
        """Count duplicates in rows and columns only (boxes are correct)."""
        errors = 0
        for i in range(self.length):
            row = self.grid[i, :]
            col = self.grid[:, i]
            errors += len(row) - len(np.unique(row))
            errors += len(col) - len(np.unique(col))
        return errors

    def compute_delta_errors(self, r1, c1, r2, c2):
        """Compute delta in total errors if swapping two cells."""
        before = self.compute_total_errors()
        self.grid[r1, c1], self.grid[r2, c2] = self.grid[r2, c2], self.grid[r1, c1]
        after = self.compute_total_errors()
        self.grid[r1, c1], self.grid[r2, c2] = self.grid[r2, c2], self.grid[r1, c1]
        return after - before

    def swap(self):
        """Swap two non-fixed cells within the same box."""
        # pick a random box
        br, bc = random.randint(0, self.n-1), random.randint(0, self.n-1)
        candidates = [(r, c) for r in range(br*self.n, (br+1)*self.n)
                              for c in range(bc*self.n, (bc+1)*self.n)
                              if not self.fixed[r, c]]
        if len(candidates) < 2:
            return False
        (r1, c1), (r2, c2) = random.sample(candidates, 2)

        delta = self.compute_delta_errors(r1, c1, r2, c2)
        accepted = False

        if delta < 0 or random.random() < math.exp(-delta / max(self.T, 1e-9)):
            self.grid[r1, c1], self.grid[r2, c2] = self.grid[r2, c2], self.grid[r1, c1]
            self.error_count += delta
            accepted = True
            self.iters_since_improvement = 0
        else:
            self.iters_since_improvement += 1

        self.T *= self.decay
        self.iters += 1
        return accepted

    def perturb_low_error_plateau(self):
        """Reheat the system when stuck on low errors."""
        if self.reheats >= self.max_reheats:
            return
        self.T = max(0.2, self.T_init)  # modest reheat
        self.iters_since_improvement = 0
        self.reheats += 1
        print(f"[Reheat {self.reheats}] Temp reset to {self.T:.4f}, Errors={self.error_count}")

    def solve(self, display=False, max_iters=10**7):
        min_T = 0.01  # temperature floor
        while self.error_count > 0 and self.iters < max_iters:
            self.swap()

            # track best error
            if self.error_count < self.best_error:
                self.best_error = self.error_count
                self.iters_since_improvement = 0
            else:
                self.iters_since_improvement += 1

            # reheat if plateau
            if (self.iters_since_improvement >= self.N_plateau and
                self.reheats < self.max_reheats and
                self.error_count > 0):
                self.perturb_low_error_plateau()

            # decay temperature
            self.T = max(self.T * self.decay, min_T)
            
            if display and self.iters % 5000 == 0:
                print(f"Iter {self.iters}, Errors {self.error_count}, Temp {self.T:.4f}")

        self.sudoku.board = self.grid.tolist()
        print(f"Solved in {self.iters} iterations, {self.reheats} reheats.")
        return self.iters
