# Money Movement APP
setup a database and tables in mysql

auth for the users table with fields name email and password.
after this run ./static/db.sql in your sql workbench.
then, 

app has 3 tables in database money, request, and auth.

Update your Database configuration setting in config.py file.

app has sessions and money movement operations.

# app runs on 127.0.0.1:5000

First run 
pip install -r requirements.txt from the app's directory in CMD.
and then run python app.py
 
use emails those are registered on the app i.e. the mail used for signup should be used for transactions.
only those emails will work otherwise you will not be able to perform operations.
* assuming you've python installed in your system 
 also it has a procfile for heroku deployment.