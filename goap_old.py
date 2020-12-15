from goapy import World, Planner, Action_List
import tetris
import copy

if __name__ == '__main__':
	def canMoveRight():
		return True

	def movedLeft(x,y):
		x = x + 1
		return x

	def canMoveLeft(x,y,rotation):
		return tetris.isValidPosition(
			board,
			{'shape': shape,
			'rotation': rot,
			'x': x,
			'y': y
			}, adjX=+1)


	fallingPiece = {'shape': 'J',
			'rotation': 0,
			'x': -1,
			'y': 5
			}

	goalPiece = {'shape': 'J',
		     'rotation': 0,
		     'x': 4,
		     'y': 16
		     }

	board = tetris.getBlankBoard()
	tempPiece = copy.deepcopy(fallingPiece)
	x = tempPiece['x']
	y = tempPiece['y']
	rot = tempPiece['rotation']
	shape = tempPiece['shape']

	_brain = World()

	_movement_brain = Planner('x',
				   'y',
				   'rotation',
				   'canMoveLeft',
				   'canMoveRight',
				   'moved_down',
				   'moved_horizontal',
				  )

	_movement_brain.set_start_state(x = fallingPiece['x'],
					y = fallingPiece['y'],
					rotation = fallingPiece['rotation'],
					canMoveLeft = True,
					canMoveRight = True,
					moved_down = True,
					moved_horizontal = False)

	_movement_brain.set_goal_state(x = goalPiece['x'],
				       y = goalPiece['y'],
				       rotation = goalPiece['rotation'])

	_movement_actions = Action_List()

	_movement_actions.add_condition('move_left',
					canMoveLeft = True,
					moved_down = True
					)

	_movement_actions.add_reaction('move_left',
				       x = x,
				       movedHorizontal = True,
				       moved_down = False,
				       canMoveLeft = canMoveLeft(x,y)
				       )

	_movement_actions.add_condition('move_right',
					canMoveRight = True,
					moved_down = True
					)

	_movement_actions.add_reaction('move_right',
					x =- 1,
					movedHorizontal = True,
					moved_down = False,
					#chicken = fallingPiece['x'],
					canMoveRight = canMoveRight()
					)

	_movement_actions.add_condition('rotate_left',
					rotLeftGoal = True
					)

	_movement_actions.add_reaction('rotate_left',
					rotation = (fallingPiece['rotation'] + 1) % len(tetris.PIECES[fallingPiece['shape']])
					)

	_movement_actions.add_condition('move_down',
					canMoveDown = True,
					movingHorizontal = True
					)

	_movement_actions.add_reaction('move_down',
					lowerPiece = fallingPiece['y'] + 1
					)

	_movement_actions.add_condition('drop',
					can_drop = True
					)

	_movement_actions.add_reaction('drop',

					)

	_movement_brain.set_action_list(_movement_actions)
