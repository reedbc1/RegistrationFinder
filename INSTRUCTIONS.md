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
Unit tests  
`python -m unittest tests/unit.py`

### Run integration tests
`python -m unittest tests/integration.py`
