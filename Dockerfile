FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md PREREGISTRATION.md ./
COPY src ./src
RUN pip install --no-cache-dir .
ENV KM_DATA_DIR=/data \
    KM_REPORTS_DIR=/reports \
    KM_PREREG_PATH=/app/PREREGISTRATION.md \
    PYTHONUNBUFFERED=1
CMD ["kmaker", "paper"]
