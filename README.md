# capstone-project-3900m16athecarrothead

Setup
Python Setup

You'll need to generate a secret key to put inside a .env file (that you can create yourself) in the root of the backend directory. Generate a secret key using the python3 repl.

Example:
```
>>> import secrets
>>> secrets.token_urlsafe(16)
>>> 'zs9XYCbTPKvux46UJckflw'
>>> secrets.token_hex(16)
>>> '6bef18936ac12a9096e9fe7a8fe1f777'
```
And assign it to the SECRET_KEY variable in the .env in the backend directory.

Then, simply run the ./runBackend.sh script in your terminal whilst you're in the backend directory, Once you're actually setup, this will also run the server, however, for now it'll crash at the end, however, most of the setup will be done automagically for you before it does!

For the server to actually run, you'll need some more setup.
Prisma/Database setup

For dev work, setup your own 'local' PostgreSQL server so you don't screw with some other developer's tables/data while you're prototyping something.

This can be done easily via railway app, and you can follow the steps here to do it:
https://dev.to/ngoakor12/connect-a-railway-databasepostgresql-with-node-postgres-in-express-15lf

Otherwise, you set this up any other way, then assign the database’s url to DATABASE_URL environment variable in the .env file. Run prisma db push in your terminal again, the database will be updated with a new model, reflective of the already present prisma schema.
Pusher Setup

For messaging / notifications, you must set up a pusher service. Head to pusher, create an account if you don't have one already, and create a channel app. Call it whatever you deem appropriate, and head to the app keys section of your new app. Add these app keys to your .env file in this format:

```
PUSHER_APP_ID=app_id
PUSHER_KEY=key
PUSHER_SECRET=secret
PUSHER_CLUSTER=cluster
```

Working with the database
For any subsequent changes to the schema, you should run prisma db push if you're prototyping changes and nothing is concrete yet. If you're confident that a change you're making is important and you want to upload it to version control, run prisma migrate dev.
Running the server
Running ./runBackend in your terminal will boot the flask application with multiple workers as a web server through gunicorn using config settings in gunicorn.conf.py in the root of the backend directory. Otherwise, you can run the server by first activating the virtual environment by running source .venv/bin/activate whilst in the backend directory, then running python3 app.py in your terminal to run it in debug mode with a single worker. This is helpful for when working in a dev environment, and you need to debug or test code.
Frontend setup
Requirements
NodeJS
NPM
Environment Setup
To setup the frontend, the following environment variables are required
```
NEXT_PUBLIC_BACKEND_URL
NEXT_PUBLIC_PUSHER_KEY
NEXT_PUBLIC_PUSHER_CLUSTER
```
Installation
To use the frontend server, make ensure that all dependencies are installed using npm install in the frontend directory.

Running the server
To run the development server use npm run dev. To build and start a production instance of the server run npm run build followed by npm run start. Note that during the build process all files must be linted according to .eslintrc.json.

Deployed project
To view a deployed version of the project, visit https://mute-idea-production.up.railway.app/login
