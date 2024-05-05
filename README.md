# Chat app

An application where users can participate in conversations under different topics. A user may start a new conversation or comment on an already made one. Features of the app include:

* Users can log in and log out or sign up by creating a new account.
* A user can change their username or delete their account in user settings.
* A user is either an admin or a basic user.
* A user can start a new thread under a topic.
* Users can reply to a thread or to another reply in a thread.
* Users can delete their threads and replies or replies of other users written to their threads.
* Admins can add or remove topics and remove any thread or reply.
* Threads can be searched by using a search bar.
* Users can pin and unpin threads.
* Threads can be ordered by date and how many messages are in the thread in total. Additionally, when viewing pinned threads, there are options to order by in which order the threads were pinned.
* Replies can be ordered by date or how many replies they have.
* A specific amount of threads or replies is loaded to the page initially. If there are any left, more can be loaded with a link located at the bottom of the page.

To test admin role, register with the username testAdmin.

How to use the application locally:

Clone this repository to your computer and move to its root directory. Create a .env-file and specify its contents as follows:
* DATABASE_URL=local-address-of-the-database
* SECRET_KEY=secret-key

Activate the virtual environment and install the applications dependencies with the commands
* python3 -m venv venv
* source venv/bin/activate
* pip install -r ./requirements.txt

To define the schema of the database use the command
* psql < schema.sql

Now you should be able to run the application with the command
* flask run