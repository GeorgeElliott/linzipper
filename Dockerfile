FROM python:3.12-alpine

# Install zip utilities
RUN apk add --no-cache zip bash

WORKDIR /app

# Copy the requirements/files from your local 'web' folder 
# into the container's current working directory (.)
COPY web/ .

RUN pip install flask

EXPOSE 5000

# Now 'app.py' is directly inside the container's /app/ folder
CMD ["python", "app.py"]