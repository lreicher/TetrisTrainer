import tetris
import heapq
import copy
from math import sqrt

def get_grade(score):
    if score <= 60: return "F"
    elif score <= 70: return "D"
    elif score <= 80: return "C"
    elif score <= 90: return "B"
    elif score < 95: return "A"
    else: return "A+"

def score_placements(placements, board):
    score = []
    for placement in placements:
        score.append(heuristic_eval(placement, board))
    return score

def curve_scores(scores):
    curved_scores = []
    low_score = 100
    high_score = 1
    for score in scores:
        if score > high_score:
            high_score = score
        if score < low_score:
            low_score = score
    if high_score - low_score == 0:
        for score in scores:
            curved_scores.append(100)
    else:
        for score in scores:
            curved_score = 100 * ((score - low_score)/(high_score - low_score))
            curved_scores.append(curved_score)
    return curved_scores

def callout_deviant(placements, board):
    placements_stds = get_metrics_std(board,placements)
    placements_means,placements_metrics = get_metrics_mean(board,placements)
    placements_devs = [0,0,0,0,0]
    scores = score_placements(placements, board)

    max_score = max(scores)
    max_index = scores.index(max_score)
    best_place = placements[max_index]
    best_metrics = get_metrics(board,best_place,raw=True)
    for i in range(len(placements_devs)):
        if placements_stds[i] == 0:
            placements_devs[i] = 0
        else: placements_devs[i] = (best_metrics[i] - placements_means[i]) / placements_stds[i]
    max_dev = max(placements_devs)
    max_index = placements_devs.index(max_dev)
    return best_metrics,max_index, placements_devs[i]

def explain_choice(choice_metrics,metric_index,metric_name):
    if metric_index == 0:
        nlc_message = "This move would clear " +str(choice_metrics[metric_index]) + " lines."
        return nlc_message
    elif metric_index == 1:
        cnes_message = "This move would make a difference of " +str(choice_metrics[metric_index]) + " enclosed spaces."
        return cnes_message
    elif metric_index == 2:
        ha_message = "This move would make a difference of " +str(choice_metrics[metric_index]) + " lines of height."
        return ha_message
    elif metric_index == 3:
        cno_message = "This move would make a difference of " +str(choice_metrics[metric_index]) + " number of overhangs."
        return cno_message
    elif metric_index == 4:
        ug_message = "This move would make a difference of " + str(choice_metrics[metric_index]) + " number of unique gap widths."
        return ug_message
    else:
        er_message = "Something went wrong in metrics.explain_choice."
        return er_message

def heuristic_eval(placement, board, vals=False):
    placement_metrics = get_metrics(board, placement)
    line_difference = placement_metrics["height_added"] - placement_metrics["num_lines_cleared"]
    ld_weight = 5
    #ie_weight = 8
    #is_weight = 7
    cnes_weight = 15
    cno_weight = 3
    ug_weight = 1

    n_ld = 100 - 100 * ((line_difference - (-4) )/( 4 - (-4)))
    #next line looks sus
    n_cnes = 100 -100 * ((placement_metrics["change_num_enclosedSpaces"] - (-40))/(40 - (-40)))
    n_cno = 100 - 100 * ((placement_metrics["change_num_overhangs"] - (-2))/(2 - (-2)))
    n_ug = 100 * ((placement_metrics["unique_gaps"] - (-4))/(4 - (-4)))

    summed_weights = ld_weight + cnes_weight + cno_weight + ug_weight
    weighted_sum = ((ld_weight * n_ld)+(cnes_weight * n_cnes)+(cno_weight * n_cno)+(ug_weight * n_ug))/summed_weights
    if vals: return weighted_sum, (n_cnes, n_cno, n_ug, placement_metrics["height_added"], placement_metrics["num_lines_cleared"])
    else: return weighted_sum

def get_two_closest_placements(placement, placements, board, scores):
    placement_index = placements.index(placement)
    lesser_greater = 100
    greatest_lesser = 0
    above_index = None
    below_index = None
    above_placement = None
    below_placement = None
    for score in scores:
        if score != scores[placement_index]:
            if score > scores[placement_index] and score < lesser_greater:
                above_index = scores.index(score)
            elif score > greatest_lesser:
                below_index = scores.index(score)
    if above_index:
        above_placement = placements[above_index]
    if below_index:
        below_placement = placements[below_index]
    return (below_placement, above_placement)

def get_main_difference(placement, placements, board, scores):
    mean_metrics, mean = get_metrics_mean(board, placements)
    print("MEAN")
    print(mean_metrics)
    score, vals = heuristic_eval(placement, board, vals=True)
    print("BEST")
    print(vals)
    difference = [0,0,0,0,0]
    for i in range(len(difference)):
        difference[i] = vals[i] - mean_metrics[i]
    print("DIFFERENCE")
    print(difference)


def should_hold(board, placements, holdPiece=None, next_piece=None):
    if not holdPiece and not next_piece:
        return False

    max_score = max(score_placements(placements, board))
    if not holdPiece:
        next_score = max(score_placements(tetris.get_placements(next_piece, board),board))
        if next_score > max_score: return True
    else:
        hold_score = max(score_placements(tetris.get_placements(holdPiece, board),board))
        if hold_score > max_score: return True
    return False

def get_metrics_mean(board, placements):
    metrics = []
    for placement in placements:
        metrics.append(get_metrics(board,placement,raw=True))
    sum_metrics = [0,0,0,0,0]
    for metric in metrics:
        for i in range(len(metric)):
            sum_metrics[i] += metric[i]
    mean_metrics = [0,0,0,0,0]
    for i in range(len(sum_metrics)):
        mean_metrics[i] = sum_metrics[i] / len(sum_metrics)
    return mean_metrics, metrics

def get_metrics_std(board, placements):
    mean_metrics, metrics = get_metrics_mean(board, placements)
    res = [0,0,0,0,0]
    for metric in metrics:
        for i in range(len(res)):
            res[i] += (metric[i] - mean_metrics[i]) ** 2
    for i in range(len(res)):
        res[i] = sqrt(res[i] / len(placements))
    return res

def get_metrics(board, placement, raw=False):
    if raw:
        metrics = [0,0,0,0,0]
        metrics[0] = num_lines_cleared(placement, board)
        metrics[1] = change_num_enclosedSpaces(placement, board)
        metrics[2] = heightAdded(placement, board)
        metrics[3] = change_num_overhangs(placement, board)
        metrics[4] = get_change_roughness(placement, board)
    else:
        metrics = {}
        metrics["num_lines_cleared"] = num_lines_cleared(placement, board)
        metrics["change_num_enclosedSpaces"] = change_num_enclosedSpaces(placement, board)
        metrics["height_added"] = heightAdded(placement, board)
        metrics["change_num_overhangs"] = change_num_overhangs(placement, board)
        metrics["unique_gaps"] = get_change_roughness(placement, board)
    return metrics

def is_stuck(placement, board):
    startingRot = placement['rotation']
    tempPiece = copy.deepcopy(placement)
    if tetris.isValidPosition(board, tempPiece, adjX=1) or tetris.isValidPosition(board, tempPiece, adjX=-1) \
    or tetris.isValidPosition(board, tempPiece, adjY=-1): return 0
    for a in range(len(tetris.PIECES[tempPiece['shape']])):
        tempPiece['rotation'] = (tempPiece['rotation'] - 1) % len(tetris.PIECES[tempPiece['shape']])
        if tetris.isValidPosition(board, tempPiece) and tempPiece['rotation'] != startingRot: return 0
    return 1

def isTricky(placement, board):
    startingRot = placement['rotation']
    tempPiece = copy.deepcopy(placement)
    if (tetris.isValidPosition(board, tempPiece, adjX=1) or tetris.isValidPosition(board, tempPiece, adjX=-1)) \
    and not tetris.isValidPosition(board, tempPiece, adjY=-1): return "slide"
    for a in range(len(tetris.PIECES[tempPiece['shape']])):
        tempPiece['rotation'] = (tempPiece['rotation'] - 1) % len(tetris.PIECES[tempPiece['shape']])
        if tetris.isValidPosition(board, tempPiece) and tempPiece['rotation'] != startingRot: return "rotation"
    return None

def showWarnings(placement, board):
    trick = isTricky(placement, board)
    if trick:
        if trick == "slide":
            print("slide")
        if trick == "rotation":
            print("slide")


def is_in_enclosure(placement, board):
    enclosure_list = getEnclosedSpaces(board)
    return is_enclosed(enclosure_list, placement)

def pieceToBoard(piece):
    blocks = []
    shapeToDraw = tetris.PIECES[piece['shape']][piece['rotation']]
    for x in range(tetris.TEMPLATEWIDTH):
        for y in range(tetris.TEMPLATEHEIGHT):
            if shapeToDraw[y][x] != tetris.BLANK:
                blocks.append((piece['x'] + x, piece['y'] + y))
    return blocks

def num_lines_cleared(placement, board):
    tempBoard = copy.deepcopy(board)
    tetris.addToBoard(tempBoard, placement)
    comp_lines = 0
    for y in range(tetris.BOARDHEIGHT):
        if tetris.isCompleteLine(tempBoard, y):
            comp_lines += 1
    return comp_lines

# Returns a signed int representing the number of additional enclosed spaces
def change_num_enclosedSpaces(placement, board):
    tempBoard = copy.deepcopy(board)
    tetris.addToBoard(tempBoard, placement)
    return len(getEnclosedSpaces(tempBoard)) - len(getEnclosedSpaces(board))

def heightAdded(piece, board):
    blocks = pieceToBoard(piece)
    lowest_y = 19
    for x in range(0,10):
        for y in range(2,20):
            if board[x][y] != tetris.BLANK and y < lowest_y:
                lowest_y = y

    height_added = -1000
    for block in blocks:
        diff = lowest_y - block[1]
        if diff > height_added:
            height_added = diff
    return height_added

def change_num_overhangs(placement, board):
    tempBoard = copy.deepcopy(board)
    tetris.addToBoard(tempBoard, placement)
    return getNumOverhangs(tempBoard) - getNumOverhangs(board)

def getNumOverhangs(board, blocks=False):
    num_overhangs = 0
    top_blocks = []
    for x in range(0,10):
        for y in range(2,20):
            if board[x][y] != tetris.BLANK:
                if y + 1 <= 19:
                    if board[x][y+1] == tetris.BLANK:
                        if blocks: top_blocks.append((x,y))
                        num_overhangs += 1
    if blocks: return top_blocks
    return num_overhangs

def getEnclosedSpaces(board):
    enclosed_boxes = []
    searched_space = []
    for x in range(0,10):
        for y in range(2,20):
            if board[x][y] == tetris.BLANK and (x,y) not in searched_space:
                unexplored = []
                explored = []
                touched_roof = False
                unexplored.append((x,y))
                while(unexplored):
                    node = unexplored.pop()
                    for neighbor in get_neighbor_cells(board, node[0], node[1]):
                        a = neighbor[0]
                        b = neighbor[1]
                        if board[a][b] == tetris.BLANK and neighbor not in explored:
                            unexplored.append(neighbor)
                        if b <= 1: touched_roof = True
                    explored.append(node)
                    searched_space.append(node)
                if not touched_roof:
                    for node in explored:
                        enclosed_boxes.append(node)
    res = []
    for i in enclosed_boxes:
        if i not in res:
            res.append(i)
    return res

def get_neighbor_cells(board, x, y):
    neighbors = []
    for i in [-1,1]:
        if tetris.isOnBoard(x+i,y):
            neighbors.append((x+i,y))
    for j in [-1,1]:
        if tetris.isOnBoard(x,y+j):
            neighbors.append((x,y+j))
    return neighbors

def stripPlacements(board, placements):

    res = []
    enclosure_list = getEnclosedSpaces(board)
    for placement in placements:
        if not is_stuck(placement, board) and not is_enclosed(enclosure_list, placement):
            res.append(placement)
    return res

def strip_enclosed(board, placements):

    res = []
    for placement in placements:
        if not is_enclosed(enclosure_list, placement):
            res.append(placement)
    return res

def is_enclosed(enclosure_list, piece):
    blocks = pieceToBoard(piece)
    for block in blocks:
        if block in enclosure_list:
            return 1
    return 0

def get_shortestHeight(placements, board):
    minimum_height_index = None
    minimum_height = 500
    for i in range(len(placements)):
        height_added = heightAdded(placements[i], board)
        if height_added < minimum_height:
            minimum_height = height_added
            minimum_height_index = i
    return placements[minimum_height_index]

def get_change_roughness(placement, board):
    tempBoard = copy.deepcopy(board)
    tetris.addToBoard(tempBoard, placement)
    return get_roughness(tempBoard) - get_roughness(board)

def get_roughness(board):
    uniqueGapWidths = []
    currentHeight = 0
    prevHeight = 0
    currentGap = 1
    for x in range(tetris.BOARDWIDTH):
        for y in range(tetris.BOARDHEIGHT):
            if board[x][y] != tetris.BLANK:
                currentHeight = y
                if prevHeight == currentHeight:
                    currentGap += 1
                else:
                    if currentGap not in uniqueGapWidths:
                        uniqueGapWidths.append(currentGap)
                    currentGap = 1
                prevHeight = currentHeight
    return len(uniqueGapWidths)


def can_drop(piece, placement, board):
    tempPiece = copy.deepcopy(piece)

    if tempPiece['x'] != placement['x']: return False
    if tempPiece['rotation'] != placement['rotation']: return False
    for i in range(1, tetris.BOARDHEIGHT):
        if not isValidPosition(board, tempPiece, adjY=i):
            break
    tempPiece['y'] += i - 1
    if tempPiece['y'] != placement['y']: return False
    return True

"""
def strip_difficult_moves(board, placements, fallingPiece):
    # can move left or right
    # can rotate
    # then must move down
    # loop
    def get_neighbor_moves(piece, board, movedDown, movedHoriz, placement):
        # [can_drop, must_go_down, can_move_left, can_move_right, can_rotate_left, can_rotate_right]
        moves = []
        moves.append(can_drop(piece, placement, board))
        down = False
        if movedHorizon: down = True
        moves.append(down)
        if movedDown:
            for i in [-1,1]:
                moves.append(tetris.isValidPosition(board, piece, adjX=i))
        for i in [-1, 1]:
            piece['rotation'] = (piece['rotation'] + i) % len(tetris.PIECES[piece['shape']])
            if tetris.isValidPosition(board, piece): moves.append(True)
            else: moves.append(False)
            piece['rotation'] = (fallingPiece['rotation'] + (i * -1)) % len(tetris,PIECES[piece['shape']])
        return moves

    # can drop, same x coordinate, same rotation = goal state
    num_moves = 5
    for placement in placements:
        goal_x = placement['x']
        goal_y = placement['y']
        goal_rot = placement['rot']
        tempPiece = copy.deepcopy(fallingPiece)
        path = []
        falling_x = tempPiece['x']
        falling_y = tempPiece['y']
        while not path:
            movedDown = True
            movedHoriz = False
            rotated = False
            actions = {
                move_horiz: None
            }
            for i in range(num_moves + 1):
                    pass
"""



