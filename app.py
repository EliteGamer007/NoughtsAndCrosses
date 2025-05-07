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
                self.full += 1
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
        if self.full == 9:
            print("The game is a draw")
            return True
        return False

    def print_board(self):
        print("Current Board:")
        for row in self.space:
            print(" | ".join(row))
            print("-" * 9)


print("Play Noughts and Crosses")
game = XOs()
while True:
    print("Player 1 Enter row and column number to place 'X'")
    r1 = int(input("Row: "))
    c1 = int(input("Column: "))
    if game.insert('X', r1 - 1, c1 - 1):
        game.print_board()
        if game.win() == 'X':
            print("Player 1 is the winner")
            break
        if game.draw():
            break

    print("Player 2 Enter row and column number to place 'O'")
    r2 = int(input("Row: "))
    c2 = int(input("Column: "))
    if game.insert('O', r2 - 1, c2 - 1):
        game.print_board()
        if game.win() == 'O':
            print("Player 2 is the winner")
            break
