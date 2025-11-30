FROM python:3.10-slim

# Install potrace (needed for SVG vectorization)
#RUN apt-get update && apt-get install -y potrace

WORKDIR /app

#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use uvicorn to run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
