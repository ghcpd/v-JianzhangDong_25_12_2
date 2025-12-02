FROM python:3.11-slim

WORKDIR /app

# copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /app/requirements.txt

# copy app sources
COPY . /app

CMD ["python", "app.py"]
