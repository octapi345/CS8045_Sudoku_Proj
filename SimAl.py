import numpy as np

master_arr = np.array([i]* 9 for i in range(1,10))
print(master_arr)

class SimulatedAnnealing:
    def __init__(self, sudoku_init, t_sched = None):
        self.grid = np.array(sudoku_init.board)
        self.fixed = np.array(sudoku_init.fixed)
        self.can_swap = ~self.fixed
        
        
    def populate():
        pass