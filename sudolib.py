#Sudoku lib
"""
----------------------HOW GENERATION WORKS---------------------------

the generation algorithm is kind of like a waterfall. We start with very low level 
primitives, and gradually build logic on top. Each individual block *should* be pure--
it doesn't affect its input args, and it outputs new data with no side affects.

Lib escalates in complexity. First we need to access all the cells within a given 
row, sqr, col. With this information, we can naively check for possible values (just
based on whether that value is already set). If we check possibilities for each cell
in board, that creates a cache of possible values.

uniqueCheck() compares *possible values* for a given cell, against possible values 
for its entire row/sqr/col. If there's a unique possible value, it must be answer.

Solve() runs checkunique over and over, until hopefully puzzle is solved. THere's also
a recursion clause, where we make an arbitrary guess about a hard cell and check it.

Generate switches between randomly choosing a cells value (from possibles), and then 
running solve() on entire board to catch any determined cells. Usually this results in 
legal board, but if not, it repeats until we get legal.

Once we have full and legal board, we run carve() to randomly remove cells (while
keeping puzzle solveable. We have to check that puzzle is solveable for each removed
cell, but thankfully solve() is fast. At first we remove random cells, at end we loop
through all to get any remaining unnecessary cells.


STORAGE section just includes utitilities for storing a given puzzle in DB. We normalize
the puzzle, eg rotate it (consistently) and order it--this prevents us from storing different
permutations of the same underlying puzzle. On retrieving a puzzle, we use shuffle() to rotate
and un-order it, creating a different random permutation each time its retrieved.

We use stringify() and unstringify() to serialize a puzzle into a string, for storage.
"""


import random
import time


#---------------BOARD UTILITY----------------#

#sample boards
if True:

    s3 =  [[0,1,0,9,0,0,0,0,3],
        [0,5,9,0,0,3,0,7,0],
        [0,3,0,0,4,5,1,0,0],
        [6,0,0,0,2,0,9,3,0],
        [0,0,0,0,0,0,0,0,0],
        [0,4,8,0,7,0,0,0,2],
        [0,0,1,6,5,0,0,9,0],
        [0,9,0,4,0,0,6,1,0],
        [0,0,0,0,0,1,0,2,0],]

    s4 =  [[0,0,0,0,2,7,0,0,8],
        [2,0,7,0,0,0,4,9,0],
        [0,0,0,0,0,1,0,2,7],
        [8,9,0,0,0,0,0,5,0],
        [1,0,0,9,0,6,0,0,4],
        [0,7,0,0,0,0,0,1,9],
        [7,8,0,2,0,0,0,0,0],
        [0,1,2,0,0,0,9,0,5],
        [3,0,0,6,8,0,0,0,0],]

    s5 =  [[0,0,0,0,0,0,0,4,8],
        [0,8,6,9,0,0,0,0,1],
        [0,2,0,0,8,3,7,0,0],
        [6,0,0,5,0,0,0,1,7],
        [0,0,0,0,6,0,4,0,0],
        [2,4,0,0,0,7,0,0,5],
        [0,0,2,3,5,0,0,8,0],
        [3,0,0,0,0,8,5,7,0],
        [9,5,0,0,0,0,0,0,0],]
        
    d1 = [[0, 3, 7, 2, 1, 6, 9, 4, 8], 
        [4, 8, 6, 9, 7, 5, 2, 3, 1], 
        [1, 2, 9, 4, 8, 3, 7, 5, 6], 
        [6, 9, 3, 5, 4, 2, 8, 1, 7], 
        [8, 7, 5, 1, 6, 9, 4, 2, 3], 
        [2, 4, 1, 8, 3, 7, 6, 9, 5], 
        [7, 6, 2, 3, 5, 4, 1, 8, 9], 
        [3, 1, 4, 6, 9, 8, 5, 7, 2], 
        [9, 5, 8, 7, 2, 1, 3, 6, 4]]

    f1 = [[8, 7, 9, 1, 2, 4, 3, 6, 5], 
            [5, 2, 4, 8, 6, 3, 7, 1, 9], 
            [6, 3, 1, 7, 5, 9, 8, 2, 4], 
            [7, 5, 8, 6, 4, 2, 9, 3, 1], 
            [2, 9, 3, 5, 8, 1, 4, 7, 6], 
            [1, 4, 6, 9, 3, 7, 5, 8, 2], 
            [3, 6, 5, 4, 1, 8, 2, 9, 7], 
            [4, 8, 7, 2, 9, 6, 1, 5, 3], 
            [9, 1, 2, 3, 7, 5, 6, 4, 8]]

def getEmptyBoard():
    out = [[0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],]
    return out

def printBoard(board, hidezeros=True):
    for y, x in fullGen():
        #print every number
        if board[y][x] == 0 and hidezeros:
            print(' ', end=" ")
        else:
            print(board[y][x], end=" ")


        #formatting & separators
        if x == 8:
            print()
            if y == 2 or y == 5:
                print("----------------------")

        if x == 2 or x == 5:
            print("| ", end="")
        
def copyBoard(board):
    """Normally assigning a var to an existing board just copies the reference. this creates a 
    entire new copy. Use with getEmptyBoard() as the copy"""
    copy = getEmptyBoard()
    for y, x in fullGen():
        copy[y][x] = board[y][x]
    return copy

def getBitmap(board):
    """has 1 for all given cells, 0 for undecided cells"""
    out = getEmptyBoard()
    for y, x in fullGen():
        if board[y][x] != 0:
            out[y][x] = 1
    return out

def getOrigPermutation(board, bitmap):
    """Returns original problem board, based on bitmap
    
    I'm sure there's an elegant (complex) one-liner that could accomplish this,
    with nested generators. But this is easier I think.
    """
    out = getEmptyBoard()
    for y, x in fullGen():
        out[y][x] = board[y][x] * bitmap[y][x]
    return out

# generators to return coordinates of each cell in a row, column, or square. Replace nested loops.
def rowGen(y, x, inclusive=True):
    """Return generator that gives coord tuples (y,x) for this row"""
    return ((y, x1) for x1 in range(9) if (inclusive) or (x1 != x))
            
def colGen(y, x, inclusive=True):
    """Return generator that gives coord tuples (y,x) for the col"""
    return ((y1, x) for y1 in range(9) if (inclusive) or (y1 != y))
                
def sqrGen(y, x, inclusive=True):
    """Return generator that gives coord tuples (y,x) for the sqr"""
    cY = (y // 3) * 3   # calculate top-left corner of square, for
    cX = (x // 3) * 3   # the provided cell
    return ((y1, x1) for y1 in range(cY, cY+3) for x1 in range(cX, cX+3)
            if (inclusive) or (y1 != y) or (x1 != x))

def fullGen():
    """Returns generator that gives coord tuples (y,x) for whole board"""
    return ((y1, x1) for y1 in range(9) for x1 in range(9))
            
def exclusiveGen():
    a = lambda x, y: ((x*3 + x//3 + y) % 9)
    return ((a(y1, x1), x1) for y1 in range(9) for x1 in range(9)) 

def funnyGen():
    xs = [0,1,2,0,1,2,0,1,2]
    ys = [0,1,2,2,0,1,1,2,0]
    for sqr in range(9):
        cornerY = ys[sqr] * 3
        cornerX = xs[sqr] * 3
        for cel in range(9):
            yield cornerY + ys[cel], cornerX + xs[cel]

def rotate(start, rotates=1):
    """spins board clockwise 90 degrees for each 'rotate'. Returns new board"""
    workboard = copyBoard(start)
    for i in range(rotates):
        temp = getEmptyBoard()
        for y, x in fullGen():
            y1 = x 
            x1 = abs(8 - y)
            temp[y1][x1] = workboard[y][x]
        workboard = temp
    return workboard 
    

#---------------GET VALUES-------------------#

# Return list of KNOWN values within a row/sqr/col.         
def getRowVals(board, y, x, inclusive=True):
    """Returns list of values of already set cells in row"""
    out = []
    for y1, x1 in rowGen(y, x, inclusive=inclusive):
        if board[y1][x1] == 0:
            continue 
        elif type(board[y][x]) == int:
            out.append(board[y1][x1])
        else:
            out += board[y1][x1]
    return out   
    
def getColVals(board, y, x, inclusive=True):
    """Returns list of values of already set cells in col"""
    out = []
    for y1, x1 in colGen(y, x, inclusive=inclusive):
        if board[y1][x1] == 0:
            continue 
        elif type(board[y][x]) == int:
            out.append(board[y1][x1])
        else:
            out += board[y1][x1]
    return out

def getSqrVals(board, y, x, inclusive=True):
    """Returns list of values of already set cells in sqr"""
    out = []
    for y1, x1 in sqrGen(y, x, inclusive=inclusive):
        if board[y1][x1] == 0:
            continue 
        elif type(board[y][x]) == int:
            out.append(board[y1][x1])
        else:
            out += board[y1][x1]
    return out

def getPoss(board, y, x):
    """Returns set of possible values for a cell. Returns single-value set if cell is decided."""
    if board[y][x] != 0:
        return [board[y][x]]

    return ({1,2,3,4,5,6,7,8,9}
            -set(getRowVals(board, y, x))
            -set(getColVals(board, y, x))
            -set(getSqrVals(board, y, x)))

def countZeros(board):
    """Returns count of zeros (eg carved cells) in a provided board. 
    
    Should work on stringify() board, and also full list board"""
    
    if type(board) == str:
        return board.count('0')
        
    zeros = 0
    for y, x in fullGen():
        if board[y][x] == 0:
            zeros += 1
    return zeros

#---------------SOLVER-----------------------#

def generateCache(board):
    """returns parallel cache board, holding set of possibilities for each cell"""
    out = getEmptyBoard()
    for y, x in fullGen():
        out[y][x] = getPoss(board, y, x)
    return out
    
def uniqueCheck(board, y, x, cache=None):
    """Tries to solve cell. Return 1-9 if found, 0 if inconclusive, -1 if no possibilities. 
    
        Looks like this is 16x faster w cache provided. Also if we calc cache here, we're doing a lot of
        work to get possibilities for cells we won't access. 
        
        Works by getting the set of possible values
        for the cell, then comparing with the possible values for every other cell in its row/col/sqr.
    """
    
    #run cheap, naive checks first
    cellPoss = getPoss(board, y, x)
    if len(cellPoss) == 1:      #if cell has one poss, must be answer
        return cellPoss.pop()
    elif len(cellPoss) == 0:    #if no poss for cell, must be error in board
        return -1

    #if no cache, we do have to generate one
    if cache == None:
        cache = generateCache(board)

    #compare cell possibilities to unit possibilities. Looking for UNIQUE poss in cell
    if cellPoss - set(getRowVals(cache, y, x, inclusive=False)):
        return (cellPoss - set(getRowVals(cache, y, x, inclusive=False))).pop()
    if cellPoss - set(getColVals(cache, y, x, inclusive=False)):
        return (cellPoss - set(getColVals(cache, y, x, inclusive=False))).pop()
    if cellPoss - set(getSqrVals(cache, y, x, inclusive=False)):
        return (cellPoss - set(getSqrVals(cache, y, x, inclusive=False))).pop()
    
    #if inconclusive, just return nothing
    return 0
            
def solve(board, nest=0):
    """This is best-effort solve. Tries its best, but may return an incomplete or inconsistent 
        board. If error, should have that cell as -1. 
    """
    wb = copyBoard(board)   #pure function--dont change original board arg
    c = generateCache(wb)
    solved = False
    changed = True

    while not solved and changed:           # iterate over board
        changed = False
        for y, x in fullGen():              # use uniqueCheck() against whole board
            if wb[y][x] == 0:               # but skip already solved cells
                wb[y][x] = uniqueCheck(wb, y, x, cache=c)
                if wb[y][x] > 0:
                    c = generateCache(wb)       #regen cache if we hit an answer
                    changed = True              #if solved, raise the flag

        if checkComplete(wb):               #now check if it's finished
            solved = True

    #recurse clause (up to 3 times)
    if not solved and nest < 3:
        lpy, lpx = 0, 0     #lynchpin cell coords. Find cell with most possibilities.
        for y, x in fullGen():
            if len(c[y][x]) > len(c[lpy][lpx]):
                lpy, lpx = y, x

        #now we check EACH possibility for lynchpin, to see if we get a solve
        for value in c[lpy][lpx]:
            testWB = copyBoard(wb)              #testWB is a branch--doesn't change orig state of wb
            testWB[lpy][lpx] = value            #make assumption about lynchpin  
            testWB = solve(testWB, nest=nest+1) #try to solve

            if checkComplete(testWB) and checkConsistent(testWB):
                if not solved:
                    wb = testWB
                    solved = True
                else:                           #if board already solved, means multiple solutions
                    print("Error: recursion uncovered multiple valid solutions")
                    wb[0][0] = 0                #in case of multiple valid solutions, fail the board

    #output the now-solved (maybe incomplete) (and maybe inconsistent) board
    return wb 

def checkComplete(board):
    """Naive check whether each cell has been filled (or if its still 0)"""
    for y, x in fullGen():
        if board[y][x] == 0:
            return False 
    return True
        
def checkConsistent(board):
    """Loop through board. If a cell matches another cell in its unit, its not consistent"""

    #check for -1 first, this automatically means error
    if not checkConsistentCheap(board):
        return False
    
    for y, x in fullGen():
        if board[y][x] == 0:    #ignore unset cells
            continue  

        temp = (  
            getRowVals(board, y, x, inclusive=False) 
            + getColVals(board, y, x, inclusive=False)
            + getSqrVals(board, y, x, inclusive=False)
        )
        if board[y][x] in temp:
            return False

    return True

def checkConsistentCheap(board):
    for y, x in fullGen():
        if board[y][x] == -1:
            return False
    return True


#---------------GENERATOR--------------------#

def picker(board, y, x, cache=None):
    #short-circuit, if y/x has val already
    if board[y][x] != 0:    
        return board[y][x]
    
    # cache is optional arg, may need to calc
    if cache == None:       
        cache = generateCache(board)

    #uniqueCheck returns value, or -1 for error
    slv = uniqueCheck(board, y, x, cache=cache)
    if slv != 0:      
        return slv
    
    # if no existing val, solve, or error, pick randomly from valid opt    
    else:             
        options = list(cache[y][x])
        return options[random.randint(0, len(options)-1)]

def generate():
    done = False
    while not done:
        n = getEmptyBoard()
        for y, x in fullGen():          # loop through entire board
            n[y][x] = picker(n, y, x)   # picker solves cell if possible, otherwise gives random

            if y > 5:                   # heuristic: once board is mostly full
                n = solve(n, nest=4)    # start trying to solve remaining cells
                if checkComplete(n):    
                    break

        if checkConsistent(n):
            done = True
    return n

def removable(board, y, x, nest=4):
    """ Tests whether board can still be solved without given y/x cell. Returns true/false"""
    test = copyBoard(board)        
    test[y][x] = 0
    test = solve(test, nest=nest)  # test to see if board is still solveable after remove

    if checkComplete(test) and checkConsistent(test):
        return True 
    else:
        return False

def rm(wb, forbid, ry, rx, nest=4):
    """checks whether a cell is removable or not. If yes, removes it. Returns 1 or 0, if removed.
    
    This is NOT PURE. It changes the wb and forbid lists that are passed to it.
    """
    if wb[ry][rx] == 0 or forbid[ry][rx] == 1: 
        return 0
    if removable(wb, ry, rx, nest=nest):       # if board solveable after removing this coord
        wb[ry][rx] = 0              # remove that cell and continue
        return 1
    else:
        forbid[ry][rx] = 1          # if test fails, forbid value so we dont retest it
        return 0

def carve(board, count=60):
    """ Takes a full board, and removes cells so that puzzle is still solveable. Removes up to
    count cells (if it can. In practice, we're removing ~60 cells max right now)
    """
    wb = copyBoard(board)
    forbid = getEmptyBoard()            # if a cell is necessary for solve, save coords 
    removes = 0
    attempts = 0

    # stage one: try removing random coords (up to 50 times
    while removes < count and attempts < 50:  
        attempts += 1
        ry = random.randint(0, 8)  
        rx = random.randint(0, 8)
        if rm(wb, forbid, ry, rx):      # rm() tries remove, updates wb and forbid, returns t/f
            removes += 1
            
    # stage two: crawl entire board and try remove
    if removes < count:
        for ry, rx in exclusiveGen():
            if rm(wb, forbid, ry, rx): # nest=1):   # can use nesting to get ~5 extra carves (at time cost)
                removes += 1
                if removes == count:
                    break
                
    #print(removes)
    return wb 

def getPuzzle(diff=40):
    """feed it the number of cells to remove. 60 is hard, 25 is easy"""
    return carve(generate(), count=diff)


#---------------STORAGE----------------------#


def rotateNormal(board):
    """Rotates board so heaviest side is on bottom. Goal is consistency--identical puzzles should end up
    the same, regardless of initial orientation (identical meaning *normal* versions of the puzzle are identical).
    
    I want to take a given puzzle and rotate it, so that different permutations always end up in the same
    orientation. I cannot use the values of the cells, because these will also be normalized. So, I have to 
    consider only the *locations* of filled vs unfilled cells--we're essentially figuring out which side
    is the heaviest.
    
    If I only counted all the values on a given side (eg the top is every cell in first three rows), sides 
    would frequently have the same weight. So, we scale each row (and each square) slightly differently.
    The scaling should be the same between different sides, so the same side gets the same weighted score
    regardless of whether it's currently on top, left, bottom or right. But specific *cells* within that side
    are weighted differently, to try to give differentiation.
    
    We still have problem of a completely symmetrical puzzle being non-rotateable. But giving these funky
    weights decreases the chance of that (hopefully)
    
    """
    a, b, c, d = 0, 0, 0, 0            # these hold sum of weights for each side

    t1 = sum(1.114 for y, x in rowGen(0,4) if board[y][x] != 0)
    t2 = sum(1.326 for y, x in rowGen(1,4) if board[y][x] != 0)
    t3 = sum(1.453 for y, x in rowGen(2,4) if board[y][x] != 0)
    t4 = sum(1.242 for y, x in sqrGen(0,0) if board[y][x] != 0)
    t5 = sum(1.141 for y, x in sqrGen(0,3) if board[y][x] != 0)
    t6 = sum(1.242 for y, x in sqrGen(0,6) if board[y][x] != 0)
    a = t1 + t2 + t3 + t4 + t5 + t6

    t1 = sum(1.114 for y, x in colGen(4,8) if board[y][x] != 0)
    t2 = sum(1.326 for y, x in colGen(4,7) if board[y][x] != 0)
    t3 = sum(1.453 for y, x in colGen(4,6) if board[y][x] != 0)
    t4 = sum(1.242 for y, x in sqrGen(0,8) if board[y][x] != 0)
    t5 = sum(1.141 for y, x in sqrGen(3,8) if board[y][x] != 0)
    t6 = sum(1.242 for y, x in sqrGen(6,8) if board[y][x] != 0)
    b = t1 + t2 + t3 + t4 + t5 + t6

    t1 = sum(1.114 for y, x in rowGen(8,4) if board[y][x] != 0)
    t2 = sum(1.326 for y, x in rowGen(7,4) if board[y][x] != 0)
    t3 = sum(1.453 for y, x in rowGen(6,4) if board[y][x] != 0)
    t4 = sum(1.242 for y, x in sqrGen(8,0) if board[y][x] != 0)
    t5 = sum(1.141 for y, x in sqrGen(8,3) if board[y][x] != 0)
    t6 = sum(1.242 for y, x in sqrGen(8,6) if board[y][x] != 0)
    c = t1 + t2 + t3 + t4 + t5 + t6

    t1 = sum(1.114 for y, x in colGen(4,0) if board[y][x] != 0)
    t2 = sum(1.326 for y, x in colGen(4,1) if board[y][x] != 0)
    t3 = sum(1.453 for y, x in colGen(4,2) if board[y][x] != 0)
    t4 = sum(1.242 for y, x in sqrGen(0,0) if board[y][x] != 0)
    t5 = sum(1.141 for y, x in sqrGen(3,0) if board[y][x] != 0)
    t6 = sum(1.242 for y, x in sqrGen(6,0) if board[y][x] != 0)
    d = t1 + t2 + t3 + t4 + t5 + t6


    if a>b and a>c and a>d:
        return board 
    elif b>a and b>c and b>d:
        return rotate(board)
    elif c>a and c>b and c>d:
        return rotate(board, rotates=2)
    elif d>a and d>b and d>c:
        return rotate(board, rotates=3)
    else:
        print('error, two values collide')
        print('a: ', a, 'b: ', b, 'c: ', c, 'd: ', d)
        return getEmptyBoard()
    
def orderNormal(board):
    """ Re-orders values in puzzle, without changing logic. Goal is consistency"""

    temp = copyBoard(board)
    for digit in range(1, 9):           # go through 1 - 9, to ensure puzzle is in order
        for y, x in fullGen():          # check through entire board
            if temp[y][x] < digit:     # if cell is 0 or smaller number, ignore since already in order
                continue 
            elif temp[y][x] == digit:  # if next cell we come to is our digit, break since already in order
                break
            else:                       # if cell is out of order, swap all occurences of number w digit 
                old = 1*temp[y][x]                 # get old, out of order num
                for y1, x1 in fullGen():            # new loop through board
                    if temp[y1][x1] == old:        # swap
                        temp[y1][x1] = digit 
                    elif temp[y1][x1] == digit:
                        temp[y1][x1] = old
                break
    return temp

def normalize(board):
    """returns normalized form of board--all permutations should result in same normal form"""
    return orderNormal(rotateNormal(board))

def shuffle(board):
    digits = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    out = copyBoard(board)

    for old in range(1, 10):
        digit = digits[random.randint(0, len(digits)-1)]
        digits.remove(digit)
        for y, x in fullGen():
            if out[y][x] == old:
                out[y][x] = digit 
            elif out[y][x] == digit:
                out[y][x] = old 
    
    r = random.randint(0, 3)
    return rotate(out, rotates=r) 

def stringify(board):
    """Serializes board (a 2D list) into a flat string divided by semicolons"""
    outString = ""
    for y, x in fullGen():
        outString += str(board[y][x])
        if x == 8 and y != 8:
            outString += ";"
    return outString

def unstringify(boardString):
    """reconstructs board (a 2D list) from a flat string"""
    out = getEmptyBoard()
    temp = boardString.split(";")
    for y, x in fullGen():
        out[y][x] = int(temp[y][x])
    return out 


#---------------TEST SUITE-------------------#

import timeit

def test_rowGen():
    
    # call func, no test data needed
    res = list(rowGen(3, 7, inclusive=False))
    
    # test against hardcoded answer ( a list of y/x tuples)
    if res != [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 8)]:
        print("FAIL. got: ", res)
    else:
        print("passed.")

def test_colGen():
    
    # call func, no test data needed
    res = list(colGen(3, 7, inclusive=False))
    
    # test against hardcoded answer ( a list of y/x tuples)
    if res != [(0, 7), (1, 7), (2, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7)]:
        print("FAIL. got: ", res)
    else:
        print("passed.")

def test_sqrGen():
    
    # call func, no test data needed
    res = list(sqrGen(3, 7, inclusive=False))
    
    # test against hardcoded answer ( a list of y/x tuples)
    if res != [(3, 6), (3, 8), (4, 6), (4, 7), (4, 8), (5, 6), (5, 7), (5, 8)]:
        print("FAIL. got: ", res)
    else:
        print("passed.")

def test_fullGen():
    res = list(fullGen())
    expected = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), 
    (0, 7), (0, 8), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), 
    (1, 7), (1, 8), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), 
    (2, 7), (2, 8), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), 
    (3, 7), (3, 8), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), 
    (4, 7), (4, 8), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), 
    (5, 7), (5, 8), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), 
    (6, 7), (6, 8), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), 
    (7, 7), (7, 8), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), 
    (8, 7), (8, 8)]
    
    if res != expected:
        print("FAIL. Got: ", res)
    else:
        print("passed.")
    


def test_getRowVals():
    # init testboard
    t5 =  [[0,0,0,0,0,0,0,4,8],
        [0,8,6,9,0,0,0,0,1],
        [0,2,0,0,8,3,7,0,0],
        [6,0,0,5,0,0,0,1,7],
        [0,0,0,0,6,0,4,0,0],
        [2,4,0,0,0,7,0,0,5],
        [0,0,2,3,5,0,0,8,0],
        [3,0,0,0,0,8,5,7,0],
        [9,5,0,0,0,0,0,0,0],]
        
    # call func on test board with args
    res = getRowVals(t5, 3, 7, inclusive=False)
    
    # test against hardcoded answer
    if res != [6, 5, 7]:
        print("FAIL. got: ", res)
    else:
        print("passed.")
        
def test_getColVals():
    # init testboard
    t5 =  [[0,0,0,0,0,0,0,4,8],
        [0,8,6,9,0,0,0,0,1],
        [0,2,0,0,8,3,7,0,0],
        [6,0,0,5,0,0,0,1,7],
        [0,0,0,0,6,0,4,0,0],
        [2,4,0,0,0,7,0,0,5],
        [0,0,2,3,5,0,0,8,0],
        [3,0,0,0,0,8,5,7,0],
        [9,5,0,0,0,0,0,0,0],]
        
    # call func on test board with args
    res = getColVals(t5, 1, 1, inclusive=False)
    
    # test against hardcoded answer
    if res != [2, 4, 5]:
        print("FAIL. got: ", res)
    else:
        print("passed.")

def test_getSqrVals():
    # init testboard
    t5 =  [[0,0,0,0,0,0,0,4,8],
        [0,8,6,9,0,0,0,0,1],
        [0,2,0,0,8,3,7,0,0],
        [6,0,0,5,0,0,0,1,7],
        [0,0,0,0,6,0,4,0,0],
        [2,4,0,0,0,7,0,0,5],
        [0,0,2,3,5,0,0,8,0],
        [3,0,0,0,0,8,5,7,0],
        [9,5,0,0,0,0,0,0,0],]
        
    # call func on test board with args
    res = getSqrVals(t5, 4, 4, inclusive=False)
    
    # test against hardcoded answer
    if res != [5, 7]:
        print("FAIL. got: ", res)
    else:
        print("passed.")


    



def quick(inString):
    return timeit.timeit(stmt=inString, globals=globals(), number=10000)
def slow(inString):
    return timeit.timeit(stmt=inString, globals=globals(), number=500) 
def verySlow(inString):
    return timeit.timeit(stmt=inString, globals=globals(), number=50) 
def superSlow(inString):
    return timeit.timeit(stmt=inString, globals=globals(), number=5)

def speedTests():
    import timeit

    def quick(inString):
        return timeit.timeit(stmt=inString, globals=globals(), number=10000)
    def slow(inString):
        return timeit.timeit(stmt=inString, globals=globals(), number=500) 
    def verySlow(inString):
        return timeit.timeit(stmt=inString, globals=globals(), number=50) 

    print("rowGen()", "---",        quick("rowGen(3,3)"))
    print("colGen()", "---",        quick("colGen(3,3)"))
    print("sqrGen()", "---",        quick("sqrGen(3,3)"))
    print("fullGen()", "---",       quick("fullGen()"))
    print()
    print("getRowVals()", "---",    quick("getRowVals(s3,3,3)"))
    print("getColVals()", "---",    quick("getColVals(s3,3,3)"))
    print("getSqrVals()", "---",    quick("getSqrVals(s3,3,3)"))
    print()
    print("getPoss()", "---",       quick("getPoss(s3,3,3)"))
    print("uniqueCheck()", "---",   quick("uniqueCheck(s3,3,3)"))
    print()
    print("===================================")
    print("generateCache()", "---", slow("generateCache(s3)"))
    print("solve()", "---",         slow("solve(s3)"))
    print("checkConsistent()", "---", slow("checkConsistent(s3)"))
    print()
    print("===================================")
    print("generate()", "---", verySlow("generate()"))
    print("carve()", "---", verySlow("carve(f1)"))
    print()
    print("getPuzzle()", "---", verySlow("getPuzzle()"))

def testGen(genFunc):
    board = getEmptyBoard()
    for y, x in genFunc():
        board[y][x] = 'X'
        printBoard(board)
        print('----------------------')


#5/12/22 test results
"""
    rowGen() --- 0.0055575
    colGen() --- 0.0052339
    sqrGen() --- 0.0033147999999999997
    fullGen() --- 0.003064299999999999

    getRowVals() --- 0.0418316
    getColVals() --- 0.03638910000000001
    getSqrVals() --- 0.053771999999999986

    getPoss() --- 0.12813639999999998
    uniqueCheck() --- 8.199947700000001

    ===================================
    generateCache() --- 0.39510630000000013
    solve() --- 21.26534
    checkConsistent() --- 0.23430940000000078

    ===================================
    generate() --- 19.191720000000004
    carve() --- 5.075975199999995

    getPuzzle() --- 21.846923900000007


    NOTES:
    everything builds off the previous primitive. getRowVals() needs rowGen(). 
    getPoss() uses getRowVals, getColVals, getSqrVals.
    uniqueCheck() uses getPoss for every unit 
    generateCache() runs uniqueCheck() for every cell. So the call stack grows multiplicatively.
    
"""

