import reportlab
from reportlab.pdfgen import canvas
from datetime import date
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import Objects

# Import scores csv
#   first row: dates in format MM/dd/yyyy
#   second row: game index
#   third row: player name
#   4th - 21st rows: yatzy category scores
# Output games dict - {}
def parse_games(scoreFile):
    # Open csv file of score data
    f = open(scoreFile, 'r')
    # Parse out all rows
    rawData = [row.split(',') for row in f.read().strip().split('\n')]
    f.close()

    dateRow = rawData[0][1:]                    # first row is dates of games in MM/dd/yyyy format
    gameNumRow = rawData[1][1:]                 # second row are game indexes (1 - n)
    playerRow = rawData[2][1:]                  # third row are player names
    scoreRows = [i[1:] for i in rawData[3:]]    # remaining rows are scores
                                                # (skips first column of category labels)

    # List out dates of games excluding blank cells
    allDates = [i for i in dateRow if len(i) > 0]
    # List out all score categories (also used in pdf build)
    global categories
    categories = [i[0] for i in rawData[3:] if len(i) > 0]
    print(categories)

    # Declare player objects and add to list of players
    carl = Objects.Player('Carl')
    ali = Objects.Player('Ali')
    players = [carl, ali]

    # Dict to return at the end
    # {game index (int): Game object}
    games = {}

    for a, dateStr in enumerate(dateRow):
        # If we found a new game
        if len(dateStr) > 0:
            # If we aren't at the end of the row and the next cell in the date row is blank
            # (indicating a 2 person game as opposed to a solo game)
            if a < (len(dateRow) - 1) and len(dateRow[a + 1]) == 0:
                soloGame = False
                # add player names to the list of this games players
                thesePlayers = [playerRow[a], playerRow[a + 1]]
            else:
                soloGame = True
                # add only this column's player to list of this games players
                thesePlayers = [playerRow[a]]

            # set game index (same column as date but in gameNumRow)
            gameIndex = int(gameNumRow[a])
            # Declare new game object
            thisGame = Objects.Game(gameIndex, dateStr, soloGame)
            # Add to games dict
            games[gameIndex] = thisGame

            # Add player scores to player objects
            for name in thesePlayers:
                # set player and index where score values should be found
                # for this player in this game
                if name == 'Carl':
                    player = carl
                    playerIndex = a
                elif name == 'Ali':
                    player = ali
                    if len(thesePlayers) > 1:
                        playerIndex = a + 1
                    else:
                        playerIndex = a

                # Add player scores
                for b, row in enumerate(scoreRows):
                    player.addScore(gameIndex, categories[b], row[playerIndex])

                # Add scores to this game object
                thisGame.setScores(name, player.scores[gameIndex])

            # find winner of the game and set it in game object
            thisGame.setWinner()

    return games

def draw_pdf(games, fileName):
    # *********
    # FIRST PAGE
    # *********
    c = reportlab.pdfgen.canvas.Canvas(fileName)                                                    # Create New Page
    imagePath = 'Carl&Aliv1.jpg'
    c.drawInlineImage(imagePath, 0.5 * inch, 8.75 * inch, width=7.5 * inch, height=2.5 * inch)      # Draw Title Image
    c.setFont('Times-BoldItalic', 20)                                                               # Set title font
    c.drawCentredString(4.25 * inch, 8.25 * inch, 'STATS AS OF ' + lastGameDate)                    # Draw Title

    totalWidth = 400                                                                                # Set total bar width

    # Games Won
    winners = [games[g].winner for g in games if games[g].winner.find('No one') == -1]              # List all winners
    carlWins = sum([int(i == 'Carl') for i in winners])                                             # Find wins for carl
    aliWins = sum([int(i == 'Ali') for i in winners])                                               # Find wins for ali

    carlWidth = totalWidth * float(carlWins) / len(winners)                     # Calc carl's portion of the bar
    aliWidth = totalWidth * float(aliWins) / len(winners)                       # Calc ali's portion of the bar

    y = 7.5 * inch                                                              # Set initial y position on page

    c.setFont('Times-Bold', 14)                                                 # Set title font
    c.drawString(inch * 0.5, 8.0 * inch, 'Games Won')                           # Draw title
    c.setFillColorRGB(1, 0, 0)                                                  # Set Carl's color
    c.drawString(inch * 0.5, y + 10, 'Carl')                                    # Draw Carl's name
    c.rect(100, y, carlWidth, 30, fill=1)                                       # Draw carl's rectangle
    c.setFillColorRGB(0, 0, 1)                                                  # Set Ali's color
    c.drawString(inch * 7.4, y + 10, 'Ali')                                     # Draw Ali's name
    c.rect(carlWidth + 100, y, aliWidth, 30, fill=1)                            # Draw Ali's rectangle
    c.setFillColorRGB(1, 1, 1)                                                  # Set color for value labels
    c.drawString(100 + (carlWidth / 2), y + 10, str(carlWins))                  # Draw value label for Carl
    c.drawString(100 + carlWidth + (aliWidth / 2), y + 10, str(aliWins))        # Draw value label for Ali

    print("Carl has won: %d/%d games (%.2f%s), Ali has won %d/%d games (%.2f%s)"
          % (carlWins, len(winners), float(carlWins) * 100.0 / float(len(winners)), '%', aliWins, len(winners),
             float(aliWins) * 100.0 / float(len(winners)), '%'))

    # Yatzys Count
    carlYatzys = [int(games[game].scores['Carl']['Yatzy'] == 50)                # Calc carl yatzys
                  for game in games if 'Carl' in games[game].scores]
    aliYatzys = [int(games[game].scores['Ali']['Yatzy'] == 50)                  # Calc ali yatzys
                 for game in games if 'Ali' in games[game].scores]

    carlWidth = (float(sum(carlYatzys)) / len(carlYatzys)) * totalWidth         # Calculate Carl rectangle width
    aliWidth = (float(sum(aliYatzys)) / len(aliYatzys)) * totalWidth            # Calculate Ali rectangle width

    y = 6.5 * inch                                                              # Set initial y position

    c.setFont('Times-Bold', 14)                                                 # Set Header font
    c.setFillColorRGB(0, 0, 0)                                                  # Set header color = Black
    c.drawString(inch * 0.5, 7 * inch, 'Yatzys')                                # Draw Header

    c.setFillColorRGB(1, 1, 1)                                                  # Set color = white
    c.rect(100, y, totalWidth, 30, fill=1)                                      # Draw background white rectangle
    c.setFillColorRGB(1, 0, 0)                                                  # Set carls color
    c.drawString(inch * 0.5, y + 10, 'Carl')                                    # Write "Carl"
    c.rect(100, y, carlWidth, 30, fill=1)                                       # Draw carl's rectangle
    c.setFillColorRGB(1, 1, 1)                                                  # Set color = white
    c.drawString(100 + (carlWidth / 2), y + 10, str(sum(carlYatzys)))           # Overlay value label on rectangle
    c.setFillColorRGB(0, 0, 0)                                                  # Set color = Black
    c.drawString(inch * 7, y + 10, str(len(carlYatzys)) + ' games')             # Write total game count at right side of rect

    y = 6.0 * inch                                                              # Set initial y position

    c.setFillColorRGB(1, 1, 1)                                                  # Set color = white
    c.rect(100, y, totalWidth, 30, fill=1)                                      # Draw background white rectangle
    c.setFillColorRGB(0, 0, 1)                                                  # Set Ali's color = blue
    c.drawString(inch * 0.5, y + 10, 'Ali')                                     # Write "Ali"
    c.rect(100, y, aliWidth, 30, fill=1)                                        # Draw Ali's rectangle
    c.setFillColorRGB(1, 1, 1)                                                  # Set color = white
    c.drawString(100 + (aliWidth / 2), y + 10, str(sum(aliYatzys)))             # Overlay value label on rectangle
    c.setFillColorRGB(0, 0, 0)                                                  # Set color = Black
    c.drawString(inch * 7, y + 10, str(len(aliYatzys)) + ' games')              # Write total game ct at right side of rect

    print("Carl has gotten %d Yatzys in %d games (%.2f%s). Ali has gotten %d Yatzys in %d games (%.2f%s)"
          % (
              sum(carlYatzys), len(carlYatzys), sum(carlYatzys) * 100.0 / len(carlYatzys), '%', sum(aliYatzys),
              len(aliYatzys),
              sum(aliYatzys) * 100.0 / len(aliYatzys), '%'))

    # Score Counts
    carlScores = [games[game].scores['Carl']['Total'] for game in games         # Get all of Carl's scores
                    if 'Carl' in games[game].scores]
    aliScores = [games[game].scores['Ali']['Total'] for game in games           # Gat all of Ali's scores
                    if 'Ali' in games[game].scores]
    carlAvg = round(sum(carlScores) / len(carlScores), 2)                       # Calc carl's avg score
    aliAvg = round(sum(aliScores) / len(aliScores), 2)                          # Calc ali's avg score

    y = 5.0 * inch                                                              # Set initial y position

    c.setFont('Times-Bold', 14)                                                 # Set Header font
    c.setFillColorRGB(0, 0, 0)                                                  # Set header color = Black
    c.drawString(inch * 0.5, 5.5 * inch, 'Min/Avg/Max Scores')                  # Draw Header

    c.setFillColorRGB(1, 1, 1)                                                  # Set color = white
    c.rect(100, y, totalWidth, 30, fill=1)                                      # Draw background white rectangle
    c.setFillColorRGB(1, 0, 0)                                                  # Set carl's color
    c.drawString(inch * 0.5, y + 10, 'Carl')                                    # Write "Carl"
    c.rect(100 + (min(carlScores)), y,
           max(carlScores) - min(carlScores), 30, fill=1)                       # Draw carl's rectangle (min score - avg score)
    c.rect(100 + carlAvg, y, max(carlScores) - carlAvg, 30, fill=1)             # Draw carl's rectangle (avg score - max score)
    c.setFillColorRGB(0, 0, 0)                                                  # Set color = black
    c.drawString(90 + (min(carlScores)), y - 12, str(min(carlScores)))          # Draw Min Score under rectangle
    c.drawString(90 + (carlAvg), y - 12, str(carlAvg))                          # Draw Avg Score under rectangle
    c.drawString(90 + (max(carlScores)), y - 12, str(max(carlScores)))          # Draw Max Score under rectangle

    y = 4.35 * inch                                                             # Set initial y position

    c.setFillColorRGB(1, 1, 1)                                                  # Set color = white
    c.rect(100, y, totalWidth, 30, fill=1)                                      # Draw background white rectangle
    c.setFillColorRGB(0, 0, 1)                                                  # Set ali's color
    c.drawString(inch * 0.5, y + 10, 'Ali')                                     # Write "Ali"
    c.rect(100 + (min(aliScores)), y,
           max(aliScores) - min(aliScores), 30, fill=1)                         # Draw rectangle (min score - avg score)
    c.rect(100 + (sum(aliScores) / len(aliScores)), y,
           max(aliScores) - aliAvg, 30, fill=1)                                 # Draw rectangle (avg score - max score)
    c.setFillColorRGB(0, 0, 0)                                                  # Set color = black
    c.drawString(90 + (min(aliScores)), y - 12, str(min(aliScores)))            # Draw Min Score under rectangle
    c.drawString(90 + aliAvg, y - 12, str(aliAvg))                              # Draw Avg Score under rectangle
    c.drawString(90 + (max(aliScores)), y - 12, str(max(aliScores)))            # Draw Max Score under rectangle

    print("Carl's average score is %d. Carl's maximum score is %d. Carl's minimum score is %d."
          % (sum(carlScores) / len(carlScores), max(carlScores), min(carlScores)))
    print("Ali's average score is %d. Ali's maximum score is %d. Ali's minimum score is %d."
          % (sum(aliScores) / len(aliScores), max(aliScores), min(aliScores)))

    # Bonus Counts
    carlBonus = [int(games[game].scores['Carl']['Bonus'] == 35)                 # calc all times Carl got bonus
                 for game in games if 'Carl' in games[game].scores]
    aliBonus = [int(games[game].scores['Ali']['Bonus'] == 35)                   # calc all times ali got bonus
                for game in games if 'Ali' in games[game].scores]
    carlWidth = (float(sum(carlBonus)) / len(carlBonus)) * totalWidth           # Calculate Carl rectangle width
    aliWidth = (float(sum(aliBonus)) / len(aliBonus)) * totalWidth              # Calculate Ali rectangle width

    y = 3.25 * inch                                                             # Set inital y position

    c.setFont('Times-Bold', 14)                                                 # Set Header font
    c.setFillColorRGB(0, 0, 0)                                                  # Set header color = Black
    c.drawString(inch * 0.5, 3.75 * inch, 'Bonus Count')                        # Draw Header

    c.setFillColorRGB(1, 1, 1)                                                  # Set color = white
    c.rect(100, y, totalWidth, 30, fill=1)                                      # Draw white rectangle
    c.setFillColorRGB(1, 0, 0)                                                  # Set carls color
    c.drawString(inch * 0.5, y + 10, 'Carl')                                    # Write "Carl"
    c.rect(100, y, carlWidth, 30, fill=1)                                       # Draw carls rectangle
    c.setFillColorRGB(1, 1, 1)                                                  # Set color = white
    c.drawString(100 + (carlWidth / 2), y + 10, str(sum(carlBonus)))            # Overlay value label on rectangle
    c.setFillColorRGB(0, 0, 0)                                                  # Set color = Black
    c.drawString(inch * 7, y + 10, str(len(carlBonus)) + ' games')              # Write total game ct at right side of rect

    y = 2.75 * inch                                                             # Set initial y position
    c.setFillColorRGB(1, 1, 1)                                                  # Set color = white
    c.rect(100, y, totalWidth, 30, fill=1)                                      # Draw background white rectangle
    c.setFillColorRGB(0, 0, 1)                                                  # Set ali's color
    c.drawString(inch * 0.5, y + 10, 'Ali')                                     # Write "Ali"
    c.rect(100, y, aliWidth, 30, fill=1)                                        # Draw Ali's rectangle
    c.setFillColorRGB(1, 1, 1)                                                  # Set color = white
    c.drawString(100 + (aliWidth / 2), y + 10, str(sum(aliBonus)))              # Overlay value label on rectangle
    c.setFillColorRGB(0, 0, 0)                                                  # Set color = Black
    c.drawString(inch * 7, y + 10, str(len(aliBonus)) + ' games')               # Write total game ct at right side of rect

    print("Carl has gotten the bonus %d/%d times (%.2f%s). Ali has gotten the bonus %d/%d times (%.2f%s)"
          % (sum(carlBonus), len(carlBonus), sum(carlBonus) * 100.0 / len(carlBonus), '%', sum(aliBonus), len(aliBonus),
             sum(aliBonus) * 100.0 / len(aliBonus), '%'))


    # Scratch Counts
    catNoBonus = categories
    del catNoBonus[catNoBonus.index('Bonus')]
    del catNoBonus[catNoBonus.index('Top Total')]
    del catNoBonus[catNoBonus.index('Total')]

    # Scratch list [[category 1, scratch ct], [category 2, scratch ct]]
    carlScratches = [[c, 0] for c in catNoBonus]
    aliScratches = [[c, 0] for c in catNoBonus]

    for g in games:
        thisGame = games[g]
        for (player, score) in thisGame.scores.items():
            for a, cat in enumerate(catNoBonus):
                if player == 'Carl':
                    carlScratches[a][1] += int(score[cat] == 0)
                else:
                    aliScratches[a][1] += int(score[cat] == 0)

            #for a in catNoBonus:
            #    scratches[player][a] += int(score[a] == 0)

    # get second value in the list for sorting
    def getVal(row):
        return row[1]

    carlScratches.sort(key=getVal, reverse=True)
    carlScratchAvg = sum([cat[1] for cat in carlScratches]) / len(carlScores)
    aliScratches.sort(key=getVal, reverse=True)
    aliScratchAvg = sum([cat[1] for cat in aliScratches]) / len(aliScores)

    scratchStr1 = "%s scratched an average of %.2f categories per game."
    scratchStr2 = "%s scratches %s %.1f%s of the time."

    y = 2 * inch                                                             # Set initial y position

    c.setFont('Times-Bold', 14)
    c.setFillColorRGB(1, 0, 0)                                                  # Set carls color
    c.drawString(inch * 0.5, y + 15, scratchStr1 %('Carl', carlScratchAvg))     # Write carl's scratch avg
    c.drawString(inch * 0.5, y, scratchStr2 % ('Carl', carlScratches[0][0],
                (carlScratches[0][1] * 100.0 / len(carlScores)), '%'))               # Write carl's 1st scratch category
    c.drawString(inch * 0.5, y - 15, scratchStr2 % ('Carl', carlScratches[1][0],
                (carlScratches[1][1] * 100.0 / len(carlScores)), '%'))               # Write carl's 2nd scratch category
    c.drawString(inch * 0.5, y - 30, scratchStr2 % ('Carl', carlScratches[2][0],
                (carlScratches[2][1] * 100.0 / len(carlScores)), '%'))               # Write carl's 3rd scratch category

    y = 1 * inch                                                                     # Set initial y position

    c.setFillColorRGB(0, 0, 1)                                                       # Set alis color
    c.drawString(inch * 0.5, y + 15, scratchStr1 % ('Ali', aliScratchAvg))           # Write ali's scratch avg
    c.drawString(inch * 0.5, y, scratchStr2 % ('Ali', aliScratches[0][0],
                (aliScratches[0][1] * 100.0 / len(aliScores)), '%'))                 # Write ali's 1st scratch category
    c.drawString(inch * 0.5, y - 15, scratchStr2 % ('Ali', aliScratches[1][0],
                (aliScratches[1][1] * 100.0 / len(aliScores)), '%'))                 # Write ali's 2nd scratch category
    c.drawString(inch * 0.5, y - 30, scratchStr2 % ('Ali', aliScratches[2][0],
                (aliScratches[2][1] * 100.0 / len(aliScores)), '%'))                 # Write ali's 3rd scratch category

    print("Carl scratches an average of %.2f categories per game." % (
            sum([cat[1] for cat in carlScratches]) / len(carlScores)))
    print("Ali scratches an average of %.2f categories per game." % (
                sum([cat[1] for cat in aliScratches]) / len(aliScores)))


    c.showPage()

    # HISTOGRAMS

    # Input x (float) - starting x position on the page where the graph will be drawn
    # y (float) - starting y position on the page where the graph will be drawn
    # scores (list ints) - list of scores to be drawn on the histogram
    # color (list of 3 ints, RGB) - color corresponding to the player whose scores are being drawn
    # maximum (int) - maximum value on the y-axis (if not given, default used is maximum of the scores)
    def drawHistogram(x=0.5*inch, y=7*inch, scores=[], color=[1, 1, 1], maximum=0):
        # Create dictionary to count the number of occurances of each score
        scoreDict = dict.fromkeys(scores, 0)
        for score in scoreDict:
            scoreDict[score] = sum([int(i == score) for i in scores])

        # if no max given, use maximum occurances of the scores in the dictionary
        if maximum == 0:
            maximum = max(list(scoreDict.values()))

        # List out unique score values
        scoreKeys = list(scoreDict.keys())
        scoreKeys.sort()

        # Set size of the histogram
        height = 50
        width = 475

        c.setFont('Times-Bold', 12)
        c.setFillColorRGB(0, 0, 0)                                      # Set color = black
        c.line(x, y, x, y + height)                                     # draw y axis
        c.line(x, y, x + width, y)                                      # draw x axis
        c.drawString(x - 15, y + height, str(maximum))                  # Draw maximum value label on yaxis
        c.drawString(x - 15, y + int(height/2), str(int(maximum/2)))    # Draw 1/2 of maximum value label on yaxis
        c.setFillColorRGB(color[0], color[1], color[2])                 # Set color to players color

        # Set where first bar will start (will move as bars are drawn)
        movingX = x + 2
        # Set width of the bars (total histogram width / number of unique score values)
        barW = (width / len(scoreKeys)) - 2
        for a, score in enumerate(scoreKeys):
            barH = height * (scoreDict[score] / maximum)                # calc bar height
            c.rect(movingX, y + 1, barW, barH, fill=1)                  # Draw this bar
            c.drawString(movingX + (barW / 2), y - 12, str(score))      # Write score under bar
            movingX += barW + 2                                         # Shift moving starting point for next bar

    # Drawing histograms

    # Find player scores
    carlScores = [games[game].scores['Carl'] for game in games if 'Carl' in games[game].scores]
    aliScores = [games[game].scores['Ali'] for game in games if 'Ali' in games[game].scores]

    for a, category in enumerate(catNoBonus):
        if a % 3 == 0:
            if a > 0:
                # Go to new page after 3 histograms
                c.showPage()

            c.setFont('Times-Bold', 18)                                 # Page Header font
            c.setFillColorRGB(0, 0, 0)                                  # Set color = Black
            c.drawCentredString(4.25 * inch, 10.5 * inch, 'Histograms') # Write Header on new page

        c.setFont('Times-Bold', 14)                                     # Category Header font
        c.setFillColorRGB(0, 0, 0)                                      # Set color = Black
        y = (10 - (a % 3) * 3) * inch                                   # Set y position
        c.drawString(inch * 0.5, y, category)                           # Write Category Header

        # Get average values for both players for this category
        carlAvg = round(sum([score[category] for score in carlScores if score[category] > 0]) / len(
            [score[category] for score in carlScores if score[category] > 0]), 2)
        aliAvg = round(sum([score[category] for score in aliScores if score[category] > 0]) / len(
            [score[category] for score in aliScores if score[category] > 0]), 2)

        # Write averages
        c.drawString(inch * 0.5, y - 20, 'Avg: ' + str(round((carlAvg + aliAvg) / 2, 2)))   # Write Both Avg
        c.setFillColorRGB(1, 0, 0)
        c.drawString(inch * 0.5 + 100, y - 20, 'Carl Avg: ' + str(carlAvg))                 # Write Carl Avg
        c.setFillColorRGB(0, 0, 1)
        c.drawString(inch * 0.5 + 250, y - 20, 'Ali Avg: ' + str(aliAvg))                   # Write Ali Avg

        # Draw Carl's histogram
        drawHistogram(y= y - 85, scores=[score[category] for score in carlScores], color=(1, 0, 0))
        # Draw Ali's histogram
        drawHistogram(y= y - 160, scores=[score[category] for score in aliScores], color=(0, 0, 1))

    c.showPage()

    # SCORES OVER TIME

    # (x, y) pairs will be (days from first day, score)
    def makeGraph(y, points=[], xLabels=[], color=[1, 1, 1], connect=True):
        height = 100
        width = 450
        x = inch
        c.setFillColorRGB(0, 0, 0)                              # Set color = black
        c.line(x, y, x, y + height)                             # draw y axis
        c.line(x - 10, y, x + 10, y)                            # draw tiny line on y axis
        c.line(x - 10, y + height / 3, x + 10, y + height / 3)  # draw tiny line on y axis
        c.line(x - 10, y + 2 * height / 3, x + 10, y + 2 * height / 3)  # draw tiny line on y axis
        c.line(x - 10, y + height, x + 10, y + height)          # draw tiny line on y axis
        c.line(x, y, x + width, y)                              # draw x axis
        c.setFont('Times-Bold', 10)                             # set font
        c.drawString(x, y - 12, xLabels[0])                     # Write x axis label 1
        c.drawString(x + (450 / 3), y - 12, xLabels[1])         # Write x axis label 2
        c.drawString(x + (450 * 2 / 3), y - 12, xLabels[2])     # Write x axis label 3
        c.drawString(x + 450, y - 12, xLabels[3])               # Write x axis label 4

        # Get all x and y points for max/min calcs
        allY = [pts[1] for pts in points]
        allX = [pts[0] for pts in points]

        minY = min(allY)
        maxY = max(allY) + 10
        maxX = max(allX)
        yLabels = [str(int(minY)),                              # y axis labels
                   str(int(minY + ((maxY - minY) / 3))),
                   str(int(minY + ((maxY - minY) * 2 / 3))),
                   str(int(maxY))]

        c.drawString(inch * 0.5, y, yLabels[0])                 # Write lowest y axis label
        c.drawString(inch * 0.5, y + 33, yLabels[1])            # Write y axis label 1
        c.drawString(inch * 0.5, y + 66, yLabels[2])            # Write y axis label 2
        c.drawString(inch * 0.5, y + 100, yLabels[3])           # Write y axis label 3

        c.setFillColorRGB(color[0], color[1], color[2])         # Set players color
        for a, pts in enumerate(points):
            xRaw, yRaw = pts
            # Need to convert raw values into relative values
            xPt = x + (xRaw * width / maxX)
            yPt = y + (yRaw - minY) * height / (maxY - minY)

            c.circle(xPt, yPt, 5, stroke=1, fill=1)             # Draw circle

            if connect:                                         # If we want to connect the points
                if a > 0:
                    c.line(xPt, yPt, lastX, lastY)              # connect this point w/ last point
                lastX = xPt
                lastY = yPt

    # Draw score vs time graphs

    c.setFont('Times-Bold', 18)                                         # Page Header font
    c.setFillColorRGB(0, 0, 0)                                          # Set color = Black
    c.drawCentredString(inch * 4.25, 10.5 * inch, 'Scores Over Time')   # Write Page Header

    c.setFont('Times-Bold', 14)                                         # Set graph header font
    y = 10 * inch                                                       # Set initial y value
    c.drawString(inch * 0.5, y + 15, "Carl Scores")                     # Write Graph Header

    gameIndexes = list(games.keys())
    gameIndexes.sort()

    # Get score values for carl
    carlScores = [[games[game].date, games[game].scores['Carl']['Total']]
                  for game in gameIndexes if 'Carl' in games[game].scores]
    # Date of 1st game
    firstDate = carlScores[0][0]
    # 1st, last and 2 middle dates for labeling the x-axis
    xLabels = [str(carlScores[0][0]), str(carlScores[int(len(carlScores) / 3)][0]),
               str(carlScores[int(len(carlScores) * 2 / 3)][0]), str(carlScores[-1][0])]
    # convert (date, score) pairs into (days from start, score) pairs
    relativePts = [[(row[0] - firstDate).days, row[1]] for row in carlScores]
    # Make carl's graph
    makeGraph(y - 110, relativePts, xLabels, (1, 0, 0), connect=False)

    c.setFont('Times-Bold', 14)                                         # Set graph Header font
    c.setFillColorRGB(0, 0, 0)                                          # Set color = Black
    y = 7.5 * inch                                                      # Set y position
    c.drawString(inch * 0.5, y + 15, "Ali Scores")                      # Write Graph Header

    # Get score values for ali
    aliScores = [[games[game].date, games[game].scores['Ali']['Total']]
                 for game in gameIndexes if 'Ali' in games[game].scores]
    # Get 1st date value from scores
    firstDate = aliScores[0][0]
    # 1st, last and 2 middle dates for labeling the x-axis
    xLabels = [str(aliScores[0][0]), str(aliScores[int(len(carlScores) / 3)][0]),
               str(aliScores[int(len(carlScores) * 2 / 3)][0]), str(aliScores[-1][0])]
    # convert (date, score) pairs into (days from start, score) pairs
    relativePts = [[(row[0] - firstDate).days, row[1]] for row in aliScores]
    # Make ali's graph
    makeGraph(y - 110, relativePts, xLabels, (0, 0, 1), connect=False)

    c.setFont('Times-Bold', 14)                                         # Graph Header font
    c.setFillColorRGB(0, 0, 0)                                          # Set color = Black
    y = 5 * inch                                                        # Set y value
    c.drawString(inch * 0.5, y + 15, "Carl Moving Average")             # Write Graph Header

    # Moving average points to be graphed
    avgPts = []
    # Running total value
    total = 0.0
    for a, row in enumerate(carlScores):
        date, val = row
        total += val
        avg = total / (a + 1)
        avgPts += [[date, avg]]

    firstDate = avgPts[0][0]
    # Build labels for the x-axis from the first date, last date, and 2 middle dates
    xLabels = [str(carlScores[0][0]), str(carlScores[int(len(carlScores) / 3)][0]),
               str(carlScores[int(len(carlScores) * 2 / 3)][0]), str(carlScores[-1][0])]
    # convert (date, score) pairs into (days from start, score) pairs
    relativePts = [[(row[0] - firstDate).days, row[1]] for row in avgPts]
    # Draw moving avg graph for Carl
    makeGraph(y - 110, relativePts, xLabels, (1, 0, 0), connect=True)

    c.setFont('Times-Bold', 14)                                         # Set Graph Header font
    c.setFillColorRGB(0, 0, 0)                                          # Set color = Black

    y = 2.5 * inch                                                      # Set y position

    c.drawString(inch * 0.5, y + 15, "Ali Moving Average")              # Write Graph Header

    # Moving average points to be graphed
    avgPts = []
    # Running total value
    total = 0.0
    for a, row in enumerate(aliScores):
        date, val = row
        total += val
        avg = total / (a + 1)
        avgPts += [[date, avg]]

    firstDate = avgPts[0][0]
    # Build labels for the x-axis from the first date, last date, and 2 middle dates
    xLabels = [str(aliScores[0][0]), str(aliScores[int(len(aliScores) / 3)][0]),
               str(aliScores[int(len(aliScores) * 2 / 3)][0]), str(aliScores[-1][0])]
    # convert (date, score) pairs into (days from start, score) pairs
    relativePts = [[(row[0] - firstDate).days, row[1]] for row in avgPts]
    # draw ali's moving average point graph
    makeGraph(y - 110, relativePts, xLabels, (0, 0, 1), connect=True)

    c.showPage()
    c.save()

if __name__ == '__main__':
    scoreFilePath = 'Yatzy Raw Data.csv'
    games = parse_games(scoreFilePath)

    # Get the date of the last game played
    gameIndexes = list(games.keys())
    gameIndexes.sort()
    lastGame = games[gameIndexes[-1]]
    lastGameDate = lastGame.dateStr.replace('/', '-')
    # Assign pdf file name
    fileName = 'Yatzy Results ' + lastGameDate + '.pdf'
    # Create pdf
    draw_pdf(games, fileName)

