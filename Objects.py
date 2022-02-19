from datetime import date

class Player():
    scores = {}

    def __init__(self, name):
        self.name = name
        self.scores = {}

    def addScore(self, index, label, value):
        if index not in self.scores:
            self.scores[index] = {}

        if label not in self.scores[index]:
            self.scores[index][label] = int(value)
        else:
            print('label already in scores', index, label, self.name)


class Game():
    index = 0
    dateStr = ''
    solo = False
    winner = ''
    loser = ''
    scores = {}

    def __init__(self, index, dateStr, solo):
        self.index = int(index)
        self.dateStr = dateStr
        month, day, yr = [int(s) for s in dateStr.split('/')]
        self.date = date(yr, month, day)
        self.solo = solo
        self.winner = ''
        self.loser = ''
        self.scores = {}

    def setScores(self, player, scores):
        self.scores[player] = scores

    def setWinner(self):
        if self.solo:
            self.winner = 'No one -- solo game.'
        elif self.scores['Carl']['Total'] > self.scores['Ali']['Total']:
            self.winner = 'Carl'
            self.loser = 'Ali'
        elif self.scores['Carl']['Total'] < self.scores['Ali']['Total']:
            self.winner = 'Ali'
            self.loser = 'Carl'
        else:
            self.winner = 'A tie?!?! O.o'
            self.loser = 'A tie?!?! O.o'

