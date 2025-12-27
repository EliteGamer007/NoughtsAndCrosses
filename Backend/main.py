import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Tuple, Dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game_stats = {
    1: {"w": 0, "l": 0, "d": 0},
    2: {"w": 0, "l": 0, "d": 0},
    3: {"w": 0, "l": 0, "d": 0},
    "streak": 0
}

class Move(BaseModel):
    player: str
    row: int
    col: int
    level: int = 2

class GameState:
    def __init__(self):
        self.space = [[' ' for _ in range(3)] for _ in range(3)]
        self.full = 0
        self.finished = False
        self.history = []

    def save_state(self):
        board_snapshot = [row[:] for row in self.space]
        self.history.append((board_snapshot, self.full, self.finished))

    def undo(self) -> bool:
        if not self.history:
            return False
        self.space, self.full, self.finished = self.history.pop()
        return True
    
    def insert(self, player: str, row: int, col: int):
        if self.finished:
            raise ValueError("Game over.")
        
        self.save_state()

        if self.space[row][col] != ' ':
            self.history.pop()
            raise ValueError("Occupied.")
        
        self.space[row][col] = player
        self.full += 1

    def win(self) -> Optional[Tuple[str, List[List[int]]]]:
        for i in range(3):
            if self.space[i][0] == self.space[i][1] == self.space[i][2] != ' ':
                self.finished = True
                return self.space[i][0], [[i, 0], [i, 1], [i, 2]]
            if self.space[0][i] == self.space[1][i] == self.space[2][i] != ' ':
                self.finished = True
                return self.space[0][i], [[0, i], [1, i], [2, i]]
        
        if self.space[0][0] == self.space[1][1] == self.space[2][2] != ' ':
            self.finished = True
            return self.space[0][0], [[0, 0], [1, 1], [2, 2]]
        if self.space[0][2] == self.space[1][1] == self.space[2][0] != ' ':
            self.finished = True
            return self.space[0][2], [[0, 2], [1, 1], [2, 0]]
        return None

    def draw(self) -> bool:
        if self.full == 9 and not self.win():
            self.finished = True
            return True
        return False

    def get_best_move_minimax(self, cpu_player: str) -> List[int]:
        human_player = 'X' if cpu_player == 'O' else 'O'
        best_score = -float('inf')
        move = [-1, -1]
        
        for r in range(3):
            for c in range(3):
                if self.space[r][c] == ' ':
                    self.space[r][c] = cpu_player
                    self.full += 1
                    score = self.minimax(0, False, cpu_player, human_player)
                    self.space[r][c] = ' '
                    self.full -= 1
                    if score > best_score:
                        best_score = score
                        move = [r, c]
        return move

    def minimax(self, depth: int, is_maximizing: bool, cpu_player: str, human_player: str) -> int:
        win_res = self.win()
        if win_res:
            winner = win_res[0]
            self.finished = False
            return 10 - depth if winner == cpu_player else depth - 10
        if self.full == 9: return 0

        if is_maximizing:
            best_score = -float('inf')
            for r in range(3):
                for c in range(3):
                    if self.space[r][c] == ' ':
                        self.space[r][c] = cpu_player
                        self.full += 1
                        score = self.minimax(depth + 1, False, cpu_player, human_player)
                        self.space[r][c] = ' '
                        self.full -= 1
                        best_score = max(score, best_score)
            return int(best_score)
        else:
            best_score = float('inf')
            for r in range(3):
                for c in range(3):
                    if self.space[r][c] == ' ':
                        self.space[r][c] = human_player
                        self.full += 1
                        score = self.minimax(depth + 1, True, cpu_player, human_player)
                        self.space[r][c] = ' '
                        self.full -= 1
                        best_score = min(score, best_score)
            return int(best_score)

game = GameState()

def process_move_result(level: int, user_symbol: str = 'X'):
    if level not in [1, 2, 3]: level = 2

    result = game.win()
    if result:
        winner, winning_line = result
        if winner == user_symbol:
            game_stats[level]["w"] += 1
            game_stats["streak"] += 1
        else:
            game_stats[level]["l"] += 1
            game_stats["streak"] = 0
            
        return {
            "status": "win",
            "winner": winner,
            "winning_line": winning_line,
            "board": game.space,
            "stats": game_stats
        }
    
    if game.draw():
        game_stats[level]["d"] += 1
        game_stats["streak"] = 0
        return {
            "status": "draw",
            "board": game.space,
            "stats": game_stats
        }
        
    return {
        "status": "ongoing",
        "board": game.space,
        "stats": game_stats
    }

@app.post("/move")
def make_move(move: Move):
    try:
        game.insert(move.player, move.row, move.col)
        return process_move_result(level=move.level, user_symbol=move.player)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/undo")
def undo_move():
    if len(game.history) >= 2:
        game.undo() 
        game.undo() 
    return {
        "status": "ongoing", 
        "board": game.space, 
        "finished": game.finished,
        "stats": game_stats
    }

@app.post("/ai-move")
def ai_move(level: int = 2, user_symbol: str = 'X'):
    if game.finished: raise HTTPException(status_code=400, detail="Finished")
    
    cpu_symbol = 'O' if user_symbol == 'X' else 'X'

    skill_map = {1: 60, 2: 85, 3: 99}
    roll = random.randint(1, 100)
    empty = [[r, c] for r in range(3) for c in range(3) if game.space[r][c] == ' ']
    
    if not empty: raise HTTPException(status_code=400, detail="No moves")

    if roll > skill_map.get(level, 85):
        coords = random.choice(empty)
    else:
        coords = game.get_best_move_minimax(cpu_player=cpu_symbol)

    game.insert(cpu_symbol, coords[0], coords[1])
    return process_move_result(level=level, user_symbol=user_symbol)

@app.get("/board")
def get_board():
    return {"board": game.space, "stats": game_stats}

@app.post("/reset")
def reset_game():
    global game
    game = GameState()
    return {"status": "reset", "board": game.space, "stats": game_stats}