# Project Intro
A fastapi websocket and API server that will show a leaderboard of top users performing on various games or activities. This project is from the [roadmap.sh](https://roadmap.sh/) and can be found at here: [Real Time Leaderboard System](https://roadmap.sh/projects/realtime-leaderboard-system)


# Tools
- `FastAPI[standard]>=0.115.11`
- `redis>=5.2.1`
- `PostgreSQL=latest`
- `uv` for project management
- `websockets>=15.0.1`
- `ruff>=0.11.0`
- `pyjwt>=2.10.1`
- `faker>=37.1.0`


# Features
- User Authentication and Authorization
    - User Signup and Login.
    - JWT-based accesss with protected routes for both websocket and API.
    - Bcrypt password hashing.

- Realtime Score Submission and Leaderboard      
    - Live leaderboard fetch.
    - Leaderboard pagination.
    - Leaderboard fetch by game.
    - Update leaderboard upon score submission.
    - Get current users' top score.
    - Fetch top players report by a given period with limiting.


# Installation
1. Clone repository
```git clone https://github.com/HAL94/fast-realtime.git```

2. Navigate to project directory: `cd fast-realtime`

3. Create environment with your favourite tool.
    - using `uv`: `uv venv .venv`
    - activate (Windows): `.venv\Scripts\activate`
    - activate (MacOS/Linux): `source .venv/bin/activate`

4. Setup `.env`:
```
PG_USER="postgres"
PG_PW="postgres"
PG_SERVER="localhost"
PG_PORT="5432" 
PG_DB="leaderboard_db"

SECRET_KEY=jwt_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60.0
```
Note: Redis env was not set, it is hard-coded within object creation (Sorry :P).

5. Install dependencies:
with your tool of choice or with uv: `uv sync`

6. Deactivate environement
```deactivate```

# Usage
Use one of the following commands:
- `uv run uvicorn app.main:app --reload`
- Alternative: `uv run fastapi dev`

This will start the API server at the `http://localhost:8000/api/v1` and WebSockets at `ws://localhost:8000/ws/v1`


# Data Seeding
Data is seeded using `faker` and it is generated for: `User` data and for `Scores` to generate leaderboard results.

Seeding module is located at `app/seed`. Generated users are populated in `PostgreSQL` while scores are populated in `redis` with refrences to `user_id`.

## Running seed as a Module
- Using uv: `uv run python -m app.seed.main_seed`
- This will generate:
    - random users with random names, emails and a password fixed at: `123456`.
    - random scores in the range (100-1000) for the users previously generated within the last 6 months starting from current month over 10 games (To see which games are available in the system visit `app/redis/channels`)

# API
- Authentication (/auth):
    - POST `/login` Login to the system
        - Request: `{ email: "sample@domain.com", password: "password" }`
        - Response (200 Success): `{ success: true, statusCode: 200, message: ..., data: { id: 1, name: "James Brown", email: "sample@domain.com" }}`
        - Response (422 Unprocessable Entity)

    - GET `/me` Get current logged in user.
        - Response (200 Success): `{ success: true, statusCode: 200, message: ..., data: { id: 1, name: "James Brown", email: "sample@domain.com" }}`
        - Response (401 Unauthorized)

    - POST `/logout` logout endpoint
        - Response (200 Success): `{ success: true, statusCode: 200, message: ..., data: { id: 1, name: "James Brown", email: "sample@domain.com" }}`
    
    - Post `/signup` Signup to the system
        - Request: `{ email: "sample@domain.com", name: "James Brown", password: "password" }`
        - Response (200 Success): `{ success: true, statusCode: 200, message: ..., data: { id: 1, name: "James Brown", email: "sample@domain.com" }}`

- Games (/games):
    - GET `/` Get a list of all games:
        - Response (200 Success): `{ success: true, statusCode: 200, message: ..., data: [{ label: "Call of Duty", value: "cod"}, ...]}`

    
# Websocket Endpoints/Connections
- `/` Welcome Endpoint
    - Response (Text): `Welcome to your websocket server`

- `/my-score` Get the highest score for the current user in the leaderboard in realtime.
    - Response (JSON): `{"rank": 11, "user_id": 1, "player": "James Brown", "score": 200, "date": "2025-01-01" }

- `/add-score` Submit score for a particular game/channel
    - Response (None)

- `/scores` Return a paginated leaderboard in realtime
    - Request (JSON): `{ channel: "all", start: 0, end: 4 }`
    - Response (JSON): `{ "result": [{"rank": 1, "user_id": 1, "player": "Rick Grimes", "score": 250, "date": "2013-09-13" }, ...], "total_count": 50}`

- `/reports` Return top `N` players in a particular date range period
    - Request (JSON): `{"start": "ISODate", "end": "ISODate", "limit": 4}`
    - Response (JSON): `{ "result": [ { "name": "James Brown", "score": 400, "games": 4, "game": "Call of Duty", "date": "2025-03-32"} ]}`
