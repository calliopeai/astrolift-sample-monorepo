FROM python:3.12-alpine
WORKDIR /app
COPY apps/api/server.py ./server.py
USER 10001:10001
ENV PORT=8080
EXPOSE 8080
CMD ["python", "server.py"]
