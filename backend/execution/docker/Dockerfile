FROM python:3.11-slim

# Enforce strict pip behavior:
#   - No cache files kept
#   - Disable version check for speed
#   - Disallow installing transitive dependencies (packages must be self‑contained)
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_DEPS=1

# Install any build tools needed for compiling wheels (optional, kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy optional constraints and requirements for image‑time installation
COPY constraints.txt /tmp/constraints.txt
COPY requirements.txt /tmp/requirements.txt

# Install packages listed in requirements.txt using constraints (if the file is non‑empty)
RUN if [ -s /tmp/requirements.txt ]; then \
        pip install --no-cache-dir -c /tmp/constraints.txt -r /tmp/requirements.txt; \
    fi

WORKDIR /workspace

# Default entrypoint runs pytest (can be overridden at runtime)
ENTRYPOINT ["pytest"]
