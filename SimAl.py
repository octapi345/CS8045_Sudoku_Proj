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
    def __init__(self, sudoku_init, t_init=5.0, decay=0.99995, max_plateau=5000, max_reheats=5):
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
        self.populate_smart()
        self.error_count = self.compute_total_errors()

    def populate_smart(self):
        for box_row in range(self.n):
            for box_col in range(self.n):
                numbers = set(all_digits[self.n])
                for r in range(box_row*self.n, (box_row+1)*self.n):
                    for c in range(box_col*self.n, (box_col+1)*self.n):
                        if self.fixed[r][c]:
                            numbers.discard(self.grid[r][c])
                positions = [(r, c) for r in range(box_row*self.n, (box_row+1)*self.n)
                                      for c in range(box_col*self.n, (box_col+1)*self.n)
                                      if not self.fixed[r][c]]
                random.shuffle(positions)
                for r, c in positions:
                    valid_numbers = [num for num in numbers
                                     if num not in self.grid[r, :]
                                     and num not in self.grid[:, c]
                                     and num not in self.grid[box_row*self.n:(box_row+1)*self.n,
                                                             box_col*self.n:(box_col+1)*self.n]]
                    chosen = random.choice(valid_numbers) if valid_numbers else random.choice(list(numbers)) if numbers else random.randint(1, self.length)
                    self.grid[r, c] = chosen
                    numbers.discard(chosen)

    def compute_total_errors(self):
        errors = 0
        for i in range(self.length):
            row = self.grid[i, :]
            col = self.grid[:, i]
            errors += len(row) - len(np.unique(row))
            errors += len(col) - len(np.unique(col))
        return errors

    def compute_delta_errors(self, r1, c1, r2, c2):
        before = self.sudoku.numErrors(self.grid)
        self.grid[r1, c1], self.grid[r2, c2] = self.grid[r2, c2], self.grid[r1, c1]
        after = self.sudoku.numErrors(self.grid)
        self.grid[r1, c1], self.grid[r2, c2] = self.grid[r2, c2], self.grid[r1, c1]
        return after - before

    def swap(self):
        candidates = [(r, c) for r in range(self.length)
                      for c in range(self.length)
                      if not self.fixed[r][c]]
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
        # Identify all conflicting cells (cells contributing to error)
        conflicts = set()
        for i in range(self.length):
            row = self.grid[i, :]
            for val in set(row):
                idxs = np.where(row == val)[0]
                if len(idxs) > 1:
                    for c in idxs:
                        if not self.fixed[i, c]:
                            conflicts.add((i, c))
            col = self.grid[:, i]
            for val in set(col):
                idxs = np.where(col == val)[0]
                if len(idxs) > 1:
                    for r in idxs:
                        if not self.fixed[r, i]:
                            conflicts.add((r, i))
        conflicts = list(conflicts)
        if len(conflicts) < 2:
            return

        # Permute a significant fraction of conflicting cells
        num_swaps = max(4, min(len(conflicts)//2, len(conflicts)))
        sampled = random.sample(conflicts, num_swaps)
        vals = [self.grid[r, c] for r, c in sampled]
        random.shuffle(vals)
        for idx, (r, c) in enumerate(sampled):
            self.grid[r, c] = vals[idx]

        # Stronger reheat based on conflicts
        self.T = max(self.T_init * 10, 0.5)
        self.iters_since_improvement = 0
        self.reheats += 1
        print(f"[Reheat {self.reheats}] Aggressive Temp reset to {self.T:.4f}, Errors={self.error_count}")

    def solve(self, display=False, max_iters=10**7):
        min_T = 0.01  # temperature floor
        while self.error_count > 0 and self.iters < max_iters:
            accepted = self.swap()

            # increment plateau counter if no improvement
            if self.error_count < self.best_error:
                self.best_error = self.error_count
                self.iters_since_improvement = 0
            else:
                self.iters_since_improvement += 1

            # reheat trigger for plateau
            if (self.iters_since_improvement >= self.N_plateau and
                self.reheats < self.max_reheats and
                self.error_count > 0):
                self.perturb_low_error_plateau()

            # Micro-reheat for very low errors
            if self.error_count <= 5 and self.iters_since_improvement > 2000:
                self.T = max(self.T, 0.5 + self.error_count * 0.05)
                self.iters_since_improvement = 0
                if display:
                    print(f"[Micro-reheat] Temp boosted to {self.T:.4f} for low errors")

            # decay temperature
            self.T = max(self.T * self.decay, min_T)
            self.iters += 1

            if display and self.iters % 5000 == 0:
                print(f"Iter {self.iters}, Errors {self.error_count}, Temp {self.T:.4f}")

        self.sudoku.board = self.grid.tolist()
        print(f"Solved in {self.iters} iterations, {self.reheats} reheats.")
        return self.iters
