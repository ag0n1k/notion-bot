FROM python:3.8-slim

# ENV TELEGRAM_TOKEN
# ENV NOTION_TOKEN

WORKDIR /source

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

ADD notion-py.tar.gz .
RUN python setup.py install

COPY . .

CMD [ "python", "source/main.py" ]
