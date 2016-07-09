from flask import Flask, request, redirect, render_template, session, flash, Markup
from mysqlconnection import MySQLConnector
from time import strftime
import re, datetime
app = Flask(__name__)
app.secret_key = 'KeepItSecretKeepItSafe'
mysql = MySQLConnector(app, 'email_validation_with_db')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
noNumbers = re.compile(r'^[^0-9]+$')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/success', methods=['GET', 'POST'])
def success():
    if (len(request.form['email']) < 1) or (len(request.form['first_name']) < 1) or (len(request.form['last_name']) < 1):
        error = Markup('<div id="error"><h2>"You cannot leave a field blank."</h2></div>')
        return render_template('index.html', error=error)
    elif not (noNumbers.match(request.form['first_name'])) or (not noNumbers.match(request.form['last_name'])):
        error = Markup('<div id="error"><h2>"Names cannot conatin numbers"</h2></div>')
        return render_template('index.html', error=error)
    elif not EMAIL_REGEX.match(request.form['email']):
        error = Markup('<div id="error"><h2>"Email is not valid!"</h2></div>')
        return render_template('index.html', error=error)
    else:
        query = "INSERT INTO users (first_name, last_name, email, created_at) VALUES (:first_name, :last_name, :email, NOW())"
        data = {
                'first_name': request.form['first_name'], 
                'last_name': request.form['last_name'],
                'email': request.form['email']
               }
        mysql.query_db(query, data)
        query = "SELECT * FROM users"
        users = mysql.query_db(query)
        newuser = {
                'first_name': request.form['first_name'], 
                'last_name': request.form['last_name'],
                'email': request.form['email']
                }
        return render_template('success.html', all_users=users, newuser=newuser)

@app.route('/delete/<user_id>', methods=['GET', 'POST'])
def delete(user_id):
    query = "DELETE FROM users WHERE id = :id"
    data = {'id': user_id}
    mysql.query_db(query, data)
    flash("User " + user_id + " has been deleted from the database")
    return redirect('/users')

@app.route('/users', methods=['GET', 'POST'])
def users():
    query = "SELECT * FROM users"
    users = mysql.query_db(query)
    return render_template('success.html', all_users=users)


app.run(debug=True)