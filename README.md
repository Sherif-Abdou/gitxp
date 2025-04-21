# GitXP

GitXP is a project that keeps track and gamifies your github history making use of the GitHub API. This project is built using sqlalchemy and flask on the backend, interfacing with a Postgres SQL database. On the frontend, we use ReactJS.

## Installation

Dependencies:
* Postgres
* Python
* Npm and node

## Installation instructions
```
git clone https://github.com/Sherif-Abdou/gitxp
cd backend
pip install -r requirements.txt
cd ..
cd frontend
npm install
cd ..
```

### Backend: 
* Ensure `POSTGRES_DB` url and `GITHUB_PERSONAL_ACCESS_TOKEN` are available
* `POSTGRES_DB` key format: `postgresql+psycopg2://<username>:<password>@<ip>:<port>/<databasename>`
  - `<username>`: Username used to sign into postgres database
  - `<password>`: Password used to sign into postgres database
  - `<ip>`: IP address or hostname where the database lives
  - `:<port>`: Optional port where the database is hosted on
  - `<databasename>`: Name of the database you wish to connect to
* Recommendation Put the keys in a .env file inside `backend/`

### Frontend:
* Ensure clerk publishable key is available in env
* Recommendation Put the key in a .env file inside `frontend/`

## Running
First, run the backend
```
cd backend
flask run --app main run --debug
```

Then, run the frontend
```
cd frontend
npm run dev
```
