# Sandbox container for isolated Python code execution
# Minimal, non-root, no network access, limited resources
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 sandbox && \
    mkdir -p /sandbox && \
    chown -R sandbox:sandbox /sandbox

# Install minimal dependencies (math, json, re, statistics are stdlib)
RUN pip install --no-cache-dir numpy scipy pandas

# Switch to non-root user
USER sandbox
WORKDIR /sandbox

# Default: read code from stdin, write output to stdout
ENTRYPOINT ["python3"]
CMD ["-u", "-c", "import sys; exec(sys.stdin.read())"]
