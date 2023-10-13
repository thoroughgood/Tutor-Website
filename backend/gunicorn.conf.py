bind = "127.0.0.1:8000"
wsgi_app = "wsgi:app"
workers = 4
threads = 2
worker_class = "gthread"

# https://docs.gunicorn.org/en/stable/settings.html#daemon
# daemon = True

# debug options
# https://docs.gunicorn.org/en/stable/settings.html#loglevel
loglevel = "debug"
# https://docs.gunicorn.org/en/stable/settings.html#reload
reload = True
