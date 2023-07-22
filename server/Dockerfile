# Build Flask
FROM python:3.9 as server

WORKDIR /

COPY .ENV ./

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5001

CMD ["sh", "-c", "export $(cat .ENV | xargs) && flask run --port 5001"]
