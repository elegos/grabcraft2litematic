FROM python:3.12

RUN python -m ensurepip && \
  pip install --upgrade pip pipenv && \
  useradd -m -d /appdaemon appdaemon && \
  mkdir -p /appdaemon/db && \
  chown -R appdaemon:appdaemon /appdaemon

COPY --chown=appdaemon:appdaemon ./ /appdaemon/

USER appdaemon
WORKDIR "/appdaemon"

RUN pipenv install

ENTRYPOINT ["pipenv", "run", "uvicorn", "--host", "0.0.0.0", "srv:app"]

