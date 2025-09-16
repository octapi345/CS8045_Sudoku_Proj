import Sudoku

board1 = Sudoku.Sudoku(3)
digitString = "070000043040009610800634900094052000358460020000800530080070091902100005007040802"
board1.fillFromString(digitString)
print(board1.toString())