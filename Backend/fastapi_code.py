from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS so frontend can make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
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

    def insert(self, player, row, col):
        if self.finished:
            raise ValueError("Game over. Please reset to start a new game.")
        if player not in ('X', 'O'):
            raise ValueError("Invalid player. Use 'X' or 'O'.")
        if not (0 <= row < 3 and 0 <= col < 3):
            raise ValueError("Row and column must be between 0 and 2.")
        if self.space[row][col] != ' ':
            raise ValueError("Space already occupied.")
        self.space[row][col] = player
        self.full += 1

    def win(self):
        # Check rows
        for i in range(3):
            if self.space[i][0] == self.space[i][1] == self.space[i][2] != ' ':
                self.finished = True
                return self.space[i][0], [[i, 0], [i, 2]]
        # Check columns
        for i in range(3):
            if self.space[0][i] == self.space[1][i] == self.space[2][i] != ' ':
                self.finished = True
                return self.space[0][i], [[0, i], [2, i]]
        # Check main diagonal
        if self.space[0][0] == self.space[1][1] == self.space[2][2] != ' ':
            self.finished = True
            return self.space[0][0], [[0, 0], [2, 2]]
        # Check anti-diagonal
        if self.space[0][2] == self.space[1][1] == self.space[2][0] != ' ':
            self.finished = True
            return self.space[0][2], [[0, 2], [2, 0]]
        return None

    def draw(self):
        if self.full == 9 and not self.win():
            self.finished = True
            return True
        return False

    def get_board(self):
        return self.space

game = GameState()

@app.post("/move")
def make_move(move: Move):
    try:
        game.insert(move.player, move.row, move.col)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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

@app.get("/board")
def get_board():
    return {"board": game.get_board()}

@app.post("/reset")
def reset_game():
    global game
    game = GameState()
    return {"message": "Game reset.", "board": game.get_board()}

