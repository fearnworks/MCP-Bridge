FROM python:3.12-bullseye

# install uv to run stdio clients (uvx)
RUN pip install --no-cache-dir uv

# install npx to run stdio clients (npx)
RUN apt-get update && apt-get install -y --no-install-recommends curl
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y --no-install-recommends nodejs

# Install Docker CLI (simplified)
RUN apt-get update && apt-get install -y docker.io \
    && rm -rf /var/lib/apt/lists/*

# Set Docker Host globally in container
ENV DOCKER_HOST=tcp://socket-proxy:2375

COPY pyproject.toml .
RUN uv sync

COPY mcp_bridge mcp_bridge

EXPOSE 8000

WORKDIR /mcp_bridge
ENTRYPOINT ["uv", "run", "main.py"]
