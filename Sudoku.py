class Sudoku:
    def __init__(self, size):
        self.size = size #size 3 means 9x9
        self.length = size*size
        self.board = [[0]*self.length for _ in range(self.length)] 
        self.fixed = [[False]*self.length for _ in range(self.length)]
        self.operations = 0
        self.isValidRuns = 0
    
    def fillFromString(self, digitString): #only works with size 3 or less. done with digits. zero is empty
        digitArr = [int(char) for char in digitString] 
        pointer = 0
        for i in range(self.length):
            for j in range(self.length):
                self.board[i][j]=digitArr[pointer]
                if self.board[i][j]!=0:
                    self.fixed[i][j]=True
                pointer += 1

    def toString(self):
        output = ""
        for row in self.board:
            output+=('-'*2*self.length)+"\n"
            for num in row:
                output+="|"+str(num)
            output+="|\n"
        output+=('-'*2*self.length)+"\n"
        return output

    
    def isComplete(self): #checks if the sudoku has any illegal number placements. also insures no empty cells
        for i in range(self.length): #checks rows
            contains = [False]*(self.length+1)

            for j in range(self.length):
                num = self.board[i][j]
                if contains[num]:
                    return False
                contains[num]=True
            
            if contains[0]: #checks if any cells empty
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
                    for m in range(self.size):
                        num = self.board[(i*self.size)+k][(j*self.size)+m]
                        if contains[num]:
                            return False
                        contains[num]=True
        return True

    def isValid(self): #checks if the sudoku has any illegal number placements. ignores empty cells
        self.isValidRuns+=1
        for i in range(self.length): #checks rows
            contains = [False]*(self.length+1)
            
            for j in range(self.length):
                self.operations+=4
                num = self.board[i][j]
                if num!=0 and contains[num]:
                    return False
                contains[num]=True
                

        for i in range(self.length): #checks columns
            contains = [False]*(self.length+1)

            for j in range(self.length):
                self.operations+=4
                num = self.board[j][i]
                if num!=0 and contains[num]:
                    return False
                contains[num]=True
        

        for i in range(self.size): #checks boxes
            for j in range(self.size):
                contains = [False]*(self.length+1)

                for k in range(self.size):
                    for m in range(self.size):
                        self.operations+=4
                        num = self.board[(i*self.size)+k][(j*self.size)+m]
                        if num!=0 and contains[num]:
                            return False
                        contains[num]=True
        return True
    
    def numErrors(self, grid=None): #checks number of errors (matching digits in row) in board
        errors = 0
        if grid==None:
            grid = self.board
        for i in range(self.length): #checks rows
            contains = [False]*(self.length+1)
            
            for j in range(self.length):
                num = grid[i][j]
                if num!=0 and contains[num]:
                    errors+=1
                contains[num]=True
                

        for i in range(self.length): #checks columns
            contains = [False]*(self.length+1)

            for j in range(self.length):
                num = grid[j][i]
                if num!=0 and contains[num]:
                    errors+=1
                contains[num]=True
        

        for i in range(self.size): #checks boxes
            for j in range(self.size):
                contains = [False]*(self.length+1)

                for k in range(self.size):
                    for m in range(self.size):
                        num = grid[(i*self.size)+k][(j*self.size)+m]
                        if num!=0 and contains[num]:
                            errors+=1
                        contains[num]=True
        return errors