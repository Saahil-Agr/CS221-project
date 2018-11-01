import numpy as np
import os
from collections import defaultdict
import random

## Global variables
# How many tiles each player draws at the start
NUM_START_TILES = 15
# How big to make the virtual grid that I populate
MAX_BOARD_SIZE = NUM_START_TILES * 2
# Bananagrams is a complex game. Limit how deep we go
MAX_WORDS_PER_SPOT = 100000
# How big should the tiles be in visualization
TILE_SIZE = 50
# Some constants to store directions
LEFT_RIGHT = 0
# Some constants to store directions
UP_DOWN = 1

class Spot():
    def __init__(self,r,c,dir):
        '''
        :param r: the row of the spot
        :param c: column of the spot
        :param dir: direction to move
        '''
        self.r = r
        self.c = c
        self.dir = dir

class Utils():
    def __init__(self):
        self.anagramMap = defaultdict(list)
        self.letterScores = defaultdict(int)

###############################################################################################
#                                   Setup
###############################################################################################
'''
/* Make Board
 * Make a really large empty board. Make it so big that if we start in
 * the middle no combination of words could take us off the board.
 * Later when visualizing the board we can trim it.
 */
'''
def makeBoard():
    grid = []
    for _ in range(MAX_BOARD_SIZE):
        grid.append([])
        for _ in range(MAX_BOARD_SIZE):
            grid[-1].append(' ')
    return grid

def scoreLetter(ch, count):
    if ch in ['a','e','i','u']:
        return 1
    if count <= 2: return 40
    if count <= 4: return 10
    if count <=9: return 5

    return 3

'''
/* Set Up Utils
 * This function loads the scrabble dictionary, the map
 * of letter scores (the "scores" are made up by Chris and
 * are not part of the game rules) and the game tiles.
 */
'''
#TODO find a function to create vocabulary for english. There should be pre-existing library or dictionary
def setUpUtils(utils): # why is passed by reference here. Needs to understand this to know what name to put
    print("Bananagrams")
    # with open("Collins-Scrabble-Words-2015.txt") as word_file:
    #     valid_words = set(word_file.read().split())
    vocab = set()
    with open("Collins-Scrabble-Words-2015.txt") as f:
        for line in f.readlines()[2:]:
            line = line.rstrip("\n")
            vocab.add(line)
    populateAnagramMap(vocab, utils)
    loadLetterScores(utils)
    return loadLetters()


'''
/* Load Letters
 * Bananagrams uses a carefully chosen count of tiles. I looked
 * up those counts and put them in the file banana-dist.txt. This
 * function reads that file and returns all the tiles as one long
 * string.
 */
'''
#TODO create the file bana-dist and test the below block of code
def loadLetterScores(utils):
    with open("bananagram-tiles.txt") as f:
        for line in f.readlines():
            ch,count = line.split(':')[0], int(line.split(':')[1])
            letterscore = scoreLetter(ch,count)
            utils.letterScores[ch] = letterscore
    return

def loadLetters():
    with open("bananagram-tiles.txt") as f:
        letters = ""
        for line in f.readlines():
            ch,count = line.split(':')[0], int(line.split(':')[1])
            letters += ch*count
    print("loaded letters are: {}".format(letters))
    return letters

'''
For every word we create a map from it's sorted letters to the word. 
Basically this dictionary is a look up for anagrams
'''
def populateAnagramMap(eng_dict,utils):
    for word in eng_dict:
        word = word.upper()
        sorted_words = ''.join(sorted(word)) #sorted function sorts alphabetically and returns a list
        #print (sorted_words)
        if utils.anagramMap[sorted_words]:
            utils.anagramMap[sorted_words].append(word)
        else:
            utils.anagramMap[sorted_words] = [word]
    # print ("the final vocab is {}".format(utils.anagramMap))
    return

'''
Given a pile of tiles randomly select the number without replacement. Return the selected tiles
'''

def selectRandomTiles(pile, num):
    hand = []
    for i in range(num):
        idx = random.randint(0,len(pile) - 1)
        tile = pile[idx]
        del pile[idx]
        hand.append(tile)

    return hand


###############################################################################################
#                                   FIRST WORD
###############################################################################################
'''
Get First word. Chose a first word to play given your tiles. All df the logic here is deferred to the function 
getWordToPlay which can take a letter to pay off. At start there is no letter.
'''

def getFirstWord(utils, tiles):
    return getWordToPlay(utils,tiles,"")

def placeFirstWordOnBoard(board, first):
    for i in range(len(first)):
        middle = int(MAX_BOARD_SIZE/2)
        col = middle + i
        board[middle][col] = first[i]

###############################################################################################
#                                           AI
###############################################################################################
def getWordToPlay(utils, tiles, seed):
    best = ''
    word = ''
    bestscore = 0
    pipeline = []
    pipeline.append(seed)
    depth = 0
    while (not isEmpty(pipeline)):
        soFar = pipeline.pop(0)
        score = getHeuristic(utils,soFar,seed)
        if score > bestscore:
            word = checkForWord(utils,soFar)
        if word != '' and word != best:
            bestscore = score
            best = word
            print ('The new best word is: {}'.format(best))

        idx = len(soFar) - len(seed)
        if idx < len(tiles):
            a = soFar + tiles[idx]
            pipeline.append(a)
            b = soFar + '-'
            pipeline.append(b)

        depth +=1

        if depth == MAX_WORDS_PER_SPOT: break

    return best

def playWordOnBoard(utils, tiles, board):
    bestSpot = (None, None, None)
    best = ''
    bestScore = 0
    playableSpots = getSpots(board, len(tiles))

    for spot in playableSpots:
        seed  = board[spot.r][spot.c]
        word = getWordToPlay(utils, tiles, seed)
        if word != '':
            score = getHeuristic(utils, word,seed)
            if score > bestScore:
                bestSpot = spot
                bestScore = score
                best = word

    if best != '':
        seed = board[bestSpot.r][bestSpot.c]
        used = list(best)
        used.remove(seed)
        used = "".join(used)
        removeTiles(tiles,used)
        orientWord(board,bestSpot,best)
    return best



def getSpots(board, spacing):
    spots = []
    
    for r in range(numRows(board)):
        for c in range(numCols(board)):
            if board[r][c] != '-':
                if checkLeftRight(board,r,c,spacing):
                    found = Spot(r,c,"left_right")
                    spots.append(found)
                if checkUpDown(board,r,c,spacing):
                    found = Spot(r,c,"up_down")
                    spots.append(found)
    return spots



def getHeuristic(utils,soFar,seed):
    score = 0
    for i in range(len(seed), len(soFar),1):
        if soFar[i] != '-':
            ch = soFar[i]
            score += utils.letterScores[ch]
    return score

#TODO need to make these codes better and more pythonic
def checkForWord(utils, soFar):
    base = ''
    for i in soFar:
        if i != '-': base += i
    base = base.upper()
    baseSorted = ''.join(sorted(base))
    if utils.anagramMap[baseSorted]:
        return utils.anagramMap[baseSorted][0]
    return ""


def checkLeftRight(board,row,col,spacing):
    # print (row,col,spacing)
    for dCol in range(-spacing, spacing):
        currCol = col + dCol
        # print(row, currCol)
        try:
            if board[row][currCol] != ' ' and currCol != col: 
                return False
        except IndexError:
            return False
    return True


def checkUpDown(board, row, col, spacing):
    for dRow in range(-spacing, spacing,):
        currRow = row + dRow
        try:
            if board[currRow][col] != ' ' and currRow != row: 
                return False
        except IndexError:
            return False
    return True

###############################################################################################
#                                           Helper Functions
###############################################################################################
def removeTiles(playertiles, playedword):
    playedword = list(playedword.upper())
    for w in playedword:
        if w == '-' : continue
        playertiles.remove(w)
    return playertiles

def countLetters(string):
    count = sum([1 for char in string if char != '-'])
    return count

def orientWord(board, spot, word):
    print(spot,word)
    seed = board[spot.r][spot.c]
    idx = word.index(seed)
    if spot.dir == "left_right":
        startCol = spot.c - idx
        for i,j in enumerate(word):
            board[spot.r][startCol + i] = j
    if spot.dir == "up_down":
        startRow = spot.r - idx
        for i,j in enumerate(word):
            #print(startRow, i, spot.c, word[j])
            board[startRow + i][spot.c] = j

    return

def isEmpty(l):
    return len(l) == 0

def numRows(l):
    return len(l)

def numCols(l):
    '''
    Assumes that each sub list has the same number of elements. Grid representation in lists essentially
    :param l: a list of lists
    :return: length of a sub list of the lists
    '''
    return len(l[0])

###############################################################################################
#                                           Board Visualization
###############################################################################################
def outputTrimmedBoard(board):
    minC = numCols(board) - 1
    maxC = 0
    minR = numRows(board) - 1
    maxR = 0
    for r in range(0, numRows(board)):
        for c in range(0, numCols(board)):
            if board[r][c] != ' ':
                minC = min(minC, c)
                minR = min(minR, r)
                maxC = max(maxC, c)
                maxR = max(maxR, r)
    newC = maxC - minC + 1
    newR = maxR - minR + 1
    trimmed = [[' ' for ii in range(newC)] for i in range(newR)]
    for r in range(newR):
        for c in range(newC):
            trimmed[r][c] = board[minR + r][minC + c]
    return trimmed


if __name__ == '__main__':
    utils = Utils()
    allTiles = list(setUpUtils(utils))
    playertiles = selectRandomTiles(allTiles,21)
    board = makeBoard()
    print ('the original tiles are: {}'.format(playertiles))
    input('Press enter to run: ')
    #1. Play the first word
    first = getFirstWord(utils, playertiles)
    print ("The first word is:",first)
    placeFirstWordOnBoard(board,first)
    #outputTrimmedBoard(board)
    removeTiles(playertiles,first)
    print ("remaining tiles : {}".format(playertiles))

    #2. Play remaining words
    while True:
        if playWordOnBoard(utils, playertiles,board) == "": break
        trimmedBoard = outputTrimmedBoard(board)
        for row in trimmedBoard: print (*row)
        print ("remaining tiles : {}".format(playertiles))

