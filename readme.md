
# Project Title
MutaEngine Test Assignment

## Getting Started

Follow these steps to set up the project on your local machine for development and testing purposes.

### 1. Clone the Project

First, clone the repository to your local machine:

```bash
git clone https://github.com/your-username/your-project.githttps://github.com/Faizan82001/mutaengine.git
cd mutaengine
```

### 2. Create and Activate Virtual Environment (Optional but Recommended)

It's recommended to use a virtual environment to isolate dependencies:

```bash
# On Linux/MacOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

After setting up the environment, install the required dependencies:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create an `.env` file in the root directory of your project and add the environment variables mentioned in `.env-template` file.

### 5. Run Migrations

Apply database migrations:

```bash
python manage.py migrate
```

### 6. Create a Superuser (Admin Account)

Create an admin account:

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

Run the Django development server:

```bash
python manage.py runserver
```

Now the project should be running at `http://127.0.0.1:8000/`.

---

