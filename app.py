class XOs:
    def __init__(self):
        self.space = [[' ' for _ in range(3)] for _ in range(3)]
        self.full = 0

    def insert(self, player, row, col):
        if player not in ('X', 'O'):
            print("Invalid player. Choose 'X' or 'O'.")
            return False
        if 0 <= row < 3 and 0 <= col < 3:
            if self.space[row][col] == ' ':
                self.space[row][col] = player
                self.full+=1
                return True
            else:
                print("Space already occupied.")
                return False
        else:
            print("Invalid row or column.")
            return False
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
        if self.full==9:
            print("The game is a draw")
            return None
        return None  
print("Play Noughts and Crosses")
game = XOs()
while True:
    print("Player 1 Enter row and column number to place '"'X'"'")
    r1=int(input("Row: "))
    c1=int(input("Column: "))
    game.insert('X',r1-1,c1-1)
    key1=game.win()
    if key1 is not None:
        print("Player 1 is the winner")
        break
    game.draw()
    print("Player 2 Enter row and column number to place '"'O'"'")
    r2=int(input("Row: "))
    c2=int(input("Column: "))
    game.insert('O',r2-1,c2-1)
    key2=game.win()
    if key2 is not None:
        print("Player 2 is the winner")
        break add a print function to showcase the board
