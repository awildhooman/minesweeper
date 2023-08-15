#x-coordinate is column, y-coordinate is row

import random

class Board:

    squares = []
    
    def __init__(self, length, height, percentMines):
        self.length = length
        self.height = height
        self.percentMines = percentMines

    def printBoard(self):
        print("\033[2J\033[H")
        print(" " + "  ".join((str(i%10 + 1) if i%10 != 9 else "0" for i in range(self.length))))
        print(" --"*self.length)
        for i in range(self.height):
            print("|" + " |".join((square.returnSquareValue() for square in self.squares[i])) + " |" + str(i+1))
            print(" --"*self.length)

    #initializes empty squares, with some of them being mines
    def initializeSquares(self):
        for row in range(self.height):
            squareRow = []
            for col in range(self.length):
                if random.randint(1, 100) <= percentMines:
                    squareRow.append(Square(col, row, True, 0, 0, True, False))
                else:
                    squareRow.append(Square(col, row, True, 0, 0, False, False))
            self.squares.append(squareRow)

    #after initializing the squares, for each square this calculates the number of adjacent mines
    def initializeMines(self):
        for row in range(self.height):
            for col in range(self.length):
                square = self.squares[row][col]
                if square.isMine:
                    for neighbor in self.getNeighbors(col, row):
                        neighbor.adjacentMines += 1

    #main loop
    def move(self, col, row, action):
        self.revealSquare(col, row, action)
        self.revealAdjacentSquaresWithFlags(col, row)

    #performs a dig or flag action
    def revealSquare(self, col, row, action):
        square = self.squares[row][col]
        if action == "F" or action == "f":
            if square.isFlagged:
                self.squares[row][col].isFlagged = False
            else:
                if square.isHidden:
                    self.squares[row][col].isFlagged = True
        elif (action == "D" or action == "d"):
            if not square.isFlagged:
                if square.isMine:
                    global gameState
                    gameState = -1
                elif square.adjacentMines == 0 and square.isHidden:
                    self.revealAdjacentSquares(col, row)
                else:
                    if self.squares[row][col].isHidden == True:
                        self.squares[row][col].isHidden = False
        else:
            pass
    
    #reveals adjacent squares; used when a square with a 0 is unconvered
    def revealAdjacentSquares(self, col, row):
        neighbors = self.getNeighbors(col, row)
        if self.squares[row][col].isHidden == True:
            self.squares[row][col].isHidden = False
        for neighbor in neighbors:
            if neighbor.adjacentMines == 0 and neighbor.isHidden:
                self.revealAdjacentSquares(neighbor.col, neighbor.row)
            else:
                self.revealSquare(neighbor.col, neighbor.row, "d")

    #if a square has the same number of adjacent mines as adjacent flags, selecting that square to dig reveals the remaining adjacent squares
    def revealAdjacentSquaresWithFlags(self, col, row):
        adjacentMines = self.squares[row][col].adjacentMines
        if adjacentMines > 0 and adjacentMines == self.getAdjacentFlags(col, row) and (not self.squares[row][col].isHidden):
            self.revealAdjacentSquares(col, row)

    #makes sure first square picked has 0 adjacent mines
    def firstMove(self, col, row):
        neighbors = self.getNeighbors(col, row)
        for neighbor in neighbors:
            neighbor.isMine = False
        self.squares[row][col].adjacentMines = 0
        self.squares[row][col].isMine = False
        self.initializeMines()
        self.revealSquare(col, row, "d")

    #returns a square's adjacent squares
    def getNeighbors(self, col, row):
        neighbors = []
        adjacentSquares = [[col-1, row-1], [col, row-1], [col+1, row-1], [col-1, row], [col+1, row], [col-1, row+1], [col, row+1], [col+1, row+1]]
        for coordinate in adjacentSquares:
            if not (coordinate[0] == -1 or coordinate[0] >= self.length or coordinate[1] == -1 or coordinate[1] >= self.height):
                neighbors.append(self.squares[coordinate[1]][coordinate[0]])
        return neighbors

    #return number of flags adjacent to a square
    def getAdjacentFlags(self, col, row):
        adjacentFlags = 0
        for neighbor in self.getNeighbors(col, row):
            if neighbor.isFlagged:
                adjacentFlags += 1
        return adjacentFlags

class Square:

    def __init__(self, col, row, isHidden, adjacentMines, adjacentFlags, isMine, isFlagged):
        self.col = col
        self.row = row
        self.isHidden = isHidden
        self.adjacentMines = adjacentMines
        self.adjacentFlags = adjacentFlags
        self.isMine = isMine
        self.isFlagged = isFlagged
    
    def returnSquareValue(self):
        global allSquaresRevealed
        if gameState == -1 and self.isMine:
            return "M"
        elif self.isFlagged:
            return "F"
        elif self.isHidden:
            #when printBoard() is called, returnSquareValue() is called on every square, so this checks if all squares are revealed
            if not self.isMine:
                allSquaresRevealed = 0
            return " "
        else:
            return str(self.adjacentMines)

print("Welcome to Minesweeper! Your task is to clear all of the spaces without hitting a mine. When you clear a space, a number will show up, representing the number of mines in the eight adjacent squares. If you hit a mine, you lose. You can clear a space whose number equals the number of adjacent flags to reveal all adjacent squares. Good luck!\n\n")
boardLength = int(input("Choose length of board: "))
boardHeight = int(input("Choose height of board: "))
percentMines = int(input("Choose percentage of mines between 1 and 100: "))
print("Input syntax: <column> <row> <action>")
#gamestate: 0 means game is in progress, 1 means game is won, -1 means game is lost
gameState = 0
allSquaresRevealed = 1

if boardLength <= 1:
    boardLength = 10
if boardHeight <= 1:
    boardHeight = 10

board = Board(boardLength, boardHeight, percentMines)
board.initializeSquares()

#first move, guarantees that first dug square is not a mine
board.printBoard()
Input = input().split(" ")
inputCol = int(Input[0])-1
inputRow = int(Input[1])-1
board.firstMove(inputCol, inputRow)
board.printBoard()

while gameState == 0:
    allSquaresRevealed = 1
    Input = input().split(" ")
    #-1 to make it not 0-indexed for user
    inputCol = int(Input[0])-1
    inputRow = int(Input[1])-1
    action = Input[2]
    board.move(inputCol, inputRow, action)
    board.printBoard()
    if allSquaresRevealed == 1:
        gameState = 1

if gameState == -1:
    board.printBoard()
    print("You lose!")

if gameState == 1:
    board.printBoard()
    print("You win!")