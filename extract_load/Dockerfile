FROM python:3.10-slim
WORKDIR /app

COPY extract_load /app
COPY common /app/common

RUN pip install --no-cache-dir -r requirements.txt -r common/requirements.txt

CMD ["python", "gdp_extraction.py"]
