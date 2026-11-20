# Two stages: install dependencies in a builder, ship only what the app needs.
# The final image has no pip/setuptools (they carry their own CVEs and are not
# needed at runtime) and takes the latest Debian security fixes.

FROM python:3.13-slim AS build
COPY requirements.txt .
RUN python -m venv /venv \
 && /venv/bin/pip install --no-cache-dir -r requirements.txt \
 && /venv/bin/pip uninstall -y pip

FROM python:3.13-slim
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/* \
 && python -m pip uninstall -y pip setuptools wheel 2>/dev/null; \
    rm -rf /usr/local/lib/python3.13/ensurepip
COPY --from=build /venv /venv
ENV PATH=/venv/bin:$PATH

WORKDIR /srv
COPY app/ app/

RUN useradd --uid 10001 --no-create-home appuser
USER 10001

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
