# Student Priority Manager 
Application which helps students  to stay informed, organized, and productive




## STEPS FOR EXECUTING THE PROJECT

* Step 1: Switch to the project folder or directory in the visual code.

* Step 2: Open the terminal or command prompt in the vs code.

* Step 3: Create Django migrations using `python manage.py makemigrations`.

* Step 4: Push the Django migrations to the PostgreSQL database with `python 
manage.py migrate` command.

* Step 5: Create superuser for Django Administration by `python manage.py 
createsuperuser`, then fill username and password for the administrator 
account.

* Step 6: Collect static files of Django Application with `python manage.py 
collectstatic`.

* Step 7: Run the Django development server using `python manage.py 
runserver` command.

* Step 8: Open the new terminal or command prompt in the visual studio code.

* Step 9: Run celery my running `celery -A ProjectTime.celery worker -l info` in 
newly opened terminal.

* Step 10: Switch back to the first terminal and copy the URL of the website and 
open it in the browser.
