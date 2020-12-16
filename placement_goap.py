import tetris
import goap
from argparse import ArgumentParser
from typing import Optional
from goap.action import Action, reference, ActionStatus, StateType
from goap.planner import Goal, Planner, PlanStatus
from goap.director import Director
from time import time
import copy
from tetris import PIECES

global goalPiece
global origPiece
global currPiece
goalPiece = {'shape': "Z",
			 'rotation': 0,
			 'x': 0,
			 'y': 16,
			}
origPiece = {'shape': "Z",
			 'rotation': 0,
			 'x': 0,
			 'y': 3,
			}

currPiece = {'shape': "Z",
			 'rotation': 0,
			 'x': 0,
			 'y': 3,
			}



def can_rotate(piece,board,rotLeft=False):
	tempPiece = copy.deepcopy(piece)
	if rotLeft: rotation = (tempPiece['rotation'] + 1) % len(PIECES[tempPiece['shape']])
	tempPiece['rotation'] = rotation

class MoveLeft(Action):
	effects = {"movedLeft": True, "movedDown": False,}
	preconditions = {"canMoveLeft": True, "movedDown": True, "movedLeft": False}

	def on_enter(self, world_state, goal_state):
		world_state['x'] = world_state['x'] - 1
		tempPiece = tetris.getPiece(world_state['shape'], world_state['rotation'], world_state['x'], world_state['y'])
		world_state['canMoveLeft'] = tetris.isValidPosition(world_state['board'], tempPiece, adjX=-1)

class MoveRight(Action):
	effects = {"movedRight": True, "movedDown": False, "x": world_state['x'] + 1}
	preconditions = {"canMoveRight": True, "movedDown": True, "movedRight": False}

	def on_enter(self, world_state, goal_state):
		world_state['x'] = world_state['x'] + 1
		tempPiece = tetris.getPiece(world_state['shape'], world_state['rotation'], world_state['x'], world_state['y'])
		world_state['canMoveLeft'] = tetris.isValidPosition(world_state['board'], tempPiece, adjX=1)

class MoveDown(Action):
	effects = {"movedRight": False, "movedLeft": False, "movedDown": True}
	preconditions = {"canMoveDown": True}

	def on_enter(self, world_state, goal_state):
		#world_state['y'] = world_state['y'] + 1
		#tempPiece = tetris.getPiece(world_state['shape'], world_state['rotation'], world_state['x'], world_state['y'])
		#world_state['canMoveDown'] = tetris.isValidPosition(world_state['board'], tempPiece, adjY=1)
		pass

class PlacePiece(Goal):
	'''
	state = {"x": goalPiece['x'],
			 "y": goalPiece['y'],
			 "rotation": goalPiece['rotation']}
	'''
	state = {"x": 0,
			 "y": 4
			}
if __name__ == "__main__":
	parser = ArgumentParser(description="Run demo GOAP program")
	parser.add_argument("-graph", type=str)
	args = parser.parse_args()

	board = tetris.getBlankBoard()

	world_state = dict(rotation= copy.copy(origPiece['rotation']),
					   x= copy.copy(origPiece['x']),
					   y= copy.copy(origPiece['y']),
					   shape= copy.copy(origPiece['shape']),
					   board=board,
					   movedDown=False,
					   movedLeft=False,
					   movedRight=False,
	   				   canMoveLeft=True,
	                   canMoveRight=True,
	                   canMoveDown=True)

	actions = [a() for a in Action.__subclasses__()]
	goals = [g() for g in Goal.__subclasses__()]

	planner = Planner(actions, world_state)
	director = Director(planner, world_state, goals)

	plan = director.find_best_plan()


	print("Initial State:", world_state)
	print("Plan:", plan)
	print("----Running Plan" + "-" * 34)

	if args.graph:
		from goap.visualise import visualise_plan

		visualise_plan(plan, args.graph)

	while plan.update() == PlanStatus.running:
		continue

	print("-" * 50)
	print("Final State:", world_state)

