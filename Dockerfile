# 1. Use the official lightweight Python 3.11 image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app



# 4. Copy ONLY the requirements file first.
# This is a Docker best practice! Docker caches layers. 
# If we change our code (src/) but not our requirements, Docker doesn't have to reinstall everything!
COPY requirements.txt .

# 5. Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code and the saved ML models
# (Note: .dockerignore will automatically prevent the 1.5GB data folder from being copied)
COPY src/ /app/src/
COPY models/ /app/models/

# 7. Expose the port that FastAPI runs on
EXPOSE 8000

# 8. Define the command to start the server
# We use uvicorn, set host to 0.0.0.0 (so it accepts traffic from outside the container), and port 8000.
CMD ["uvicorn", "src.fraudguard.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
