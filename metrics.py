import tetris
import heapq
import copy

def get_grade(score):
    if score <= 60: return "F"
    elif score <= 70: return "D"
    elif score <= 80: return "C"
    elif score <= 90: return "B"
    elif score > 90: return "A"

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
    placements_metrics = []
    placement_metrics_sums = {}
    placement_metrics_avgs = {}
    placement_metrics_xms = {}
    placements_metrics_xms = {}
    placement_metrics_devs = {}
    placements_metrics_devs = {}
    population_size = len(placements)
    
    for placement in placements:
        placements_metrics.append(get_metrics(board, placement))    
    for placement_metrics in placements_metrics:
        for metric,value in placement_metrics.items():
            if metric not in placement_metrics_sums.keys():
                placement_metrics_sums[metric] = value
            else:
                placement_metrics_sums[metric] = placement_metrics_sums[metric] + value
        for metric,value in placement_metrics.items():
            placement_metrics_avgs[metric] = placement_metrics_sums[metric] / population_size
    for placement_metrics in placements_metrics:
        placement_metrics_xms.clear()
        for metric,value in placement_metrics.items():
            if metric not in placement_metrics_xms.keys():
                placement_metrics_xms[metric] = math.pow(value - placement_metrics_avgs[metric],2)
            else:
                placement_metrics_xms[metric] = placement_metrics_xms[metric] + (math.pow(value - placement_metrics_avgs[metric],2))
        placements_metrics_xms[placement_metrics] = placement_metrics_xms
    for placement_metrics in placements_metrics:
        placement_metrics_devs.clear()
        for metric,value in placement_metrics.items():
            placement_metrics_devs[metric] = math.sqrt((placements_metrics_xms[placement_metrics][metric])/population_size)
        placements_metrics_devs[placement_metrics] = placement_metrics_devs
    scores = score_placements(placements, board)
    high_score = 1
    for score in scores:
        if score > high_score:
            high_score = score
    most_deviant = 0
    for placement in placements:
        if high_score == heuristic_eval(placement_board):
            best_placement_metrics = get_metrics(board, placement)
            for metric,value in best_placement_metrics:
                if most_deviant < placements_metrics_devs[best_placement_metrics][metric]:
                    most_deviant = placements_metrics_devs[best_placement_metrics][metric]
            for metric,value in best_placement_metrics:
                if most_deviant == placements_metrics_devs[best_placement_metrics][metric]:
                    most_deviant_name = metric
            return (placement,most_deviant_name)
    
        

        
def heuristic_eval(placement, board):
    placement_metrics = get_metrics(board, placement)
    line_difference = placement_metrics["height_added"] - placement_metrics["num_lines_cleared"]
    ld_weight = 5
    #ie_weight = 8
    #is_weight = 7
    cnes_weight = 10
    cno_weight = 3
    ug_weight = 1

    n_ld = 100 - 100 * ((line_difference - (-4) )/( 4 - (-4)))
    #next line looks sus
    n_cnes = 100 -100 * ((placement_metrics["change_num_enclosedSpaces"] - (-200))/(200 - (-200)))
    n_cno = 100 - 100 * ((placement_metrics["change_num_overhangs"] - (-2))/(2 - (-2)))
    n_ug = 100 * ((placement_metrics["unique_gaps"] - (-4))/(4 - (-4)))

    summed_weights = ld_weight + cnes_weight + cno_weight + ug_weight
    weighted_sum = ((ld_weight * n_ld)+(cnes_weight * n_cnes)+(cno_weight * n_cno)+(ug_weight * n_ug))/summed_weights

    if placement_metrics["in_enclosure"] == 1 or placement_metrics["is_stuck"] == 1:
        return 0

    return weighted_sum


def get_metrics(board, placement, raw=False):
    if raw:
        metrics = [0,0,0,0,0,0,0]
        metrics[0] = num_lines_cleared(placement, board)
        metrics[1] = change_num_enclosedSpaces(placement, board)
        metrics[2] = heightAdded(placement, board)
        metrics[3] = change_num_overhangs(placement, board)
        metrics[4] = is_in_enclosure(placement, board)
        metrics[5] = is_stuck(placement, board)
        metrics[6] = get_change_roughness(placement, board)
    else:
        metrics = {}
        metrics["num_lines_cleared"] = num_lines_cleared(placement, board)
        metrics["change_num_enclosedSpaces"] = change_num_enclosedSpaces(placement, board)
        metrics["height_added"] = heightAdded(placement, board)
        metrics["change_num_overhangs"] = change_num_overhangs(placement, board)
        metrics["in_enclosure"] = is_in_enclosure(placement, board)
        metrics["is_stuck"] = is_stuck(placement, board)
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

def getNumOverhangs(board):
    num_overhangs = 0
    for x in range(0,10):
        for y in range(2,20):
            if board[x][y] != tetris.BLANK:
                if y + 1 <= 19:
                    if board[x][y+1] == tetris.BLANK:
                        num_overhangs += 1
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

def strip_enclosed(enclosure_list, placements):
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


