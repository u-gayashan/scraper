FROM python:3.10-slim

WORKDIR /app


COPY main.py ./
COPY test.csv ./

RUN pip install --timeout=100 --retries=10 requests beautifulsoup4 pandas

CMD ["python", "main.py"]
