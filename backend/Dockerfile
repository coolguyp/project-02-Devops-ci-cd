FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /app

# Python best practices
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install runtime deps only (NO build tools needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
 && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Security: run as non-root
RUN useradd -m appuser
USER appuser

# Flask runs on 5000 by default
EXPOSE 5000

CMD ["python", "app.py"]



#FROM python:3.11-slim

#WORKDIR /app

# system deps for psycopg2
#RUN apt-get update && apt-get install -y \
#    gcc \
#    libpq-dev \
# && rm -rf /var/lib/apt/lists/*

#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt

#COPY . .

# make python see /app
#ENV PYTHONPATH=/app

#CMD ["python", "app.py"]
