# Step 1: Use the official Python runtime as a base image
FROM python:3.9-slim

# Step 3: Set the working directory inside the container
WORKDIR /app

# Step 4: Copy the requirements.txt file into the container to install dependencies
COPY requirements.txt .

# Step 5: Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Copy the rest of the application code into the container
COPY . /app

# Step 7: Expose the port that FastAPI will use (default is 8000)
EXPOSE 8001

# Step 8: Run the FastAPI application with Uvicorn
CMD ["uvicorn", "user_management:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
