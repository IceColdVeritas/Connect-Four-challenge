from itertools import groupby
import numpy as np
from google.cloud import bigquery

import os
import logging


ROW_COUNT = 6
COLUMN_COUNT = 7

# read the file
with open("/Users/fidel/Downloads/connect_four/matchdata.txt", "r") as f:
    lines = f.readlines()
    player_groups = []
    games = []

    # read the file and split the data into two lists
    lists = [list(g) for k, g in groupby(lines, lambda x: x == '\n') if not k]

    # remove the \n from the lists and append the names and moves into two lists
    for list in lists:
        player_groups.append(list[0].strip('\n').split(','))
        games.append(list[1].strip('\n').split(','))


# Create an empty game board
def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=str)
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def get_next_open_row(board, col):
    for r in range(ROW_COUNT-1, -1, -1):
        if board[r][col] == '':
            return r


def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if all(board[r][c+i] == piece for i in range(4)):
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if all(board[r+i][c] == piece for i in range(4)):
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True

game_results = []

for game, players in zip(games, player_groups):
    # Initialize an empty game board after each game
    board = create_board()
    print()
    print("Board created")
    print("Game between " + players[0] + " and " + players[1] + " started!")

    for i, moves in enumerate(game):
        player = players[i % 2]
        col = int(moves[1])
        col -= 1
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, moves[0])
        
        if winning_move(board, moves[0]):
            # Prepare the game results data
            game_results.append({"player1": players[0], "player2": players[1], "winner": player})
            print(f"{player} wins!")
            break

    else:
        print("It's a draw!")

    print(board)

print(game_results)

# Initialize a BigQuery client
client = bigquery.Client()

# Define project, dataset and table variables
project_id = os.environ.get('CONNECT4_PROJECT_ID')
dataset_id = os.environ.get('CONNECT4_DATASET_ID')
table_id = os.environ.get('CONNECT4_TABLE_ID')

# Define the dataset reference
dataset_ref = client.dataset(dataset_id, project=project_id)
logging.info(f"dataset_ref: {dataset_ref}")

# Create the dataset if it doesn't exist
try:
    client.get_dataset(dataset_ref)
except Exception as e:
    dataset = bigquery.Dataset(dataset_ref)
    dataset = client.create_dataset(dataset)
    logging.info(f"Dataset {dataset_id} created.")

# Define the table reference
table_ref = dataset_ref.table(table_id)
logging.info(f"table_ref: {table_ref}")

# Job configuration
schema = [
    bigquery.SchemaField("player_1", "STRING"),
    bigquery.SchemaField("player_2", "STRING"),
    bigquery.SchemaField("winner", "STRING"),
]
logging.info(f"Schema is {schema}")

# Define job configuration
job_config = bigquery.LoadJobConfig(
    schema=schema,
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
)
logging.debug("Job config: {}".format(job_config))

# Load data into the table
job = client.load_table_from_json(game_results, table_ref, job_config=job_config)
logging.info(f"Job: {job}")
job.result()  # Wait for the job to complete

print("Data successfully loaded.")




# def check_winner(board, player):
#     # Check for vertical wins
#     for col in range(7):
#         for row in range(3):
#             if all(board[row+i][col] == player for i in range(4)):
#                 print('Found a vertical win')
#                 return True
    
#     # Check for horizontal wins
#     for row in range(6):
#         for col in range(4):
#             if all(board[row][col+i] == player for i in range(4)):
#                 print('Found a horizontal win')
#                 return True
    
#     # Check for diagonal wins (both directions)
#     for row in range(3):
#         for col in range(4):
#             if all(board[row+i][col+i] == player for i in range(4)):
#                 print('Found a diagonal win')
#                 return True
#             if all(board[row+i][col+3-i] == player for i in range(4)):
#                 print('Found a diagonal win')
#                 return True
    
#     return False


# # Convert moves and update the board
# def play_game(games, player_groups):
#     for game, players in zip(games, player_groups):
#         for i, moves in enumerate(game):
#             player = players[i % 2]
#             col = int(moves[1])
#             col -= 1
#             for row in range(5, -1, -1):
#                 if board[row][col] == '':
#                     board[row][col] = moves[0]
#                     if check_winner(board, player):
#                         print(f"{player} wins!")
#                         break
#                     break

#             # If no winner is found, it's a draw
#             else:
#                 print("It's a draw!")

#             # Print the board
#             for row in board:
#                 print(row)
#             print()

#             # Add a log statement
#             print(f"Player {player} played in column {col+1}\n")


# if __name__=='__main__':
#     play_game(games, player_groups)
