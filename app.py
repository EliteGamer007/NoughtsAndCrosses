from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Move(BaseModel):
    player: str  # 'X' or 'O'
    row: int     # 1-based index
    col: int     # 1-based index

class GameState:
    def __init__(self):
        self.space = [[' ' for _ in range(3)] for _ in range(3)]
        self.full = 0

    def insert(self, player, row, col):
        if player not in ('X', 'O'):
            raise ValueError("Invalid player. Choose 'X' or 'O'.")
        if 0 <= row < 3 and 0 <= col < 3:
            if self.space[row][col] == ' ':
                self.space[row][col] = player
                self.full += 1
                return True
            else:
                raise ValueError("Space already occupied.")
        else:
            raise ValueError("Invalid row or column.")

    def win(self):
        for i in range(3):
            if self.space[i][0] == self.space[i][1] == self.space[i][2] != ' ':
                return self.space[i][0]
            if self.space[0][i] == self.space[1][i] == self.space[2][i] != ' ':
                return self.space[0][i]
        if self.space[0][0] == self.space[1][1] == self.space[2][2] != ' ':
            return self.space[0][0]
        if self.space[0][2] == self.space[1][1] == self.space[2][0] != ' ':
            return self.space[0][2]
        return None

    def draw(self):
        return self.full == 9 and self.win() is None

    def get_board(self):
        return self.space

game = GameState()

@app.post("/move")
def make_move(move: Move):
    try:
        game.insert(move.player, move.row - 1, move.col - 1)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    winner = game.win()
    if winner:
        return {"status": "win", "winner": winner, "board": game.get_board()}
    elif game.draw():
        return {"status": "draw", "board": game.get_board()}
    else:
        return {"status": "ongoing", "board": game.get_board()}

@app.get("/board")
def get_board():
    return {"board": game.get_board()}

@app.post("/reset")
def reset_game():
    global game
    game = GameState()
    return {"message": "Game reset."}
