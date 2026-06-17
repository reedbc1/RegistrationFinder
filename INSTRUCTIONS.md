# Instructions for Running Locally

## Setting up the local environment
### Step 1. Create virtual environment  
Open PowerShell and run the following command  
`python -m venv .venv`  

### Step 2. Open virtual environment  
For **Linux**, run the following in a bash terminal  
`$ source .venv/bin/activate`  

For **Windows**, run the following in PowerShell
`PS C:\> .venv\Scripts\Activate.ps1`

### Step 3. Install dependencies located in requirements.txt  
`pip install -r requirements.txt`

For more details about using venv, [click here](https://docs.python.org/3/library/venv.html#how-venvs-work).

## Running the website locally
### Run with Flask  
`flask --app app run`

### Run with Gunicorn (Linux Only)  
`gunicorn --bind 0.0.0.0:8080 app:app`

## Running tests
### Run unit tests
`python -m unittest tests/unit.py`

### Run integration tests
`python -m unittest tests/integration.py`

## Cleaning up git branches
After deleting a branch (after it has been successfully merged, for example), 
it can be helpful to remove the merged repository from remote and local git branches. 
This is because the remote will no longer connect since the branch has 
been deleted from GitHub. I like to also remove it locally so that my local branches 
are identical to the remote branches.  

1. Delete the desired branch on GitHub
2. To remove the branch from the remote, run `git fetch --prune`
3. To remove the branch locally, run `git branch -d your_branch_name_here`  

**DO NOT delete the main branch from GitHub**.   
Other branches with new commits/features that you would like the app to use 
should be merged to main whenever possible.
Merge conflicts can be dealt with if they occur, but they are best avoided.