# References
See these [prisma python documentation](https://prisma-client-py.readthedocs.io/en/stable/) for all your ORM needs.
I encourage you to read up on this, and the [original/typescript prisma documentation](https://www.prisma.io/docs) to get a feel on
how to mess around with the schema and write the python code to interface with a database.
Referring to pre-existing code (e.g. `/register` route) will also be a great reference point!

# Setup
## Python Side
**Requirement:** Your running python version must be at least version 3.10!
For local development, create a virtual environment (venv) by following this handy [documentation](https://docs.python.org/3/library/venv.html)
replacing `/path/to/new/virtual/environment` with `.venv`, making sure you're in
the `backend` directory as you do this.

When you've loaded up the venv, run `pip3 install -r requirements.txt` to
load up all pre-existing modules to your venv.
For future reference, if you install any additional modules in the future
in the venv, you can run `pip3 freeze > requirements.txt` whilst you're
in the `backend` directory to add new modules for others to install in the future.
Run `deactivate` to exit the venv and leave your installed modules behind~
Whenever you work on the backend in the future, you should be loaded up in this
venv. There won't really be much in the way of reprecussions if you don't, other
than nothing working and random python files bloating your file system.

You'll also need to generate a secret key to put inside a `.env` file (that you can create yourself) 
in the `backend` directory. Just generate via the repl or google a solution 
and assign it to the `SECRET_KEY` variable in `.env`.

Now you're essentially ready to go... except for all the prisma/database
setup you need to do.

## Prisma/Database setup
Given the obvious fact that every query you run to the database affects it, 
it'll be best that you setup your own 'local' PostgreSQL server so you don't 
screw with some other developer's tables/data while you're prototyping something.

Luckily, this is super easy with [railway](https://railway.app/), follow
the first couple steps [here](https://dev.to/ngoakor12/connect-a-railway-databasepostgresql-with-node-postgres-in-express-15lf) to setup the database,
and you're already halfway done! Now, the quick and dirty solution, is to copy 
the `DATABASE_URL` environment variable as you saw in the aforementioned tutorial to 
the `.env` file in the `backend` directory. Run `prisma db push` and now, 
every time you add to the database through prisma in python code or delete, 
it will be reflected in the database (which you can view in a nice GUI all in railway).

If you want a more integrated way of interacting with the database with all of
railway's fancy toolkit + a method to deploy your local version of the backend contact @K0FFE1NE about it.

## Working with the database
For any subsequent changes to the schema, you should run `prisma db push` if 
you're prototyping changes and nothing is concrete yet. If you're confident that 
a change you're making is important and you want to upload it to version control, 
run `prisma migrate dev`. If you want to know why, read this [documentation](https://www.prisma.io/docs/guides/migrate/prototyping-schema-db-push).
