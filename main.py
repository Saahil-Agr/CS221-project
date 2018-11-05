import numpy as np
import os
from collections import defaultdict
import random
import algos
from setup import setUpUtils
import setup

## Global variables
# How many tiles each player draws at the start
NUM_START_TILES = 21
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

class Util():
    def __init__(self):
        self.anagramMap = defaultdict(list)
        self.letterScores = defaultdict(int)

###############################################################################################
#                                   FIRST WORD
###############################################################################################
'''
Get First word. Chose a first word to play given your tiles. All df the logic here is deferred to the function 
getWordToPlay which can take a letter to pay off. At start there is no letter.
'''

def getFirstWord(algo, util, tiles):
    return algo.getWordToPlay(util,tiles,"")

def placeFirstWordOnBoard(board, first):
    for i in range(len(first)):
        middle = int(MAX_BOARD_SIZE/2)
        col = middle + i
        board[middle][col] = first[i]

if __name__ == '__main__':
    util = Util()
    allTiles = list(setUpUtils(util))
    playertiles = setup.selectRandomTiles(allTiles,NUM_START_TILES)
    board = setup.makeBoard(MAX_BOARD_SIZE)
    print ('the original tiles are: {}'.format(playertiles))
    input('Press enter to run: ')

    ## Initialize the algorithm object
    algo = algos.BFS(MAX_WORDS_PER_SPOT, Spot)
    setup.loadLetterScores(util, algo.getHeuristic)
    #1. Play the first word
    first = getFirstWord(algo, util, playertiles)
    print ("The first word is:",first)
    placeFirstWordOnBoard(board,first)
    setup.outputTrimmedBoard(board)
    setup.removeTiles(playertiles,first)
    print ("remaining tiles : {}".format(playertiles))

    #2. Play remaining words
    while True:
        if algo.playWordOnBoard(util, playertiles,board) == "": break
        trimmedBoard = setup.outputTrimmedBoard(board)
        for row in trimmedBoard: print (*row)
        print ("remaining tiles : {}".format(playertiles))

