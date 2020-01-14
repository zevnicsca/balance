
# Introduction
As a social payment tracking application, Balance is designed to be used by multiple people simultaneously to track expenses and payments over short or long term periods of time. For example, blockmates and or roommates who have expenses that are shared evenly between members of the group, or groups of friends that get together socially and want to keep track of who pays for what (say, Rob paid for lunch for a group of 4 friends on Monday and Annie paid for dinner within the same group of friends on Friday). Individuals can use Balance to tally expenses as they occur and to adjust totals as payments are made or IOUs are shifted according to who has contributed to ongoing tallies and what expenses have accrued.

This project was built and tested on the CS50 IDE and these instructions are made for that environment. However, it should be possible to also run on any similar environment.

# Setup
This project makes use of the Flask, Flask-Session, and Werkzeug libraries for Python. All of these are installed by default on the CS50 IDE and therefore do not need to be manually installed.  However, this project uses MongoDB in addition, which is not included by default and does need to be installed. Instructions for installing and starting MongoDB can be found [here](https://docs.c9.io/docs/setup-a-database#mongodb) – note it is only necessary that you complete up until the step where you start Mongo. In addition, this project makes use of [PyMongo](https://github.com/mongodb/mongo-python-driver/) –  the official Python driver for MongoDB for interactions between the server side code and the database. It can be installed using `pip` via `pip install pymongo`.

# Startup
First make sure that there is a running instance of primary daemon process for the MongoDB system. If you just completed the installation instructions, then you should have started one in the last step. If the process is not currently running it can be started (as long as MongoDB is installed) with the Terminal command `mongod`. Next, change directory into the directory that contains `application.py` and run the web application with the Terminal command `flask run`.  The output should include something along the lines of `* Running on https://ide50-yourCS50username.cs50.io:8080/ (Press CTRL+C to quit)`. Visiting that url should bring you to the running web application.

# Testing Ideas
Since Balance is a social payment application, for testing I would recommend creating several accounts so that you can try out the features. Then from the homepages of different accounts you can try creating groups with different combinations of these users. Once you have a few groups you can add expenses to them and view the updated balances on the user homepages.
