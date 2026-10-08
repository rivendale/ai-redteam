FROM python:3.12-slim
COPY app/ /srv/app/
COPY dev/ /srv/dev/
EXPOSE 8080
CMD ["python", "/srv/dev/dev_server.py"]
