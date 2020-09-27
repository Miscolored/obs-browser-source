FROM python:alpine

RUN pip install flask flask_socketio

COPY src /src/
COPY config /config/

EXPOSE 5000

ENV FLASK_ENV development

ENTRYPOINT ["python", "/src/app.py"]