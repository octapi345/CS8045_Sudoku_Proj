import random
import csv

random.seed(14)

clue_numbers = {2:6, 3:20, 4:110, 5:230}
all_digits = {
    2:{1,2,3,4},
    3:{1,2,3,4,5,6,7,8,9},
    4:{1,2,3,4,5,6,7,8,9,'A','B','C','D','E','F','G'},
    5:{1,2,3,4,5,6,7,8,9,'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'}
}

def make_full_grid(size):
    N = size * size
    symbols = list(all_digits[size])

    # deterministic valid base grid via pattern
    def pattern(r, c):
        return (size * (r % size) + r // size + c) % N

    base = [[symbols[pattern(r, c)] for c in range(N)] for r in range(N)]

    # shuffle bands and rows within bands
    band_starts = list(range(0, N, size))
    random.shuffle(band_starts)
    row_order = []
    for b in band_starts:
        band_rows = list(range(b, b + size))
        random.shuffle(band_rows)
        row_order.extend(band_rows)

    # shuffle stacks and cols within stacks
    stack_starts = list(range(0, N, size))
    random.shuffle(stack_starts)
    col_order = []
    for s in stack_starts:
        stack_cols = list(range(s, s + size))
        random.shuffle(stack_cols)
        col_order.extend(stack_cols)

    # optional: permute symbols for extra randomness
    perm = symbols[:]
    random.shuffle(perm)
    mapping = {symbols[i]: perm[i] for i in range(N)}

    grid = [
        [mapping[base[r][c]] for c in col_order]
        for r in row_order
    ]
    return grid

def make_puzzle(size):
    full = make_full_grid(size)
    N = size*size
    total_cells = N*N
    clues = clue_numbers[size]
    blanks = total_cells - clues

    grid = [row[:] for row in full]
    coords = [(r, c) for r in range(N) for c in range(N)]
    random.shuffle(coords)

    for k in range(blanks):
        r, c = coords[k]
        grid[r][c] = 0

    grid_string = ''.join(str(x) for row in grid for x in row)
    return grid_string

for size in [2, 3, 4, 5]:
    filename = f"size{size}.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['puzzle'])
        for _ in range(1000):
            puzzle = make_puzzle(size)
            writer.writerow([puzzle])
    print(f"Wrote 1000 puzzles of size {size} to {filename}")
