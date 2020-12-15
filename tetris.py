#GOAPy
#Generic GOAP implementation.
#flags - https://github.com/flags

#The MIT License (MIT)
#
#Copyright (c) 2014 Luke Martin (flags)
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


class World:
    def __init__(self):
        self.planners = []
        self.plans = []

    def add_planner(self, planner):
        self.planners.append(planner)

    def calculate(self):
        self.plans = []

        for planner in self.planners:
            self.plans.append(planner.calculate())

    def get_plan(self, debug=False):
        _plans = {}

        for plan in self.plans:
            _plan_cost = sum([action['g'] for action in plan])

            if _plan_cost in _plans:
                _plans[_plan_cost].append(plan)
            else:
                _plans[_plan_cost] = [plan]

        _sorted_plans = sorted(_plans.keys())

        if debug:
            _i = 1

            for plan_score in _sorted_plans:
                for plan in _plans[plan_score]:
                    print(_i)

                    for action in plan:
                        print("  %s" % action['name'])

                    _i += 1

                    print('\nTotal cost: %s\n' % plan_score)

        return [_plans[p][0] for p in _sorted_plans]

class Planner:
    def __init__(self, *keys):
        self.start_state = None
        self.goal_state = None
        self.values = {k: -1 for k in keys}
        self.action_list = None

    def state(self, **kwargs):
        _new_state = self.values.copy()
        _new_state.update(kwargs)

        return _new_state

    def set_start_state(self, **kwargs):
        _invalid_states = set(kwargs.keys()) - set(self.values.keys())

        if _invalid_states:
            raise Exception('Invalid states for world start state: %s' % ', '.join(list(_invalid_states)))

        self.start_state = self.state(**kwargs)

    def set_goal_state(self, **kwargs):
        _invalid_states = set(kwargs.keys()) - set(self.values.keys())

        if _invalid_states:
            raise Exception('Invalid states for world goal state: %s' % ', '.join(list(_invalid_states)))

        self.goal_state = self.state(**kwargs)

    def set_action_list(self, action_list):
        self.action_list = action_list

    def calculate(self):
        return astar(self.start_state,
                     self.goal_state,
                     {c: self.action_list.conditions[c].copy() for c in self.action_list.conditions},
                     {r: self.action_list.reactions[r].copy() for r in self.action_list.reactions},
                     self.action_list.weights.copy())

class Action_List:
    def __init__(self):
        self.conditions = {}
        self.reactions = {}
        self.weights = {}

    def add_condition(self, key, **kwargs):
        if not key in self.weights:
            self.weights[key] = 1

        if not key in self.conditions:
            self.conditions[key] = kwargs

            return

        self.conditions[key].update(kwargs)

    def add_reaction(self, key, **kwargs):
        if not key in self.conditions:
            raise Exception('Trying to add reaction \'%s\' without matching condition.' % key)

        if not key in self.reactions:
            self.reactions[key] = kwargs

            return

        self.reactions[key].update(kwargs)

    def set_weight(self, key, value):
        if not key in self.conditions:
            raise Exception('Trying to set weight \'%s\' without matching condition.' % key)

        self.weights[key] = value


def distance_to_state(state_1, state_2):
    _scored_keys = set()
    _score = 0

    for key in state_2.keys():
        _value = state_2[key]

        if _value == -1:
            continue

        if not _value == state_1[key]:
            _score += 1

        _scored_keys.add(key)

    for key in state_1.keys():
        if key in _scored_keys:
            continue

        _value = state_1[key]

        if _value == -1:
            continue

        if not _value == state_2[key]:
            _score += 1

    return _score

def conditions_are_met(state_1, state_2):
        # print state_1, state_2
    for key in state_2.keys():
        _value = state_2[key]

        if _value == -1:
            continue

        if not state_1[key] == state_2[key]:
            return False

    return True

def node_in_list(node, node_list):
    for next_node in node_list.values():
        if node['state'] == next_node['state'] and node['name'] == next_node['name']:
            return True

    return False

def create_node(path, state, name=''):
    path['node_id'] += 1
    path['nodes'][path['node_id']] = {'state': state, 'f': 0, 'g': 0, 'h': 0, 'p_id': None, 'id': path['node_id'], 'name': name}

    return path['nodes'][path['node_id']]

def astar(start_state, goal_state, actions, reactions, weight_table):
    _path = {'nodes': {},
             'node_id': 0,
             'goal': goal_state,
             'actions': actions,
             'reactions': reactions,
             'weight_table': weight_table,
             'action_nodes': {},
             'olist': {},
             'clist': {}}

    _start_node = create_node(_path, start_state, name='start')
    _start_node['g'] = 0
    _start_node['h'] = distance_to_state(start_state, goal_state)
    _start_node['f'] = _start_node['g'] + _start_node['h']
    _path['olist'][_start_node['id']] = _start_node

    for action in actions:
        _path['action_nodes'][action] = create_node(_path, actions[action], name=action)

    return walk_path(_path)

def walk_path(path):
    node = None

    _clist = path['clist']
    _olist = path['olist']

    while len(_olist):
        ####################
        ##Find lowest node##
        ####################

        _lowest = {'node': None, 'f': 9000000}

        for next_node in _olist.values():
            if not _lowest['node'] or next_node['f'] < _lowest['f']:
                _lowest['node'] = next_node['id']
                _lowest['f'] = next_node['f']

        if _lowest['node']:
            node = path['nodes'][_lowest['node']]

        else:
            return

        ################################
        ##Remove node with lowest rank##
        ################################

        del _olist[node['id']]

        #######################################
        ##If it matches the goal, we are done##
        #######################################

        if conditions_are_met(node['state'], path['goal']):
            _path = []

            while node['p_id']:
                _path.append(node)

                node = path['nodes'][node['p_id']]

            _path.reverse()

            return _path

        ####################
        ##Add it to closed##
        ####################

        _clist[node['id']] = node

        ##################
        ##Find neighbors##
        ##################

        _neighbors = []

        for action_name in path['action_nodes']:
            if not conditions_are_met(node['state'], path['action_nodes'][action_name]['state']):
                continue

            path['node_id'] += 1

            _c_node = node.copy()
            _c_node['state'] = node['state'].copy()
            _c_node['id'] = path['node_id']
            _c_node['name'] = action_name

            for key in path['reactions'][action_name]:
                _value = path['reactions'][action_name][key]

                if _value == -1:
                    continue

                _c_node['state'][key] = _value

            path['nodes'][_c_node['id']] = _c_node
            _neighbors.append(_c_node)

        for next_node in _neighbors:
            _g_cost = node['g'] + path['weight_table'][next_node['name']]
            _in_olist, _in_clist = node_in_list(next_node, _olist), node_in_list(next_node, _clist)

            if _in_olist and _g_cost < next_node['g']:
                del _olist[next_node]

            if _in_clist and _g_cost < next_node['g']:
                del _clist[next_node['id']]

            if not _in_olist and not _in_clist:
                next_node['g'] = _g_cost
                next_node['h'] = distance_to_state(next_node['state'], path['goal'])
                next_node['f'] = next_node['g'] + next_node['h']
                next_node['p_id'] = node['id']

                _olist[next_node['id']] = next_node

    return []


# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

# KRT 17/06/2012 rewrite event detection to deal with mouse use

import random, time, pygame, sys
from pygame.locals import *
import copy

FPS = 25
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '.'
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
    global board_history
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetromino')
    num_pieces = 1000
    board_history = []
    game_history = {

    }

    _world = Planner('right_of_goal', 'left_of_goal', 'above_goal', 'cw_of_goal', 'ccw_of_goal')
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
        tetriminos = getTetriminos(num_pieces)
        #print(tetriminos)
        tetriminos = iter(tetriminos)
        #print(len(board_history))
        runGame(tetriminos)
        #pygame.mixer.music.stop()
        '''
        iter_boardHist = iter(board_history)
        for board_ in board_history:
            tim = time.time()
            while(time.time() < tim + 1):
                #print("fuck")
                drawBoard(board_)
                pygame.display.update()
                FPSCLOCK.tick(FPS)
                print("fuck")
        '''
        board_history = []
        showTextScreen('Game Over')



def runGame(tetriminos):

    # initialize the random seed
    # this allows us to replay the game with the same tetrimino order
    seed = random.random()
    random.seed(seed)


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

    fallingPiece = next(tetriminos)
    nextPiece = next(tetriminos)
    phantomPiece = getPhantomPiece(board, fallingPiece)
    holdPiece = None
    storedThisRound = False
    board_history.append(board)
    placements = get_placements(fallingPiece, board)
    #print(placements)

    while True: # game loop
        if fallingPiece == None:
            # No falling piece in play, so start a new piece at the top
            fallingPiece = nextPiece
            phantomPiece = getPhantomPiece(board, fallingPiece)
            storedThisRound = False

            nextPiece = next(tetriminos)
            lastFallTime = time.time() # reset lastFallTime

            placements = get_placements(fallingPiece, board)

            print("PLACEMENTS")
            print(placements)
            for placement in placements:
                drawPiece(placement, phantomPiece = True)
            while checkForKeyPress() == None:
                pygame.display.update()
                FPSCLOCK.tick()

            if not isValidPosition(board, fallingPiece):
                return # can't fit a new piece on the board, so game over

        checkForQuit()
        if checkOverhangAll(board):
            print("overhang!")
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
                    showInfoScreen(None, None)
                    lastFalltime = time.time()
                    lastMoveDownTime = time.time()
                    lastMoveSidewaysTime = time.time()
                elif (event.key == K_LEFT or event.key == K_a):
                    movingLeft = False
                elif (event.key == K_RIGHT or event.key == K_d):
                    movingRight = False
                elif (event.key == K_DOWN or event.key == K_s):
                    movingDown = False

            elif event.type == KEYDOWN:
                if (event.key == K_c) and not storedThisRound:

                    if holdPiece: tempPiece = holdPiece
                    else:
                        tempPiece = nextPiece
                        nextPiece = next(tetriminos)

                    holdPiece = fallingPiece
                    holdPiece['y'] = -1
                    holdPiece['x'] = int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2)

                    fallingPiece = tempPiece
                    if fallingPiece: phantomPiece = getPhantomPiece(board, fallingPiece)
                    storedThisRound = True
                    #break
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
                board_history.append(board)
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
        if fallingPiece != None:
            drawPiece(fallingPiece)
            drawPiece(phantomPiece, phantomPiece=True)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


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



##def checkForKeyPress():
##    # Go through event queue looking for a KEYUP event.
##    # Grab KEYDOWN events to remove them from the event queue.
##    checkForQuit()
##
##    for event in pygame.event.get([KEYDOWN, KEYUP]):
##        if event.type == KEYDOWN:
##            continue
##        return event.key
##    return None

def showInfoScreen(board_history, tetrimino_order):
    # Create buttons on the bottom of the tetris board
    '''
    Buttons:
        game_start : the initial state of the game
        previous_piece : the prev piece dropped         (does nothing at start of game)
        previous_move  : the previous keyboardinput                 ""
        next_move      : the next keyboardinput         (does nothing at end of game)
        next_piece     : the next piece dropped                     ""
        game_end       : the last board state           (will not always be a finished game)
    '''
    # The mentor should still be present at every move
    # ADD a button "verbose" or something that provides an explanation of the mentors move
    # reommendation.
    pass

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
    tempX = fallingPiece['x']
    tempY = fallingPiece['y']
    tempR = fallingPiece['rotation']
    # Returns a list of valid x,y placements for the fallingPiece
    placements = []
    for a in range(len(PIECES[fallingPiece['shape']])):
        for i in range(-2, 8):
            for j in range(0,17):
                fallingPiece['x'] = i
                fallingPiece['y'] = j
                if isValidPosition(board, fallingPiece) and not isValidPosition(board, fallingPiece, adjY=1):
                    placements.append(copy.deepcopy(fallingPiece))
        fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']])
    fallingPiece['x'] = tempX
    fallingPiece['y'] = tempY
    fallingPiece['rotation'] = tempR
    return placements

def calculateLevelAndFallFreq(score):
    # Based on the score, return the level the player is on and
    # how many seconds pass until a falling piece falls one space.
    level = int(score / 10) + 1
    fallFreq = 0.27 - (level * 0.02)
    return level, fallFreq

def getTetriminos(num_pieces):
    tetriminos = []
    for i in range(num_pieces):
        tetriminos.append(getNewPiece())
    return tetriminos

def getPiece(shape, rotation, x, y, color):

    newPiece = {'shape': shape,
                'rotation': rotation,
                'x': x,
                'y': y,
                'color': color
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
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


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

def checkOverhang(board, x):
    # Return True if the column has a gap with tetriminos above and below it.
    blank = False
    block = False
    for y in range(BOARDHEIGHT):        
        if board[x][y] == BLANK:
            blank = True
            block = False
        else:
            block = True
        if blank and block:
            return True
    return False

def checkOverhangAll(board):
    for x in range(BOARDWIDTH):
        if checkOverhang(board,x):
            return True
    return False


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


def drawBox(boxx, boxy, color, pixelx=None, pixely=None):
    # draw a single box (each tetromino piece has four boxes)
    # at xy coordinates on the board. Or, if pixelx & pixely
    # are specified, draw to the pixel coordinates stored in
    # pixelx & pixely (this is used for the "Next" piece).
    if color == BLANK:
        return
    if pixelx == None and pixely == None:
        pixelx, pixely = convertToPixelCoords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))

# DRAW THE OUTLINE OF THE PHANTOM PIECE
# USE THE ABOVE drawBox() FUNCTION AS REFERENCE
# THIS FUNCTION IS CALLED IN drawPiece()
def drawPhantomPiece(color, pixelx=None, pixely=None):
    if color == BLANK:
        return
    # Add some transparency
    phantom_color = COLORS[color] + (0.5,)
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


def drawPiece(piece, pixelx=None, pixely=None, phantomPiece=False):
    shapeToDraw = PIECES[piece['shape']][piece['rotation']]
    if pixelx == None and pixely == None:
        # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
        pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])

    # draw each of the boxes that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shapeToDraw[y][x] != BLANK:
                if phantomPiece: drawPhantomPiece(piece['color'], pixelx + (x* BOXSIZE), pixely + (y*BOXSIZE))
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
        drawPiece(piece, pixelx=120, pixely=100)



if __name__ == '__main__':
    main()
