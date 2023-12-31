
# Test Your Soft

Django project for bug tracking.

## Check it out

[Test Your Soft deployed to Render](https://testyoursoft.onrender.com)

To view the service on Render, use the following credentials or crate your own account:
```angular2html
username: testuser
password: 12testpass34
```
## Functional

* authorization using login and password;
* create projects for testing;
* creat test cases;
* combine test cases into test runs;
* integration of telegram bot for receiving notifications:
* review of statistics.

## Technologies Used

* Python and Django Framework for the backend
* HTML, CSS, and JavaScript for the frontend
* SQLite and Postgres databases for data storage

## Getting Started

### Prerequisites
* Python (version 3.6 or higher) and pip installed on your system
* Git (optional, for cloning the repository)

### Installation
1. Clone the repository:
```
git clone https://github.com/your-username/bug-tracker.git
```

2. Create a virtual environment (optional but recommended):
```
python -m venv env
source env/bin/activate      
# For Windows: env\Scripts\activate
```
3.  Edit the `.env` using the template `.env.sample`.

```
# True for development, False for production
DJANDO_DEBUG=True
```

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Run database migrations:
```
python manage.py migrate
```

6. Create a superuser to access the admin panel:
```
python manage.py createsuperuser
```

7. Start the development server:
```
python manage.py runserver
```

8. Open your web browser and navigate to http://localhost:8000/

## Shutdown
To stop running app in your terminal press:
```
ctrl + C
```
![img_1.png](img_1.png)
![img.png](img.png)

