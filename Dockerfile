# Build the frontend
FROM node:22-bookworm-slim AS build-frontend

WORKDIR /src

# Copy required source files
COPY *.json .
COPY *.js .
COPY src/frontend ./src/frontend

# Install deterministic frontend dependencies, excluding Electron tooling
RUN npm ci --omit=dev && \
  npm run build-frontend

# Main app build
FROM python:3.11-bookworm

WORKDIR /app

# Install Python deps
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy prebuilt frontend
COPY --from=build-frontend /src/public public

# Copy other required source files
COPY *.py .
COPY src/__init__.py ./src/__init__.py
COPY src/backend ./src/backend
COPY *.json .

CMD ["python", "crosstalk.py", "--host=0.0.0.0", "--reticulum-config-dir=/config/.reticulum", "--storage-dir=/config/.crosstalk", "--headless"]
