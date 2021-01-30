# set base image (host OS)
FROM python:3.8

# ENV TELEGRAM_TOKEN
# ENV NOTION_TOKEN
# ENV AWS_ACCESS_KEY_ID
# ENV AWS_SECRET_ACCESS_KEY

WORKDIR /src


ADD notion-py.tar.gz .
RUN python setup.py install

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .

# command to run on container start
CMD [ "python", "./main.py" ]