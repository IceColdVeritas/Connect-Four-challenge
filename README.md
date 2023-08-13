# Connect-Four-challenge
Determine the winner in a Connect Four game

## Create a virtual environment in your terminal
Before starting installing packages, it's best to create an isolated virtual environment.
One simple option is to use Python's build in native tool.

To create a virtual environment, execute the following code in your terminal:
```javascript Python
python3 -m venv <name_of_virtualenv>
```

To activate it, execute:
```javascript Python
source <name_of_virtualenv>/bin/activate
```

When you're done, you can deactivate your virtual environment with:
``` javascript Python
deactivate
```
## Install the packages in the requirements file
Execute the following command to install all dependencies needed, which are listed in the requirements.txt file:
``` javascript Python
pip install -r requirements.txt
```
## Set up environmental variables
Set up your dataset id and table id as environmental variables to connect to an external database (BigQuery here) to make it more secure by not leaving any trace of it in your IDE.

To set up said variables, execute the following code snippets:
```bash Python
export CONNECT4_DATASET_ID=your_project_id
export CONNECT4_DATASET_ID=your_dataset_id
export CONNECT4_TABLE_ID=your_table_id
```
Alternatively, you can also create a .env file in your project's root and assign the environmental variables there, e.g. ```CONNECT4_FILE_PATH="your_file_path"```.

Install the python-dotenv library then using the following command:
```bash Python
pip install python-dotenv
```

Without it your game results data will not be populated in your table in your bigquery project!

## Connect to the bigquery database
To have these results available as a table in bigquery, the google cloud sdk is required to be installed.
Steps:
    1. Install the gcloud<https://cloud.google.com/sdk/docs/install> CLI package
    2. To initialize gcloud CLI, run ```gcloud init```