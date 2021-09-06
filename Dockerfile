
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
COPY ./requirements.txt /app/requirements.txt
# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
RUN pip install -r requirements.txt
COPY . /app

# Install production dependencies.
RUN pip install uvicorn

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec uvicorn --bind 0.0.0.0:8000 --workers 2 --threads 8 --timeout 0 run:app
