import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Tuple

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Move(BaseModel):
    player: str
    row: int
    col: int

class GameState:
    def __init__(self):
        self.space = [[' ' for _ in range(3)] for _ in range(3)]
        self.full = 0
        self.finished = False
        self.history=[]

    def save_state(self):
        board_snapshot = [row[:] for row in self.space]
        self.history.append((board_snapshot, self.full, self.finished))

    def undo(self):
        if not self.history:
            return False
        self.space, self.full, self.finished = self.history.pop()
        return True
    
    def insert(self, player: str, row: int, col: int):
        if self.finished:
            raise ValueError("Game over. Please reset to start a new game.")
        self.save_state()
        if player not in ('X', 'O'):
            raise ValueError("Invalid player. Use 'X' or 'O'.")
        if not (0 <= row < 3 and 0 <= col < 3):
            raise ValueError("Row and column must be between 0 and 2.")
        if self.space[row][col] != ' ':
            self.history.pop()
            raise ValueError("Space already occupied.")
        
        self.space[row][col] = player
        self.full += 1

    def win(self) -> Optional[Tuple[str, List[List[int]]]]:
        # Rows
        for i in range(3):
            if self.space[i][0] == self.space[i][1] == self.space[i][2] != ' ':
                self.finished = True
                return self.space[i][0], [[i, 0], [i, 2]]
        # Columns
        for i in range(3):
            if self.space[0][i] == self.space[1][i] == self.space[2][i] != ' ':
                self.finished = True
                return self.space[0][i], [[0, i], [2, i]]
        # Diagonals
        if self.space[0][0] == self.space[1][1] == self.space[2][2] != ' ':
            self.finished = True
            return self.space[0][0], [[0, 0], [2, 2]]
        if self.space[0][2] == self.space[1][1] == self.space[2][0] != ' ':
            self.finished = True
            return self.space[0][2], [[0, 2], [2, 0]]
        return None

    def draw(self) -> bool:
        if self.full == 9 and not self.win():
            self.finished = True
            return True
        return False

    def get_best_move_minimax(self) -> List[int]:
        best_score = -float('inf')
        move = [-1, -1]
        
        for r in range(3):
            for c in range(3):
                if self.space[r][c] == ' ':
                    self.space[r][c] = 'O'
                    self.full += 1
                    score = self.minimax(0, False)
                    self.space[r][c] = ' '
                    self.full -= 1
                    if score > best_score:
                        best_score = score
                        move = [r, c]
        return move

    def minimax(self, depth: int, is_maximizing: bool) -> int:
        win_res = self.win()
        if win_res:
            winner = win_res[0]
            self.finished = False 
            return 10 - depth if winner == 'O' else depth - 10
        
        if self.full == 9:
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for r in range(3):
                for c in range(3):
                    if self.space[r][c] == ' ':
                        self.space[r][c] = 'O'
                        self.full += 1
                        score = self.minimax(depth + 1, False)
                        self.space[r][c] = ' '
                        self.full -= 1
                        best_score = max(score, best_score)
            return int(best_score)
        else:
            best_score = float('inf')
            for r in range(3):
                for c in range(3):
                    if self.space[r][c] == ' ':
                        self.space[r][c] = 'X'
                        self.full += 1
                        score = self.minimax(depth + 1, True)
                        self.space[r][c] = ' '
                        self.full -= 1
                        best_score = min(score, best_score)
            return int(best_score)

    def get_board(self):
        return self.space

game = GameState()

def process_move_result(player_type: str):
    result = game.win()
    if result:
        winner, winning_line = result
        return {
            "status": "win",
            "winner": winner,
            "winning_line": winning_line,
            "board": game.get_board()
        }
    elif game.draw():
        return {
            "status": "draw",
            "board": game.get_board()
        }
    else:
        return {
            "status": "ongoing",
            "board": game.get_board()
        }

@app.post("/move")
def make_move(move: Move):
    try:
        game.insert(move.player, move.row, move.col)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return process_move_result(move.player)

@app.post("/undo")
def undo_move():
    success = game.undo() 
    if success:
        game.undo() 
    return {"message": "Undone", "board": game.get_board(), "finished": game.finished}

@app.post("/ai-move")
def ai_move(level: int = 2):
    if game.finished:
        raise HTTPException(status_code=400, detail="Game already finished.")
    
    # Map 1-3 to skill percentage (Level 3 = 1 error in 100)
    skill_map = {1: 50, 2: 80, 3: 99}
    skill_threshold = skill_map.get(level, 70) 

    roll = random.randint(1, 100)
    empty_cells = [[r, c] for r in range(3) for c in range(3) if game.space[r][c] == ' ']
    
    if not empty_cells:
        raise HTTPException(status_code=400, detail="No moves left.")

    if roll > skill_threshold:
        # BLUNDER: Pick a random empty cell
        coords = random.choice(empty_cells)
    else:
        coords = game.get_best_move_minimax()

    row, col = coords
    game.insert('O', row, col)
    
    return process_move_result('O')

@app.get("/board")
def get_board():
    return {"board": game.get_board()}

@app.post("/reset")
def reset_game():
    global game
    game = GameState()
    return {"message": "Game reset.", "board": game.get_board()}