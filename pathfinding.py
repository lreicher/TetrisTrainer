import tetris
# x {-2, 7}
# y {-1 18}



# Falling Piece x,y,r,s
# Placement Piece x,y,r,s

# All neighbor moves
    # For each rotation of falling Piece
    #   For move_left and move_right
    #   For drop

# Has dropped
# Has moved horizontally

# board

# . is blank
# BLANK

'''
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
'''

def pieceToBoard(piece):
    blocks = []
    shapeToDraw = tetris.PIECES[piece['shape']][piece['rotation']]
    for x in range(tetris.TEMPLATEWIDTH):
        for y in range(tetris.TEMPLATEHEIGHT):
            if shapeToDraw[y][x] != tetris.BLANK:
                blocks.append((piece['x'] + x, piece['y'] + y))
    return blocks

#
def get_enclosures(board):
    enclosed_boxes = []
    searched_space = []
    for y in range(2,20):
        for x in range(0,10):
            if board[x][y] == tetris.BLANK and (x,y) not in searched_space:
                empty = []
                full = []
                pass

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

def get_shortestHeight(placements, board):
    minimum_height_index = None
    minimum_height = 500
    for i in range(len(placements)):
        height_added = heightAdded(placements[i], board)
        if height_added < minimum_height:
            minimum_height = height_added
            minimum_height_index = i
    return placements[minimum_height_index]




