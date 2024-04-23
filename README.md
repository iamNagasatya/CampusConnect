# Student Priority Manager 
Application which helps students  to stay informed, organized, and productive

## SOFTWARE INSTALLATION

**Step 1: Install “Python”**

1. Go to the official Python download page for Windows.

2. Find a stable Python 3 release version 3.9.

3. Click the appropriate link for your system to download the executable file: Windows installer (64-bit) or Windows installer (32-bit).

4. After the installer is downloaded, double-click the .exe file, for example 
python-3.9.18-amd64.exe, to run the Python installer.

5. Select the Install launcher for all user’s checkbox, which enables all users of 
the computer to access the Python launcher application.

6. Select the Add python.exe to PATH checkbox, which enables users to launch 
Python from the command line.

7. Click Next.

8. Click Install to start the installation.

9. After the installation is complete, a Setup was successful message displays.

10. Enter the python --version command in the command prompt to verify the 
installation.

**Step 2: Install “PostgreSQL”**

1. Download Postgres Installer. Postgres Installer is available for PostgreSQL for various versions download version 16.

2. Click on the executable file to run the installer.

3. Select your preferred language.

4. Specify directory where you want to install PostgreSQL.

5. Specify PostgreSQL server port. You can leave this as default if you’re unsure 
what to enter.

6. Specify data directory to initialize PostgreSQL database.

7. Create a PostgreSQL user password.

8. Create password for database Superuser.

9. Click next to begin PostgreSQL installation.

10. Close the installation window after completion.

**Step 3: Create Virtual Environment**

Go the project directory create the virtual environment using by running “python -m 
venv env_name” 

**Step 4: Install “Python Libraries using pip specified in requirements.txt”**

1. Go to the project directory and activate the environment by running source 
env_name/Scripts/activate for windows and source env_name/bin/activate for 
Linux.

2. And run the command pip install -r requirements.txt to install all the 
dependencies for the project


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
