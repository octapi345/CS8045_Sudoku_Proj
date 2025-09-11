class Sudoku:
    def __init__(self, size):
        self.size = size #size 3 means 9x9
        self.length = size*size
        self.board = [[0]*self.length]*self.length
    
    def fillfromString(self, digitString): #only works with size 3 or less. done with digits. zero is empty
        digitArr = [int(char) for char in digitString] 
        pointer = 0
        for i in range(self.length):
            for j in range(self.length):
                self.board[i][j]=digitArr[pointer]
                pointer += 1

    
    def isComplete(self): #checks if the sudoku has any illegal number placements. also insures no empty cells
        for i in range(self.length): #checks rows
            contains = [False]*(self.length+1)

            for j in range(self.length):
                num = self.board[i][j]
                if contains[num]:
                    return False
                contains[num]=True
            
            if contains[0]: 
                return False
        

        for i in range(self.length): #checks columns
            contains = [False]*(self.length+1)

            for j in range(self.length):
                num = self.board[j][i]
                if contains[num]:
                    return False
                contains[num]=True
        

        for i in range(self.size): #checks boxes
            for j in range(self.size):
                contains = [False]*(self.length+1)

                for k in range(self.size):
                    for l in range(self.size):
                        num = self.board[(i*self.size)+k][(j*self.size)+l]
                        if contains[num]:
                            return False
                        contains[num]=True
        return True