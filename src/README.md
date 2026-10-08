# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

Before signing in as a teacher, create a local teacher account from the workspace root:

```sh
python src/manage_teachers.py
```

The script prompts for a username and password and stores a salted PBKDF2 password hash in `src/teachers.json`. That file is git-ignored and should not be committed. Teacher sessions use random in-memory bearer tokens and end when the server restarts or the teacher logs out. Use HTTPS when exposing the app beyond local development.

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| POST   | `/api/login`                                                       | Sign in as a teacher and receive a session token                    |
| POST   | `/api/logout`                                                      | End the current teacher session                                     |

Activity signup and unregister endpoints require the session token in an `Authorization: Bearer <token>` header. Activity browsing and participant rosters remain public.

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
