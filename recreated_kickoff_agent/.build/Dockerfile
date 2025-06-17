
# Stage 1: Build the braid library
FROM python:3.11-slim as builder

WORKDIR /app

# Copy the entire braid library source
COPY ./braid_src /app/braid_src

# Install the braid library from the local source
RUN pip install --no-cache-dir ./braid_src

# Stage 2: Final application image
FROM python:3.11-slim

WORKDIR /app

# Copy the installed braid library from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copy the agent's requirements and code
COPY ./agent_code/requirements.txt .
COPY ./agent_code/ .

# Install the agent's dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add the app directory to the python path to allow local imports
ENV PYTHONPATH="/app"

# Debugging steps to verify container state
RUN echo "--- Debugging Info ---"
RUN echo "Listing contents of /app:" && ls -R /app
RUN echo "PYTHONPATH is set to: $PYTHONPATH"
RUN echo "--- End Debugging Info ---"

# Command to run the agent
CMD ["python", "agent.py"]
