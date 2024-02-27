# pull official base image
FROM python:3.9.2-alpine

# set work directory
WORKDIR /home/app

# copy project
COPY . .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1


# install dependencies
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

# create the app user
RUN addgroup -S app && adduser -S app -G app

# chown all the files to the app user
RUN chown -R app:app .

# change to the app user
USER app

# run entrypoint.prod.sh
RUN ["chmod", "+x", "/home/app/entrypoint.sh"]
ENTRYPOINT ["/home/app/entrypoint.sh"]