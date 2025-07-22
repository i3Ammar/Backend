# Backend – Graduation Project 2 AFKAT

This repository contains the backend for the AFKAT Graduation Project 2. The backend is built using Python and Django, and it includes various modules to support authentication, game logic, home functionality, art assets, and more.

this is the [Front End](https://github.com/OmarAlbader/AFKAT-Frontend)

## Table of Contents

- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Project Modules](#project-modules)
- [Contributing](#contributing)
- [License](#license)

## Project Structure

The repository is organized as follows:

- `afkat/` – Main Django project folder.
- `afkat_auth/` – Handles authentication and user management.
- `afkat_game/` – Contains the game logic and related APIs.
- `afkat_home/` – Home/dashboard related logic.
- `afkat_art/` – Art assets or related backend logic.
- `templates/` – Django HTML templates.
- `requirements.txt` – Python dependencies.
- `manage.py` – Django management script.
- `Procfile` – Process file for deployment (e.g., Heroku).
- `TODO.md` – Project task list.
- `integration_testing_guide.md` – Guide for integration testing.

## Tech Stack

- **Language:** Python
- **Framework:** Django 5.2
- **REST API:** Django REST Framework
- **Authentication:** dj-rest-auth, django-allauth
- **Task Queue:** Celery, Redis
- **Database:** (Configured in Django settings, e.g., PostgreSQL)
- **Other:** CORS, S3 storage, JWT authentication, and more

See [`requirements.txt`](https://github.com/Graduation-Project-2-AFKAT/Backend/blob/main/requirements.txt) for a detailed list of dependencies.

## Setup & Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/Graduation-Project-2-AFKAT/Backend.git
   cd Backend
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in required values (database URL, secret key, etc.).
   - Alternatively, configure via `django-environ`.

5. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```

6. **Create a superuser (admin):**
   ```sh
   python manage.py createsuperuser
   ```

## Running the Application

To start the development server:
```sh
python manage.py runserver
```

For production, use the provided `Procfile` (e.g., with Heroku or Gunicorn):
```sh
gunicorn afkat.wsgi:application
```

## Testing

- See `integration_testing_guide.md` for integration test procedures.
- To run tests:
  ```sh
  pytest
  ```

## Project Modules

- `afkat_auth/` – Authentication, registration, JWT support
- `afkat_game/` – Game logic APIs
- `afkat_home/` – Home/dashboard APIs
- `afkat_art/` – Art-related backend logic
- `templates/` – HTML templates for the Django app

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Create a new Pull Request.

## License

This project is for educational purposes. Contact the repository owner for licensing information.

---

**Note:**  
- This README is based on partial directory and file information. [View the full repo contents here.](https://github.com/Graduation-Project-2-AFKAT/Backend/tree/main)
- For specific setup, configuration, or deployment questions, please refer to the project maintainers or check the provided documentation files.
