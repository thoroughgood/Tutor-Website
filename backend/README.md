# References
See these [prisma python documentation](https://prisma-client-py.readthedocs.io/en/stable/) for all your ORM needs.
I encourage you to read up on this, and the [original/typescript prisma documentation](https://www.prisma.io/docs) to get a feel on
how to mess around with the schema and write the python code to interface with a database. 

For argument validation, see the original [javascript documentation](https://json-schema.org/learn/getting-started-step-by-step) and
the [python implementation documentation](https://python-jsonschema.readthedocs.io/en/stable/). Generally the original documentation is greatly
preferred, and there are only some minor items you may need to refer to for the python side of things. 
Especially, given that the original documentation's glossery also has notes on the python implementation
differences.

# Setup
## Python Side
**Requirement:** You must have some version of python3 on your system.

Then, you'll need to generate a secret key to put inside a `.env` file (that you can create yourself) 
in the `backend` directory. Just generate via the repl or google a solution 
and assign it to the `SECRET_KEY` variable in `.env`.

Then, simply run the `runBackend.sh` script in your terminal whilst you're in the backend directory,
Once you're actually setup, this will also run the server, however, for now it'll
crash at the end, however, most of the setup will be done automagically
for you before it does!

For the server to actually run, you'll need to some more setup.

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

## Pusher Setup
For messaging / notifications, you must setup a pusher service. Head to [pusher](https://pusher.com/), 
create an account if you don't have one already, and create a channel app. Call it whatever you
deem appropriate, and head to the app keys section of your new app. Add these app keys to your `.env` file
in this format:
```
PUSHER_APP_ID=app_id
PUSHER_KEY=key
PUSHER_SECRET=secret
PUSHER_CLUSTER=cluster
```

## Working with the database
For any subsequent changes to the schema, you should run `prisma db push` if 
you're prototyping changes and nothing is concrete yet. If you're confident that 
a change you're making is important and you want to upload it to version control, 
run `prisma migrate dev`. If you want to know why, read this [documentation](https://www.prisma.io/docs/guides/migrate/prototyping-schema-db-push).
