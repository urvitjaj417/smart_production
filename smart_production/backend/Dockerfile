FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Train the ML model at build time so it's ready on first boot.
# (Safe no-op if you'd rather train against real DB data post-deploy.)
RUN python -m app.ml.train_model

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
