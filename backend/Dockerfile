FROM python:3.10-bullseye

WORKDIR /backend
COPY . .
RUN pip3 install -r requirements.txt
RUN python3 manage.py makemigrations users tags recipes
RUN python3 manage.py migrate
CMD ["gunicorn", "-b", "0.0.0.0:8000", "backend.wsgi:application", "-k", "gevent", "--worker-connections", "100", "--max-requests", "100", "--capture-output", "--access-logfile", "-", "--error-logfile", "-"]


