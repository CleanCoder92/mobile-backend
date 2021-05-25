# Back-end for Tatiana's Review

# from Roland.


Create an [isolated Python environment][1], into which we will install the project's dependencies. This is highly recommended so that the requirements of this project don't interfere with any other Python environments you may have in your system, including the global Python environment. We also recommend that you create a new environment outside of the project directory.
```
python3 -m venv <path_to_venv_dir>
source <path_to_venv_dir>/bin/activate
pip install -r requirements.txt
```
Create the database. By default, an SQLite database will be created.
```
python manage.py migrate
```
Migration Command
```
python manage.py makemigrations
```

Run Server

```
python manage.py runserver
```
