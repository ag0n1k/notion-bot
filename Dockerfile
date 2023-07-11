FROM python:3.11-slim

WORKDIR /source

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "nbot/main.py" ]
