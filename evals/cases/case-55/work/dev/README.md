# Developer console
Run `python dev_server.py` on your own machine; it listens on 127.0.0.1 only, uses the default password `dev`, has debug on and no TLS.
It is for local development: the Dockerfile builds the production app from `app/` only, and `.dockerignore` excludes `dev/`.
