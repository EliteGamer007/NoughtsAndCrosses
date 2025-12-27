# NoughtsAndCrosses
Classic game of Noughts and crosses. Or XO or Tic Tac Toe or whatever you wanna call it. Built with Python and FastAPI, this project goes beyond simple logic by integrating an unbeatable AI, persistent state management, and a reactive frontend.

Features:
1. Advanced AI Opponent (Minimax Algorithm)

Single-Player Mode: Play against a computer that adapts to your skill level.

Difficulty Scaling:

Level 1 (Easy): The AI makes random errors 40% of the time.

Level 2 (Medium): A balanced challenge with occasional mistakes.

Level 3 (Pro): Powered by a recursive Minimax algorithm, this level plays a mathematically perfect game. It is impossible to beat, only draw against. It is set to make a mistake 1 put of a 100 moves.

Dynamic Symbol Selection: The user can choose to play as 'X' (First Turn) or 'O' (Second Turn). The AI automatically adjusts its strategy based on turn order.

2. Robust State Management

Undo System: A full history stack implementation allows players to undo moves. In "Vs Computer" mode, undoing reverts both the computer's and the player's last moves instantly.

Persistent Stats Tracking: A global tracker maintains a record of Wins (W), Draws (D), and Losses (L) specific to each difficulty level.

Win Streak: A live "Streak" counter tracks consecutive wins against the computer, resetting immediately upon a loss or draw.


Victory Celebration: Winning lines are highlighted in gold with a pulsing animation, accompanied by a dynamic confetti burst.

Status Bar: A dedicated bottom bar displays live statistics and streak data.

Auto-Reset: The game automatically detects terminal states (Win/Draw) and resets the board after a 1.5-second delay to keep the gameplay loop smooth.

CORS Enabled: Fully configured to handle cross-origin requests for local testing or deployed environments.

Future Roadmap (Potential)
Multiplayer Rooms: Implementing a lobby system to allow two humans to play on different devices via WebSockets with users creating a code for their own room like Jackbox games.

High Score Persistence: Saving streaks to a database (SQLite/PostgreSQL) so they persist after server restarts.
