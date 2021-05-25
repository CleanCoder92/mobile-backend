web: gunicorn Clout9.wsgi --chdir backend --limit-request-line 8188 --log-file -
worker: celery worker --workdir backend --app=Clout9 --loglevel=info
