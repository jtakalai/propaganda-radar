# The writable site: radar/web.py serves web/ and the review API off one process.
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# The server only needs the store and the RSS fetch; sklearn stays out of the image.
RUN pip install --no-cache-dir pandas feedparser

COPY radar/ radar/
COPY web/ web/
# Baked in so the image runs without a volume; mount over it to keep the labels.
COPY data/processed/headlines.csv data/processed/

EXPOSE 8000
CMD ["python", "-m", "radar.web", "--host", "0.0.0.0"]
