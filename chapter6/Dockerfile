# Dockerfile for Chapter 6
# Start with the slim parent image
FROM python:3.10-slim

#  set the Docker working directory
WORKDIR /code

# copy the build context directory to the Docker working directory
COPY requirements.txt /code/

# install dependencies
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

# copy the code files and database from the build context directory
COPY *.py /code/
COPY *.db /code/

# launch the uvicorn web server and run the Application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]