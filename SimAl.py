import numpy as np
import math, random
from itertools import permutations

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
    def __init__(self, sudoku_init, t_init=5.0, decay=0.99995, max_plateau=35000, max_reheats=2000):
        self.sudoku = sudoku_init
        self.grid = np.array(sudoku_init.board)
        self.grid = np.vectorize(_to_int)(self.grid)
        self.fixed = np.array(sudoku_init.fixed)
        self.length = sudoku_init.length
        self.n = int(math.sqrt(self.length))

        # Annealing parameters
        self.T_init = t_init
        self.T = self.T_init
        self.decay = decay
        self.N_plateau = max_plateau
        self.max_reheats = max_reheats
        
        if self.n>4:
            self.N_plateau *= self.n

        # Tracking variables
        self.iters = 0
        self.iters_since_improvement = 0
        self.reheats = 0
        self.best_error = float('inf')
        self.tried_BF = False

        # Initial population
        self.populate_strict_boxes()
        self.error_count = self.compute_total_errors()

    def populate_strict_boxes(self):
        """Fill each n x n box with all numbers 1..N exactly once."""
        for br in range(self.n):
            for bc in range(self.n):
                numbers = list(range(1, self.length + 1))
                for r in range(br*self.n, (br+1)*self.n):
                    for c in range(bc*self.n, (bc+1)*self.n):
                        if self.fixed[r, c] and self.grid[r, c] in numbers:
                            numbers.remove(self.grid[r, c])
                positions = [(r, c) for r in range(br*self.n, (br+1)*self.n)
                             for c in range(bc*self.n, (bc+1)*self.n)
                             if not self.fixed[r, c]]
                random.shuffle(positions)
                random.shuffle(numbers)
                for (r, c), val in zip(positions, numbers):
                    self.grid[r, c] = val

    def compute_total_errors(self):
        """Count total number of conflicting cells in rows and columns."""
        errors = 0
        for i in range(self.length):
            row = self.grid[i, :]
            col = self.grid[:, i]

            # Count row conflicts
            _, row_counts = np.unique(row, return_counts=True)
            errors += np.sum(row_counts[row_counts > 1])

            # Count column conflicts
            _, col_counts = np.unique(col, return_counts=True)
            errors += np.sum(col_counts[col_counts > 1])

        return errors


    def compute_delta_errors(self, r1, c1, r2, c2):
        """Compute delta errors only for affected rows/columns after swapping two cells."""
        rows = {r1, r2}
        cols = {c1, c2}

        # Count errors before swap
        before = 0
        for r in rows:
            vals, counts = np.unique(self.grid[r, :], return_counts=True)
            before += np.sum(counts[counts > 1])
        for c in cols:
            vals, counts = np.unique(self.grid[:, c], return_counts=True)
            before += np.sum(counts[counts > 1])

        # Swap
        self.grid[r1, c1], self.grid[r2, c2] = self.grid[r2, c2], self.grid[r1, c1]

        # Count errors after swap
        after = 0
        for r in rows:
            vals, counts = np.unique(self.grid[r, :], return_counts=True)
            after += np.sum(counts[counts > 1])
        for c in cols:
            vals, counts = np.unique(self.grid[:, c], return_counts=True)
            after += np.sum(counts[counts > 1])

        # Swap back
        self.grid[r1, c1], self.grid[r2, c2] = self.grid[r2, c2], self.grid[r1, c1]

        return after - before



    def swap(self):
        """Swap two non-fixed cells within the same box."""
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

        return accepted

    def get_conflict_cells(self):
        conflicts = set()
        for i in range(self.length):
            row = self.grid[i, :]
            col = self.grid[:, i]
            for val in set(row):
                if list(row).count(val) > 1:
                    conflicts.update([(i, j) for j, v in enumerate(row) if v == val])
            for val in set(col):
                if list(col).count(val) > 1:
                    conflicts.update([(j, i) for j, v in enumerate(col) if v == val])
        return [cell for cell in conflicts if not self.fixed[cell]]

    def focused_swaps(self, conflict_cells):
        random.shuffle(conflict_cells)
        for i in range(0, len(conflict_cells), 2):
            if i+1 < len(conflict_cells):
                r1, c1 = conflict_cells[i]
                r2, c2 = conflict_cells[i+1]
                if (r1//self.n == r2//self.n) and (c1//self.n == c2//self.n):
                    self.grid[r1, c1], self.grid[r2, c2] = self.grid[r2, c2], self.grid[r1, c1]

    def simple_brute_force(self):
        """Local brute force: try all permutations of current conflict cells."""
        conflict_cells = self.get_conflict_cells()
        if not conflict_cells:
            return False

        k = len(conflict_cells)
        if k > 6:
            return False  # too many cells to brute force

        current_vals = [self.grid[r, c] for r, c in conflict_cells]

        for perm in permutations(current_vals):
            for (r, c), val in zip(conflict_cells, perm):
                self.grid[r, c] = val
            new_errors = self.compute_total_errors()
            if new_errors < self.error_count:
                self.error_count = new_errors
                return True

        # restore original values
        for (r, c), val in zip(conflict_cells, current_vals):
            self.grid[r, c] = val

        return False

    def solve(self, display=False, max_iters=8*(10**6)):
        min_T = 0.01

        while self.error_count > 0 and self.iters < max_iters:
            self.swap()

            # Update best error / plateau counter
            if self.error_count < self.best_error:
                self.best_error = self.error_count
                self.iters_since_improvement = 0
            else:
                self.iters_since_improvement += 1

            # Apply local brute force if very few conflicts
            if self.error_count <= 4 and self.n>3 and not self.tried_BF:
                improved = self.simple_brute_force()
                self.tried_BF = True
                if improved and self.error_count == 0:
                    
                    #print("[Simple brute force] Solution found!")
                    break

            # Plateau: reheat + focused perturbation
            if self.iters_since_improvement >= self.N_plateau and self.reheats < self.max_reheats:
                self.T = max(0.4, self.T * 1.5)
                if self.n > 4:
                    self.T *= 1.5
                self.reheats += 1
                if display:
                    print(f"[Reheat {self.reheats}] Temp reset to {self.T:.4f}, Errors={self.error_count}")

                conflict_cells = self.get_conflict_cells()
                if conflict_cells:
                    self.focused_swaps(conflict_cells)
                    self.error_count = self.compute_total_errors()
                    if display:
                        print(f"[Perturb] Focused swaps on {len(conflict_cells)} conflict cells. Errors={self.error_count}")

                self.iters_since_improvement = 0
                self.tried_BF = False

            # Decay temperature
            self.T = max(self.T * self.decay, min_T)
            self.iters += 1

            if display and self.iters % 5000 == 0:
                print(f"Iter {self.iters}, Errors {self.error_count}, Temp {self.T:.4f}")

        self.sudoku.board = self.grid.tolist()
        if display:
            print(f"Solved in {self.iters} iterations, {self.reheats} reheats.")
        return self.iters
