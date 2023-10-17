# config file for gunicorn
# see https://docs.gunicorn.org/en/stable/settings.html for more

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
