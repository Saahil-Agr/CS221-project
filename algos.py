import os
from collections import defaultdict
import random
import setup

class SearchAlgo():
    # defining an abstraction of a search algorithm. Specific algorithms should have the functions below

    # function to return the score of the word based on a defined heurestic. Takes in the word to be evaluated,
    def getHeuristic(self, ch, count): raise NotImplementedError("Override me")

    def getWordToPlay(util, tiles, seed): raise NotImplementedError("Override me")

    # Since different styles of algorithm will have different simulation steps we define a sepsrate simulate for each algos.
    # Ideal would be to define a simulate that is common across algos but can be hard specially with different styles of algo.
    def Simulate(self): raise NotImplementedError("Override me")

    ## Functions common across all algos

    # TODO need to make these codes better and more pythonic
    def checkForWord(self, util, soFar):
        base = ''
        for i in soFar:
            if i != '-': base += i
        base = base.upper()
        baseSorted = ''.join(sorted(base))
        if util.anagramMap[baseSorted]:
            return util.anagramMap[baseSorted][0]
        return ""

    def checkLeftRight(self, board, row, col, spacing):
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

    def checkUpDown(self, board, row, col, spacing):
        for dRow in range(-spacing, spacing, ):
            currRow = row + dRow
            try:
                if board[currRow][col] != ' ' and currRow != row:
                    return False
            except IndexError:
                return False
        return True

    # The function below checks for each playable spot on the board,

class BFS(SearchAlgo):

    def __init__(self, max_depth, Spot):
        self.max_depth = max_depth
        self.Spots = Spot

    def getWordToPlay(self, util, tiles, seed):
        best = ''
        word = ''
        bestscore = 0
        pipeline = []
        pipeline.append(seed)
        depth = 0
        while (not setup.isEmpty(pipeline)):
            soFar = pipeline.pop(0)
            score = self.getScore(util, soFar, seed)
            if score > bestscore:
                word = self.checkForWord(util, soFar)
            if word != '' and word != best:
                bestscore = score
                best = word
                print('The new best word is: {}'.format(best))

            idx = len(soFar) - len(seed)
            if idx < len(tiles):
                a = soFar + tiles[idx]
                pipeline.append(a)
                b = soFar + '-'
                pipeline.append(b)

            depth += 1

            if depth == self.max_depth: break

        return best

    def playWordOnBoard(self, util, tiles, board):
        bestSpot = (None, None, None)
        best = ''
        bestScore = 0
        playableSpots = self.getSpots(board, len(tiles))

        for spot in playableSpots:
            seed = board[spot.r][spot.c]
            word = self.getWordToPlay(util, tiles, seed)
            if word != '':
                score = self.getScore(util, word, seed)
                if score > bestScore:
                    bestSpot = spot
                    bestScore = score
                    best = word

        if best != '':
            seed = board[bestSpot.r][bestSpot.c]
            used = list(best)
            used.remove(seed)
            used = "".join(used)
            setup.removeTiles(tiles, used)
            setup.orientWord(board, bestSpot, best)
        return best

    #A function that returns a list of all spots that can be used by the algorithm.#
    #TODO check if this will be required by all algos or is specific to BFS.
    def getSpots(self, board, spacing):
        spots = []

        for r in range(setup.numRows(board)):
            for c in range(setup.numCols(board)):
                if board[r][c] != '-':
                    if self.checkLeftRight(board, r, c, spacing):
                        found = self.Spots(r, c, "left_right")
                        spots.append(found)
                    if self.checkUpDown(board, r, c, spacing):
                        found = self.Spots(r, c, "up_down")
                        spots.append(found)
        return spots

    ## Returns the score corresponding to eh
    def getScore(self, util,soFar,seed):
        score = 0
        for i in range(len(seed), len(soFar), 1):
            if soFar[i] != '-':
                ch = soFar[i]
                score += util.letterScores[ch]
        return score

    # It is called only once during the setup to save scores corresponding to each alphabet basis the
    # frequency of occurrence.
    def getHeuristic(self, ch, count):
        '''
        :param ch: alphabet for which score is to be determined
        :param count: count of those alphabets int he game
        :return: heurestic score value
        '''
        if ch in ['a', 'e', 'i', 'u']:
            return 1
        if count <= 2: return 40
        if count <= 4: return 10
        if count <= 9: return 5

        return 3