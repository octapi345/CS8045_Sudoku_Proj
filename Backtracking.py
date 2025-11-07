import Sudoku
global operations
operations=0
# def genStaticMatrix(puzzle: Sudoku):
#     output = [[0]*puzzle.length for _ in range(puzzle.length)]
#     for row in range(puzzle.length):
#         for col in range(puzzle.length):
#             if puzzle.board[row][col]!=0:
#                 output[row][col]=True
#     return output

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


board1 = Sudoku.Sudoku(3)
digitString = "070000043040009610800634900094052000358460020000800530080070091902100005007040802"
board1.fillFromString(digitString)
algorithm(board1)
print(board1.toString())
print("num operations outside isValid: "+str(operations))
print("number of isValid operations: "+str(board1.operations))
print("number of times isValid ran: "+str(board1.isValidRuns))


    



