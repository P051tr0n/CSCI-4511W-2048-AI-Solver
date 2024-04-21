import engine, random, curses

COLORS = {0:0,2:1,4:2,8:3,16:4,32:5,64:6,128:7,256:8,512:9,1024:10,2048:11,4096:12,8192:13,16384:13,32768:12,65536:12}

def makeGame():
	"""
	Creates a new instance of a game
	"""
	game = engine.Engine()
	return game

def drawBoard(board, screen):
	"""
	Draws a given board on a given curses screen
	"""
	for row in enumerate(board):
		for item in enumerate(row[1]):
			screen.addstr(8+3*row[0], 40+6*item[0], str(item[1]), curses.color_pair(COLORS[item[1]]))
	screen.refresh()

def copyBoard(board):
	newBoard = makeGame().board
	for row in enumerate(board):
		for item in enumerate(row[1]):
			newBoard[row[0]][item[0]] = item[1]
	return newBoard


# New function: find the move-distance between a tile and all other tiles on the board of the same value
def move_distance(board, row, col):
	tile = board[row][col]

	if tile == 0:
		return 0

	dist = 0
	for j in range(4):
		for i in range(4):
			# if the ith, jth tile has the same value as the tile we're focused on (and isn't that tile itself),
			if board[i][j] == tile and not (i == row and j == col):
				# # if tile of same value shares a row or column, then it will only need one move (ignoring the presence of other tiles)
				# dist += 1 + (i != row and j != col)	

				dist += abs(row - i) + abs(col - j)
	return dist

# New function: find the value-similarity for a specific tile
def value_similarity(board, row, col):
	# Find the coordinates of all possible neighbors (filter out the following edge cases:    tile itself                           and  negative coordinates                           and  coordinates outside the board)
	shifts = [-1, 0, 1]
	neighbor_coords = [[row + shifts[i], col + shifts[j]] for j in range(3) for i in range(3) if (shifts[i] != 0 or shifts[j] != 0) and (row + shifts[i] >= 0 and col + shifts[j] >= 0) and (row + shifts[i] < 4 and col + shifts[j] < 4)]

	output = 0
	for n in neighbor_coords:
		if (board[n[0]][n[1]] != 0):
			output += abs(board[n[0]][n[1]] - board[row][col])
	return output

# New function: find weight for each coordinate according to the N1 Pattern and sum weighted tile values
def N1_pattern_weight(board):
	N1_pattern_weights = [[16, 15, 14, 13],[15, 14, 13, 12],[14, 13, 12, 11],[13, 12, 11, 10]]
	sum = 0
	for j in range(4):
		for i in range(4):
			sum += board[i][j] * N1_pattern_weights[i][j]
	return sum

# New function: calculate a penalty based on diagonally adjacent tiles
def diag_penalty(board, row, col):
	if (board[row][col] == 0):
		return 0

	shifts = [-1, 0, 1]
	neighbor_coords = [[row + shifts[i], col + shifts[j]] for j in range(3) for i in range(3) if (shifts[i] != 0 or shifts[j] != 0) and (row + shifts[i] >= 0 and col + shifts[j] >= 0) and (row + shifts[i] < 4 and col + shifts[j] < 4)]
	
	output = 0
	for n in neighbor_coords:
		if (board[n[0]][n[1]] == board[row][col]) and (abs(n[0] - row) == 1 and abs(n[1] - col) == 1):
			output += 2
	return output

# New function: calculate a penalty based on location of certain-valued tiles
def loc_penalty(board):
	middle = [(1,1), (1,2), (2,1), (2,2)]
	smalls = [2, 4, 8, 16]
	
	output = 0
	for j in range(4):
		for i in range(4):
			if (board[i][j] == 0):
				continue

			if ((i,j) in middle) and not (board[i][j] in smalls):	# penalize if there are large values in the middle coords
				output += 1
			if not ((i,j) in middle) and (board[i][j] in smalls):	# penalize if there are small values in the outer coords
				output += 1
	return output

def runRandom(board, firstMove):
	"""
	Returns the end score of a given board played randomly after moving in a given direction.
	"""
	randomGame = makeGame()					#make a new game
	moveList = randomGame.moveList
	randomGame.board = copyBoard(board) 	#copy the given board to the new game
	randomGame.makeMove(firstMove) 			#send the initial move

	while True:								#keep sending random moves until game is over
		if randomGame.gameOver():
			break
		randMove = random.choice(moveList)
		randomGame.makeMove(randMove)

	# # Original version: commenting out to replace with custom version for final project
	# return randomGame.score

	# New version: calculate score of final state using move-distance and value-similarity for each tile
	end_board = randomGame.board
	weighted_sum = N1_pattern_weight(end_board)
	score = weighted_sum
	for j in range(len(end_board)):
		for i in range(len(end_board[0])):
			if (end_board[i][j] != 0):
				frac = 	1.0 / (move_distance(end_board, i, j) * value_similarity(end_board, i , j) + 0.01)
				penalty = 3 * diag_penalty(end_board, i, j) + 4 * loc_penalty(end_board)

				score += 0.5 * frac - 0.2 * penalty
	# print(score)
	return score

def bestMove(game, runs):
	"""
	Returns the best move for a given board.
	Plays "runs" number of games for each possible move and calculates which move had best avg end score.
	"""
	average = 0
	bestScore = -100000 # modifying starting value of bestScore since there is now a penalty that could make score negative
	moveList = game.moveList

	for moveDir in moveList:
		average = 0
		for x in range(runs):
			result = runRandom(game.board, moveDir)
			average += result
		average = average/runs
		if average >= bestScore:
			bestScore = average
			move = moveDir
	return move



def solveGame(runs, screen):
	"""
	AI that plays a game till the end given a number of runs to make per move

	"""
	mainGame = makeGame()
	moveList = mainGame.moveList
	isDynamic = False

	#If runs is set to dynamic, increase the number of runs as score increases
	if runs == 'Dynamic':
		isDynamic = True

	while True:
		if mainGame.gameOver():
			break

		if isDynamic:
			runs = int(1 + (0.01)*mainGame.score)

		if runs > 0:
			move = bestMove(mainGame, runs)
		else:
			move = random.choice(moveList)
			
		mainGame.makeMove(move)
		screen.clear()
		drawBoard(mainGame.board, screen)

	return(mainGame)