from itertools import groupby
import numpy as np
import pandas as pd
import pandasql as ps
from google.cloud import bigquery

import os
from dotenv import load_dotenv
import logging


ROW_COUNT = 6
COLUMN_COUNT = 7

# Load environment variable from .env file
load_dotenv()

# Access the environment variable for the file path
FILE_PATH = os.environ.get('CONNECT4_FILE_PATH')

# read the file
with open(FILE_PATH, "r") as f:
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

# The code below runs the game of connect four. It uses a for loop to iterate through the list of games. 
# Each game is played by two players, and the for loop iterates through each move in the game. 
# The player is determined by the index of the move in the game list. 
# The game board is a list of lists, and the drop_piece function places the player's piece on the board. 
# The get_next_open_row function determines the row that the piece will be placed on. 
# If the winning_move function returns True, the game ends and the winner is declared. 
# If the for loop is completed without a winner, the game is declared a draw. 

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

# Convert the game results to a data frame
game_results_df = pd.DataFrame(game_results, columns=["player1", "player2", "winner"])
print()
print("Game results data frame:")
print(game_results_df)

# Query the data frame to aggregate the results
query = """
    with base as (
        SELECT
            player_id,
            COUNT(*) AS games_played,
            SUM(CASE WHEN winner = player_id THEN 1 ELSE 0 END) AS won,
            SUM(CASE WHEN winner <> player_id THEN 1 ELSE 0 END) AS lost,
            ROUND(SUM(CASE WHEN winner = player_id THEN 1 ELSE 0 END) * 100 / COUNT(*), 2) AS win_percentage
        FROM (
            SELECT player1 AS player_id, winner FROM game_results_df
            UNION ALL
            SELECT player2 AS player_id, winner FROM game_results_df
        )
        GROUP BY player_id
    )
    SELECT
        ROW_NUMBER() OVER(ORDER BY won DESC) AS player_rank,
        *
    FROM base
    ORDER BY player_rank ASC
"""

# Run the SQL query on the DataFrame
result_df = ps.sqldf(query, locals())
print(result_df)

# Initialize a BigQuery client
client = bigquery.Client()

# Define project, dataset and table variables
project_id = os.environ.get('CONNECT4_PROJECT_ID')
dataset_id = os.environ.get('CONNECT4_DATASET_ID')
table_id = os.environ.get('CONNECT4_TABLE_ID')

# Define the dataset reference
table_ref = str(project_id) + "." + str(dataset_id) + "." + str(table_id)

# Schema for the table
schema = [
    bigquery.SchemaField("player_rank", "INT64"),
    bigquery.SchemaField("player_id", "STRING"),
    bigquery.SchemaField("games_played", "INT64"),
    bigquery.SchemaField("won", "INT64"),
    bigquery.SchemaField("lost", "INT64"),
    bigquery.SchemaField("win_percentage", "FLOAT64")
]
logging.info(f"Schema is {schema}")

# Define job configuration
job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition="WRITE_TRUNCATE",
)
logging.debug("Job config: {}".format(job_config))

# Load data into the table
job = client.load_table_from_dataframe(result_df, table_ref, job_config=job_config)
logging.info(f"Job: {job}")
job.result()  # Wait for the job to complete

table = client.get_table(table_ref)  # Make an API request.
print(
    "Loaded {} rows and {} columns to {}".format(
        table.num_rows, len(table.schema), table_ref
    )
)
