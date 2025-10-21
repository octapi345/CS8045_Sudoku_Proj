import Sudoku
import math



class Root:
    def __init__(self):
        self.left=None
        self.right=None
        self.name="root"
    def getColHead(self, pos):
        target=self
        for i in range(pos):
            target=target.right
        return target
    def getColByName(self, name):
        target=self.right
        while(not target is self and target.name != name):
            #print(target.name)
            target=target.right    
        return target

class ColumnHeader:
    def __init__(self, name, root):
        self.left=None #other column header
        self.right=None #other column header
        self.up=self 
        self.down=self
        self.size=0
        self.name=name
        self.root=root
    def lastNode(self):
        last=self
        while(last.down and not (last.down is self)):
            last=last.down
        return last
    def cover(self):
        self.left.right=self.right
        self.right.left=self.left
        row=self.down
        while not row is self:
            i = row.right
            while not i is row:
                i.up.down=i.down
                i.down.up=i.up
                i.colHead.size-=1
                i=i.right
            row=row.down
    def uncover(self):
        row=self.up
        while not row is self:
            i = row.left
            while not i is row:
                i.colHead.size+=1
                i.up.down=i
                i.down.up=i
                i=i.left
            row=row.up
        self.left.right = self
        self.right.left = self
    
class Node:
    def __init__(self, colHead: ColumnHeader, rowHead):
        prevNode=colHead.lastNode()
        self.left=None
        self.right=None
        self.up=prevNode
        prevNode.down=self
        self.down=colHead
        colHead.up=self
        self.colHead=colHead
        self.rowHead=rowHead

    
class rowHeader:
    def __init__(self, row, col, digit, boardSize):
        self.row = row
        self.col = col
        self.digit = digit
        self.boardSize = boardSize
        self.box = (math.floor((row-1)/boardSize)*boardSize + math.ceil(col/boardSize))
        self.id = (row, col, digit)

#generates initial 2D linked list
def genLinkList(puzzle: Sudoku.Sudoku):
    root = Root()
    prev=root
    for i in range(4): #generate constraint sets
        nameFormat = ""
        match i:
            case 0:
                nameFormat="row {}, col {} contains a number"
            case 1:
                nameFormat="row {} contains digit {}"
            case 2:
                nameFormat="col {} contains digit {}"
            case 3:
                nameFormat="box {} contains digit {}"
        for j in range(1, puzzle.length+1):
            for k in range(1, puzzle.length+1):
                colH=ColumnHeader(nameFormat.format(str(j), str(k)), root)
                prev.right=colH
                colH.left=prev
                colH.right=root
                if i==3 and j==puzzle.length and k==puzzle.length:
                    root.left=colH
                prev=colH

    for row in range(1, puzzle.length+1): #generate possibilities
            for col in range(1, puzzle.length+1):
                for num in range(1, puzzle.length+1):
                    rowHead = rowHeader(row, col, num, puzzle.size)
                    colPos = ((row-1)*puzzle.length + col)
                    node1 = Node(root.getColHead(colPos), rowHead)
                    node1.colHead.size+=1
                    #print(node1.colHead.name + str(num))
                    #print(colPos)

                    colPos = ((row-1)*puzzle.length + num)+81
                    node2 = Node(root.getColHead(colPos), rowHead)
                    node2.colHead.size+=1

                    colPos = ((col-1)*puzzle.length + num)+162
                    node3 = Node(root.getColHead(colPos), rowHead)
                    node3.colHead.size+=1

                    colPos = ((rowHead.box-1)*puzzle.length + num)+243
                    node4 = Node(root.getColHead(colPos), rowHead)
                    node4.colHead.size+=1

                    node1.left=node4
                    node1.right=node2
                    node2.left=node1
                    node2.right=node3
                    node3.left=node2
                    node3.right=node4
                    node4.left=node3
                    node4.right=node1
    return root

def run(puzzle: Sudoku.Sudoku):
    #Initial board state generation
    root = genLinkList(puzzle)
    #print(root.right.right.size)
    initialBoard = puzzle.board
    for row in range(puzzle.length):
        for col in range(puzzle.length):
            if initialBoard[row][col]!=0:
                num = initialBoard[row][col]
                colName="row {}, col {} contains a number".format(str(row+1), str(col+1))
                #print(colName)
                colHead=root.getColByName(colName)
                #print(colHead.name)
                colHead.cover()

                colName = "row {} contains digit {}".format(str(row+1), str(num))
                colHead=root.getColByName(colName)
                colHead.cover()

                colName = "col {} contains digit {}".format(str(col+1), str(num))
                colHead=root.getColByName(colName)
                colHead.cover()

                box = (math.floor((row)/puzzle.size)*puzzle.size + math.ceil((col+1)/puzzle.size))
                colName = "box {} contains digit {}".format(str(box), str(num))
                colHead=root.getColByName(colName)
                colHead.cover()

    solutionList= []
    search(root, solutionList) #Run algorithm
    #print("done")
    #print(solutionList)
    #modify board state
    for val in solutionList:
        row = val[0]
        col = val[1]
        digit = val [2]
        puzzle.board[row-1][col-1]=digit


        

def search(root: Root, solutionList: list):
    #print("start")
    
    if root.right is root:
        #print(solutionList)
        return
    minNode = None
    minVal = 999
    pointer = root.right
    while not pointer is root:
        #print(pointer.name)
        if pointer.size<minVal:
            minNode=pointer
            minVal=pointer.size
        pointer=pointer.right
    #print(minNode.name)
    minNode.cover()
    row = minNode.up
    #print(row.rowHead.id)
    while not row is minNode:
        solutionList.append(row.rowHead.id)
        #print("appended")
        constraint=row.right
        while not constraint is row:
            col = constraint.colHead
            col.cover()
            constraint=constraint.right
        search(root, solutionList)
        if root.right is root:
            #print(solutionList)
            return
        constraint=row.left
        while not constraint is row:
            col = constraint.colHead
            col.uncover()
            constraint=constraint.left
        row=row.down
        solutionList.pop
    minNode.uncover()
    return


board1 = Sudoku.Sudoku(3)
digitString = "070000043040009610800634900094052000358460020000800530080070091902100005007040802"
board1.fillFromString(digitString)
run(board1)
print(board1.toString())
print(board1.isComplete())

