from itertools import groupby

# function that takes in a list of players and a list of moves and calculates the winner in a game of Connect Four
# def calculate_winner(players, moves):
#     # create a list of lists to represent the game board
#     board = [[' ' for x in range(7)] for y in range(6)]

#     # loop through the moves and place the pieces on the board
#     for move in moves:
#         # split the move into a list
#         move = move.split(',')
#         # place the piece on the board
#         board[int(move[1])][int(move[0])] = move[2]

#     # loop through the board and check for a horizontal win
#     for row in board:
#         # loop through the row
#         for i in range(len(row) - 3):
#             # check if there are four pieces in a row
#             if row[i] == row[i + 1] == row[i + 2] == row[i + 3] and row[i] != ' ':
#                 # return the winner
#                 return row[i]

#     # loop through the board and check for a vertical win
#     for i in range(len(board) - 3):
#         # loop through the column
#         for j in range(len(board[i])):
#             # check if there are four pieces in a column
#             if board[i][j] == board[i + 1][j] == board[i + 2][j] == board[i + 3][j] and board[i][j] != ' ':
#                 # return the winner
#                 return board[i][j]

#     # loop through the board and check for a diagonal win
#     for i in range(len(board) - 3):
#         # loop through the row
#         for j in range(len(board[i]) - 3):
#             # check if there are four pieces in a diagonal
#             if board[i][j] == board[i + 1][j + 1] == board[i + 2][j + 2] == board[i + 3][j + 3] and board[i][j] != ' ':
#                 # return the winner
#                 return board[i][j]

#     # loop through the board and check for a diagonal win
#     for i in range(len(board) - 3):
#         # loop through the row
#         for j in range(len(board[i]) - 3):
#             # check if there are four pieces in a diagonal
#             if board[i][j + 3] == board[i + 1][j + 1 + 2] == board[i + 2][j + 2 + 1] == board[i + 3][j + 3] and board[i][j] != ' ':
#                 # return the winner
#                 return board[i][j + 3]


def check_winner(board, player):
    # Check for vertical wins
    for col in range(7):
        for row in range(3):
            if all(board[row+i][col] == player for i in range(4)):
                return True
    
    # Check for horizontal wins
    for row in range(6):
        for col in range(4):
            if all(board[row][col+i] == player for i in range(4)):
                return True
    
    # Check for diagonal wins (both directions)
    for row in range(3):
        for col in range(4):
            if all(board[row+i][col+i] == player for i in range(4)):
                return True
            if all(board[row+i][col+3-i] == player for i in range(4)):
                return True
    
    return False


# read the file
with open("/Users/fidel/Downloads/connect_four/matchdata.txt", "r") as f:
    lines = f.readlines()
    players = []
    moves = []

    # read the file and split the data into two lists
    lists = [list(g) for k, g in groupby(lines, lambda x: x == '\n') if not k]

    # remove the \n from the lists and append the names and moves into two lists
    for list in lists:
        players.append(list[0].strip('\n').split(','))
        moves.append(list[1].strip('\n').split(','))

    print(players)
    print(moves)

# Initialize an empty game board
board = [['' for _ in range(7)] for _ in range(6)]

# Convert moves and update the board
for move in moves:
    for i, m in enumerate(move):
        player = players[i % 2]
        col = int(m[1])
        for row in range(5, -1, -1):
            if board[row][col] == '':
                board[row][col] = player
                break

        if check_winner(board, player):
            print(f"{player} wins!")
            break

# If no winner is found, it's a draw
else:
    print("It's a draw!")
# if __name__=='__main__':
#     calculate_winner(players, moves)

