import Sudoku
global operations
operations=0

def nextCell(puzzle: Sudoku, cell):
    global operations
    operations+=1
    if cell[1] < (puzzle.length-1):
        operations+=1
        cell[1]+=1
    else:
        operations+=2
        cell[0]+=1
        cell[1]=0
    return cell

def prevCell(puzzle: Sudoku, cell):
    global operations
    operations+=1
    if cell[1] > 0:
        operations+=1
        cell[1]-=1
    else:
        operations+=2
        cell[0]-=1
        cell[1]=puzzle.length-1
    return cell

def algorithm(puzzle: Sudoku):
    isStatic = puzzle.fixed
    return run(puzzle, isStatic, [0, 0], False)

def run(puzzle: Sudoku, isStatic, cell: list, inReverse: bool):
    global operations
    operations+=3
    if cell[0] < 0:
        return False
    if cell[0] >= puzzle.length:
        return True
    
    if isStatic[cell[0]][cell[1]]:
        operations+=1
        if inReverse:
            return run(puzzle, isStatic, prevCell(puzzle, cell), True)
        return run(puzzle, isStatic, nextCell(puzzle, cell), False)
    
    operations+=2
    puzzle.board[cell[0]][cell[1]]+=1
    while puzzle.board[cell[0]][cell[1]]<=puzzle.length:
        if puzzle.isValid():
            return run(puzzle, isStatic, nextCell(puzzle, cell), False)
        operations+=1
        puzzle.board[cell[0]][cell[1]]+=1
    operations+=1    
    puzzle.board[cell[0]][cell[1]]=0
    return run(puzzle, isStatic, prevCell(puzzle, cell), True)