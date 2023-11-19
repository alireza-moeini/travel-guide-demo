FROM python:3.10.4 AS dependencies

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY . .

CMD ["python", "app.py"]