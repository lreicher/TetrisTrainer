# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

# KRT 17/06/2012 rewrite event detection to deal with mouse use

import random, time, pygame, sys
from pygame.locals import *
import copy
import goap
import metrics
import numpy as np
#import goap

FPS = 25
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '.'
features = []
labels = []
# FOR TESTING -- SAME PIECE ORDER
#seed = random.random()
#print(seed)

MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ = 0.1

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)
EGGSHELL    = (94, 92, 84)
DEEPSPACE   = (58, 96, 110)
WEIRDGREEN  = (170, 174, 142)
PUMPKIN  = (247, 120, 22)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS      = (     BLUE,      GREEN,      RED,      YELLOW)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
assert len(COLORS) == len(LIGHTCOLORS) # each color must have light color

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

PIECES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetromino')

    #_world = goapy.Planner('right_of_goal', 'left_of_goal', 'above_goal', 'cw_of_goal', 'ccw_of_goal')
    #we may need to know where we want the piece to go by this point.
    #do we decide where the next piece needs to be by assigning it to the best position after the last one? how do we handle the first piece?
    #it seems like this goap is made to run around putting out fires with whatever buckets of water available
    #not exactly sure how this model should select tetrimino placements, or if it is better suited to just getting the tetrimino there
    #_world.set_start_state

    showTextScreen('Tetromino')
    while True: # game loop
        #if random.randint(0, 1) == 0:
        #    pygame.mixer.music.load('tetrisb.mid')
        #else:
        #    pygame.mixer.music.load('tetrisc.mid')
        #pygame.mixer.music.play(-1, 0.0)

        runGame()
        #pygame.mixer.music.stop()

        showTextScreen('Game Over')



def runGame():

    # initialize the random seed
    # this allows us to replay the game with the same tetrimino order
    seed = random.random()
    random.seed(seed)

    board_history = []
    fallingPiece_history = []

    # setup variables for the start of the game
    board = getBlankBoard()
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False # note: there is no movingUp variable
    movingLeft = False
    movingRight = False
    score = 0
    level, fallFreq = calculateLevelAndFallFreq(score)

    fallingPiece = getNewPiece()
    nextPiece = getNewPiece()
    phantomPiece = getPhantomPiece(board, fallingPiece)
    holdPiece = None
    storedThisRound = False
    best_place = None
    view_enclosed_area = False
    view_over_hangs = False
    view_phantom_piece = True
    view_recommendation = False

    #played_move = []
    #metrics_list = []
    #need_to_update = False

    board_history.append(copy.deepcopy(board))
    fallingPiece_history.append(copy.deepcopy(fallingPiece))

    best_place = update_reccomendation(fallingPiece, board, holdPiece, nextPiece)
    #print(placements)

    while True: # game loop
        if fallingPiece == None:
            # No falling piece in play, so start a new piece at the top
            fallingPiece = nextPiece

            board_history.append(copy.deepcopy(board))
            fallingPiece_history.append(copy.deepcopy(fallingPiece))

            phantomPiece = getPhantomPiece(board, fallingPiece)
            storedThisRound = False

            nextPiece = getNewPiece()
            lastFallTime = time.time() # reset lastFallTime

            best_place = update_reccomendation(fallingPiece, board, holdPiece, nextPiece)
            #need_to_update = True
            #for placement in placements:
                #metrics_list.append(metrics.get_metrics(board, placement, raw=True))
            #played_move = np.full(len(metrics_list), 0)

            if not isValidPosition(board, fallingPiece):
                return # can't fit a new piece on the board, so game over

        checkForQuit()

        for event in pygame.event.get(): # event handling loop
            if event.type == KEYUP:
                if (event.key == K_p):
                    # Pausing the game
                    DISPLAYSURF.fill(BGCOLOR)
                    #pygame.mixer.music.stop()
                    showTextScreen('Paused') # pause until a key press
                    #pygame.mixer.music.play(-1, 0.0)
                    lastFallTime = time.time()
                    lastMoveDownTime = time.time()
                    lastMoveSidewaysTime = time.time()
                elif (event.key == K_i):
                    #print(board_history)
                    #print(fallingPiece_history)
                    DISPLAYSURF.fill(BGCOLOR)
                    board, fallingPiece, board_history, fallingPiece_history = showInfoScreen(copy.deepcopy(board_history), copy.deepcopy(fallingPiece_history), copy.deepcopy(board), copy.deepcopy(fallingPiece), board_history.index(board))
                    best_place = update_reccomendation(fallingPiece, board, holdPiece, nextPiece)
                    phantomPiece = getPhantomPiece(board, fallingPiece)
                    lastFalltime = time.time()
                    lastMoveDownTime = time.time()
                    lastMoveSidewaysTime = time.time()
                elif (event.key == K_e):
                    view_enclosed_area = not view_enclosed_area
                elif (event.key == K_u):
                    view_over_hangs = not view_over_hangs
                elif (event.key == K_f):
                    view_phantom_piece = not view_phantom_piece
                elif (event.key == K_r):
                    view_recommendation = not view_recommendation
                elif (event.key == K_LEFT or event.key == K_a):
                    movingLeft = False
                elif (event.key == K_RIGHT or event.key == K_d):
                    movingRight = False
                elif (event.key == K_DOWN or event.key == K_s):
                    movingDown = False

            elif event.type == KEYDOWN:
                # storing the piece
                if (event.key == K_c) and not storedThisRound:
                    tempPiece = holdPiece
                    holdPiece = fallingPiece
                    holdPiece['y'] = -1
                    holdPiece['x'] = int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2)
                    if tempPiece: fallingPiece = tempPiece
                    else:
                        fallingPiece = nextPiece
                        nextPiece = getNewPiece()
                    phantomPiece = getPhantomPiece(board, fallingPiece)

                    board_history.append(copy.deepcopy(board))
                    fallingPiece_history.append(copy.deepcopy(fallingPiece))

                    best_place = update_reccomendation(fallingPiece, board, holdPiece, nextPiece)
                    storedThisRound = True

                # moving the piece sideways
                elif (event.key == K_LEFT or event.key == K_a) and isValidPosition(board, fallingPiece, adjX=-1):
                    fallingPiece['x'] -= 1
                    phantomPiece['x'] -= 1
                    movingLeft = True
                    movingRight = False
                    for i in range(1, BOARDHEIGHT):
                        if not isValidPosition(board, fallingPiece, adjY=i):
                            break
                    phantomPiece['y'] = fallingPiece['y'] + i - 1
                    lastMoveSidewaysTime = time.time()
                elif (event.key == K_RIGHT or event.key == K_d) and isValidPosition(board, fallingPiece, adjX=1):
                    fallingPiece['x'] += 1
                    phantomPiece['x'] += 1
                    movingRight = True
                    movingLeft = False
                    for i in range(1, BOARDHEIGHT):
                        if not isValidPosition(board, fallingPiece, adjY=i):
                            break
                    phantomPiece['y'] = fallingPiece['y'] + i - 1
                    lastMoveSidewaysTime = time.time()

                # rotating the piece (if there is room to rotate)
                elif (event.key == K_UP or event.key == K_w):
                    fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
                    if not isValidPosition(board, fallingPiece):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                    phantomPiece['rotation'] = fallingPiece['rotation']
                    for i in range(1, BOARDHEIGHT):
                        if not isValidPosition(board, fallingPiece, adjY=i):
                            break
                    phantomPiece['y'] = fallingPiece['y'] + i - 1
                elif (event.key == K_q): # rotate the other direction
                    fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
                    if not isValidPosition(board, fallingPiece):
                        fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
                    phantomPiece['rotation'] = fallingPiece['rotation']
                    for i in range(1, BOARDHEIGHT):
                        if not isValidPosition(board, fallingPiece, adjY=i):
                            break
                    phantomPiece['y'] = fallingPiece['y'] + i - 1
                # making the piece fall faster with the down key
                elif (event.key == K_DOWN or event.key == K_s):
                    movingDown = True
                    if isValidPosition(board, fallingPiece, adjY=1):
                        fallingPiece['y'] += 1
                    lastMoveDownTime = time.time()

                # move the current piece all the way down
                elif event.key == K_SPACE:
                    movingDown = False
                    movingLeft = False
                    movingRight = False
                    for i in range(1, BOARDHEIGHT):
                        if not isValidPosition(board, fallingPiece, adjY=i):
                            break
                    fallingPiece['y'] += i - 1

        # handle moving the piece because of user input
        if (movingLeft or movingRight) and time.time() - lastMoveSidewaysTime > MOVESIDEWAYSFREQ:
            if movingLeft and isValidPosition(board, fallingPiece, adjX=-1):
                fallingPiece['x'] -= 1
                phantomPiece['x'] -= 1
            elif movingRight and isValidPosition(board, fallingPiece, adjX=1):
                fallingPiece['x'] += 1
                phantomPiece['x'] += 1
            for i in range(1, BOARDHEIGHT):
                if not isValidPosition(board, fallingPiece, adjY=i):
                    break
            phantomPiece['y'] = fallingPiece['y'] + i - 1
            lastMoveSidewaysTime = time.time()

        if movingDown and time.time() - lastMoveDownTime > MOVEDOWNFREQ and isValidPosition(board, fallingPiece, adjY=1):
            fallingPiece['y'] += 1
            lastMoveDownTime = time.time()

        # let the piece fall if it is time to fall
        if time.time() - lastFallTime > fallFreq:
            # see if the piece has landed
            if not isValidPosition(board, fallingPiece, adjY=1):
                # falling piece has landed, set it on the board
                addToBoard(board, fallingPiece)
                #if need_to_update:
                #    played_move[placements.index(fallingPiece)] = 1
                #    features.extend(metrics_list)
                #    labels.extend(played_move)
                #    need_to_update = False
                score += removeCompleteLines(board)
                level, fallFreq = calculateLevelAndFallFreq(score)
                fallingPiece = None
            else:
                # piece did not land, just move the piece down
                fallingPiece['y'] += 1
                lastFallTime = time.time()

        # drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(board)
        drawStatus(score, level)
        drawNextPiece(nextPiece)
        drawHoldPiece(holdPiece)
        if view_enclosed_area: display_enclosed_area(board)
        if view_over_hangs: display_over_hangs(board)
        if fallingPiece != None:
            drawPiece(fallingPiece)
            if view_phantom_piece: drawPiece(phantomPiece, phantomPiece=True)
            if view_recommendation:
                if best_place: drawPiece(best_place, best_place=True)
                else: drawHoldRecc()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def update_reccomendation(fallingPiece, board, holdPiece, nextPiece):
    placements = get_placements(fallingPiece, board)
    if metrics.should_hold(board, placements, holdPiece, nextPiece): return None
    scores = metrics.score_placements(placements, board)

    max_score = max(scores)
    max_index = scores.index(max_score)
    best_place = placements[max_index]

    # THIS IS PRINTING
    print(metrics.callout_deviant(placements, board))

    return best_place

def display_enclosed_area(board):
    for box in metrics.getEnclosedSpaces(board):
        drawBox(box[0], box[1], DEEPSPACE, custom=True)

def display_over_hangs(board):
    for box in metrics.getNumOverhangs(board, blocks=True):
        pixelx, pixely = convertToPixelCoords(box[0], box[1])
        pygame.draw.rect(DISPLAYSURF, PUMPKIN, (pixelx + 1, pixely + 16, BOXSIZE - 1, BOXSIZE - 16))

def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()

def terminate():
    pygame.quit()
    sys.exit()

# KRT 17/06/2012 rewrite event detection to deal with mouse use
def checkForKeyPress():
    for event in pygame.event.get():
        if event.type == QUIT:      #event is quit
            terminate()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:   #event is escape key
                terminate()
            else:
                return event.key   #key found return with it
    # no quit or key events in queue so return None
    return None

def showInfoScreen(board_history, tetrimino_order, curr_board, fallingPiece, index):
    # Create buttons on the bottom of the tetris board
    '''
    Buttons:
        game_start : the initial state of the game
        previous_piece : the prev piece dropped         (does nothing at start of game)
        next_piece     : the next piece dropped                     ""
        game_end       : the last board state           (will not always be a finished game)
    '''
    # The mentor should still be present at every move
    # ADD a button "verbose" or something that provides an explanation of the mentors move
    # reommendation.
    _index = index
    max_index = index
    board = curr_board
    fallingPiece = fallingPiece
    board_history = board_history
    fallingPiece_history = tetrimino_order

    placements = None
    placement_index = 0
    curr_placement = None
    placement_mode = False
    scores = None
    curved_scores = None

    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_a and _index - 1 >= 0:

                    placement_mode = False
                    placements = None
                    placement_index = 0
                    curr_placement = None

                    _index -= 1
                    board = board_history[_index]
                    fallingPiece = fallingPiece_history[_index]

                    DISPLAYSURF.fill(BGCOLOR)
                    drawBoard(board)
                    drawPiece(fallingPiece)
                    pygame.display.update()
                    FPSCLOCK.tick(FPS)

                elif event.key == K_d and _index + 1 <= max_index:

                    placement_mode = False
                    placements = None
                    placement_index = 0
                    curr_placement = None

                    _index += 1
                    board = board_history[_index]
                    fallingPiece = fallingPiece_history[_index]

                    DISPLAYSURF.fill(BGCOLOR)
                    drawBoard(board)
                    drawPiece(fallingPiece)
                    pygame.display.update()
                    FPSCLOCK.tick(FPS)

                elif event.key == K_x:
                    if not placements:

                        placement_mode = True
                        placements = get_placements(fallingPiece, board)
                        scores = metrics.score_placements(placements, board)

                        curved_scores = metrics.curve_scores(scores)
                        placement_index = 0
                        curr_placement = placements[placement_index]
                        curr_grade = metrics.get_grade(curved_scores[placement_index])

                        best_metrics,max_index, metric_name = metrics.callout_deviant(placements, board)
                        print(max_index)
                        explanation = metrics.explain_choice(best_metrics, max_index, metric_name)
                        print(explanation)

                        DISPLAYSURF.fill(BGCOLOR)
                        gradeSurf = BASICFONT.render('Grade: %s' % curr_grade, True, TEXTCOLOR)
                        gradeRect = gradeSurf.get_rect()
                        gradeRect.topleft = (WINDOWWIDTH - 150, 20)
                        DISPLAYSURF.blit(gradeSurf, gradeRect)
                        pygame.display.update()

                        drawPiece(curr_placement, best_place = True)
                        #print(metrics.get_main_difference(curr_placement, placements, board, scores))
                        drawBoard(board)
                        drawPiece(fallingPiece)
                        pygame.display.update()
                        FPSCLOCK.tick()

                elif event.key == K_LEFT:
                    if placements and (placement_index - 1 >= 0) and placement_mode:

                        placement_index -= 1
                        curr_placement = placements[placement_index]
                        curr_grade = metrics.get_grade(curved_scores[placement_index])

                        DISPLAYSURF.fill(BGCOLOR)
                        gradeSurf = BASICFONT.render('Grade: %s' % curr_grade, True, TEXTCOLOR)
                        gradeRect = gradeSurf.get_rect()
                        gradeRect.topleft = (WINDOWWIDTH - 150, 20)
                        DISPLAYSURF.blit(gradeSurf, gradeRect)
                        pygame.display.update()

                        drawPiece(curr_placement, best_place = True)
                        #print(metrics.get_main_difference(curr_placement, placements, board, scores))
                        drawBoard(board)
                        drawPiece(fallingPiece)
                        pygame.display.update()
                        FPSCLOCK.tick()

                elif event.key == K_RIGHT:
                    if placements and (placement_index + 1 < len(placements)) and placement_mode:

                        placement_index += 1
                        curr_placement = placements[placement_index]
                        curr_grade = metrics.get_grade(curved_scores[placement_index])
                        #print(curr_grade)

                        DISPLAYSURF.fill(BGCOLOR)
                        gradeSurf = BASICFONT.render('Grade: %s' % curr_grade, True, TEXTCOLOR)
                        gradeRect = gradeSurf.get_rect()
                        gradeRect.topleft = (WINDOWWIDTH - 150, 20)
                        DISPLAYSURF.blit(gradeSurf, gradeRect)
                        pygame.display.update()

                        drawPiece(curr_placement, best_place = True)
                        #print(metrics.get_main_difference(curr_placement, placements, board, scores))
                        drawBoard(board)
                        drawPiece(fallingPiece)
                        pygame.display.update()
                        FPSCLOCK.tick()

            elif event.type == KEYUP:
                if event.key == K_i:
                    return (copy.deepcopy(board), copy.deepcopy(fallingPiece), copy.deepcopy(board_history[0:_index+1]), copy.deepcopy(fallingPiece_history[0:_index+1]))

            #print("Updating")
            drawBoard(board)
            drawPiece(fallingPiece)
            if curr_placement and placement_mode: drawPiece(curr_placement, best_place = True)
            pygame.display.update()
            FPSCLOCK.tick(FPS)

def showTextScreen(text):
    # This function displays large text in the
    # center of the screen until a key is pressed.
    # Draw the text drop shadow
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the text
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the additional "Press a key to play." text.
    pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    while checkForKeyPress() == None:
        pygame.display.update()
        FPSCLOCK.tick()

def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back

def get_placements(fallingPiece, board):
    tempPiece = copy.deepcopy(fallingPiece)
    # Returns a list of valid x,y placements for the fallingPiece
    placements = []
    for a in range(len(PIECES[tempPiece['shape']])):
        for i in range(-2, 8):
            for j in range(0,18):
                tempPiece['x'] = i
                tempPiece['y'] = j
                if isValidPosition(board, tempPiece) and not isValidPosition(board, tempPiece, adjY=1):
                    placements.append(copy.deepcopy(tempPiece))
        tempPiece['rotation'] = (tempPiece['rotation'] - 1) % len(PIECES[tempPiece['shape']])

    placements = metrics.stripPlacements(board, placements)
    return placements

def calculateLevelAndFallFreq(score):
    # Based on the score, return the level the player is on and
    # how many seconds pass until a falling piece falls one space.
    level = int(score / 10) + 1
    fallFreq = 0.27 - (level * 0.02)
    return level, fallFreq

def getPiece(shape, rotation, x, y):

    newPiece = {'shape': shape,
                'rotation': rotation,
                'x': x,
                'y': y,
    }
    return newPiece

def getNewPiece():
    # return a random new piece in a random rotation and color
    shape = random.choice(list(PIECES.keys()))
    newPiece = {'shape': shape,
                'rotation': random.randint(0, len(PIECES[shape]) - 1),
                'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                'y': -1, # start it above the board (i.e. less than 0)
                'color': random.randint(0, len(COLORS)-1)}
    return newPiece

def getPhantomPiece(board, fallingPiece):
    shape = fallingPiece['shape']
    rotation = fallingPiece['rotation']
    x = fallingPiece['x']
    y = fallingPiece['y']
    color = fallingPiece['color']
    #print(color)
    phantomPiece = {'shape': shape,
                    'rotation': rotation,
                    'x': x,
                    'y': y,
                    'color': color }
    for i in range(1, BOARDHEIGHT):
        if not isValidPosition(board, phantomPiece, adjY=i):
            break
    phantomPiece['y'] += i - 1
    return phantomPiece

def addToBoard(board, piece):
    # fill in the board based on piece's location, shape, and rotation
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                board[x + piece['x']][y + piece['y']] = piece['color']

def getBlankBoard():
    # create and return a new blank board data structure
    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)
    return board

def isOnBoard(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT and y >= 0

def isValidPosition(board, piece, adjX=0, adjY=0):
    # Return True if the piece is within the board and not colliding
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                return False
    return True

def isCompleteLine(board, y):
    # Return True if the line filled with boxes with no gaps.
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False
    return True

def removeCompleteLines(board):
    # Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
    numLinesRemoved = 0
    y = BOARDHEIGHT - 1 # start y at the bottom of the board
    while y >= 0:
        if isCompleteLine(board, y):
            # Remove the line and pull boxes down by one line.
            for pullDownY in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pullDownY] = board[x][pullDownY-1]
            # Set very top line to blank.
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            numLinesRemoved += 1
            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1 # move on to check next row up
    return numLinesRemoved

def convertToPixelCoords(boxx, boxy):
    # Convert the given xy coordinates of the board to xy
    # coordinates of the location on the screen.
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))

def drawBox(boxx, boxy, color, pixelx=None, pixely=None, custom=False):
    # draw a single box (each tetromino piece has four boxes)
    # at xy coordinates on the board. Or, if pixelx & pixely
    # are specified, draw to the pixel coordinates stored in
    # pixelx & pixely (this is used for the "Next" piece).
    if custom:
        if pixelx == None and pixely == None:
            pixelx, pixely = convertToPixelCoords(boxx, boxy)
        pygame.draw.rect(DISPLAYSURF, color, (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
        pygame.draw.rect(DISPLAYSURF, color, (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))
        return
    if color == BLANK:
        return
    if pixelx == None and pixely == None:
        pixelx, pixely = convertToPixelCoords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))

# DRAW THE OUTLINE OF THE PHANTOM PIECE
# USE THE ABOVE drawBox() FUNCTION AS REFERENCE
# THIS FUNCTION IS CALLED IN drawPiece()
def drawPhantomPiece(color, pixelx=None, pixely=None, best_place=False):
    if color == BLANK:
        return
    # Add some transparency
    phantom_color = COLORS[color] + (0.5,)
    if best_place:
        phantom_color = DEEPSPACE
    pygame.draw.rect(DISPLAYSURF, phantom_color, (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, (0,0,0), (pixelx + 2, pixely + 2, BOXSIZE - 3, BOXSIZE - 3))

def drawBoard(board):
    # draw the border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)

    # fill the background of the board
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    # draw the individual boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            drawBox(x, y, board[x][y])

def drawStatus(score, level):
    # draw the score text
    scoreSurf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 150, 20)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    # draw the level text
    levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 50)
    DISPLAYSURF.blit(levelSurf, levelRect)

def drawPiece(piece, pixelx=None, pixely=None, phantomPiece=False, best_place=False):
    shapeToDraw = PIECES[piece['shape']][piece['rotation']]
    if pixelx == None and pixely == None:
        # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
        pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])

    # draw each of the boxes that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shapeToDraw[y][x] != BLANK:
                if best_place: drawPhantomPiece(piece['color'], pixelx + (x* BOXSIZE), pixely + (y*BOXSIZE), best_place=True)
                elif phantomPiece: drawPhantomPiece(piece['color'], pixelx + (x* BOXSIZE), pixely + (y*BOXSIZE))
                else: drawBox(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))

# COULD COMBINE drawNextPiece AND drawHoldPiece INTO ONE FUNC BUT LAZY
def drawNextPiece(piece):
    # draw the "next" text
    nextSurf = BASICFONT.render('Next:', True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 120, 80)
    DISPLAYSURF.blit(nextSurf, nextRect)
    # draw the "next" piece
    drawPiece(piece, pixelx=WINDOWWIDTH-120, pixely=100)

def drawHoldPiece(piece):
    # draw the "hold" text
    holdSurf = BASICFONT.render('Hold:', True, TEXTCOLOR)
    holdRect = holdSurf.get_rect()
    holdRect.topleft = (120, 80)
    DISPLAYSURF.blit(holdSurf, holdRect)
    if piece != None:
        drawPiece(piece, pixelx=100, pixely=100)

def drawHoldRecc():
    holdSurf = BASICFONT.render('Hold this piece!', True, TEXTCOLOR)
    holdRect = holdSurf.get_rect()
    holdRect.topleft = (70, 220)
    DISPLAYSURF.blit(holdSurf, holdRect)

if __name__ == '__main__':
    main()
