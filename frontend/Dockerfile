FROM python:3.14.0-slim


ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt ./

RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --shell /bin/bash appuser

COPY . /app
RUN chown -R appuser:appuser /app

USER appuser

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request,sys; r = urllib.request.urlopen('http://localhost:8501/health'); sys.exit(0 if r.status == 200 else 1)"]

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]