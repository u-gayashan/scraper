FROM python:3.10-slim

WORKDIR /app


COPY main.py ./
COPY master.csv ./

RUN pip install --timeout=100 --retries=10 requests beautifulsoup4 pandas

# CMD ["python", "main.py"]
EXPOSE 8000
CMD ["sh", "-c", "python main.py && python -m http.server 8000"]