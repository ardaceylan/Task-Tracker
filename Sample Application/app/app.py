import re  
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__) 

app.secret_key = 'abcdefgh'
  
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'cs353hw4db'
  
mysql = MySQL(app)  

@app.route('/')

@app.route('/login', methods =['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = % s AND password = % s', (username, password, ))
        user = cursor.fetchone()
        if user:              
            session['loggedin'] = True
            session['userid'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return  redirect(url_for('tasks'))
        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message = message)


@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            message = 'Choose a different username!'
  
        elif not username or not password or not email:
            message = 'Please fill out the form!'

        else:
            cursor.execute('INSERT INTO User (id, username, email, password) VALUES (NULL, % s, % s, % s)', (username, email, password,))
            mysql.connection.commit()
            message = 'User successfully created!'

    elif request.method == 'POST':

        message = 'Please fill all the fields!'
    return render_template('register.html', message = message)

@app.route('/analysis')
def analysis():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT title, TIMESTAMPDIFF(HOUR, done_time, deadline) AS latency FROM Task WHERE status = 'Done' AND user_id = %s AND done_time > deadline ORDER BY latency DESC", (session['userid'],))
    after_deadline_tasks = cursor.fetchall()
    cursor.execute("SELECT AVG(TIMESTAMPDIFF(HOUR, done_time, creation_time)) FROM Task WHERE status = 'Done' AND user_id = %s", (session['userid'],))
    avg_time = cursor.fetchone()

    cursor.execute("SELECT task_type, COUNT(*) as count FROM Task WHERE status = 'Done' AND user_id = %s GROUP BY task_type ORDER BY count DESC", (session['userid'],))
    type_counts = cursor.fetchall()

    cursor.execute("SELECT title, deadline FROM Task WHERE status != 'Done' AND user_id = %s ORDER BY deadline ASC", (session['userid'],))
    uncompleted_tasks = cursor.fetchall()

    cursor.execute("SELECT title, TIMESTAMPDIFF(HOUR, done_time, creation_time) AS done_time FROM Task WHERE status = 'Done' AND user_id = %s ORDER BY done_time DESC LIMIT 2", (session['userid'],))
    slowest_tasks = cursor.fetchall()



    return render_template('analysis.html', user_id=session['userid'], after_deadline_tasks=after_deadline_tasks, avg_time=avg_time, type_counts=type_counts, uncompleted_tasks=uncompleted_tasks, slowest_tasks=slowest_tasks)


@app.route('/taskdelete/<int:task_id>', methods=['GET', 'POST', 'DELETE', 'PUT'])
def taskdelete(task_id):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM Task WHERE id = %s", (task_id,))
    mysql.connection.commit()
    cursor.close()
    return  redirect(url_for('tasks', message='deletion!'))
    '''elif request.method == 'PUT':
        # Get the task data from the form
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        task_type = request.form['task_type']

        # Update the task in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE Task SET title = %s, description = %s, deadline = %s, task_type = %s WHERE id = %s",
                       (title, description, deadline, task_type, task_id))
        mysql.connection.commit()
        cursor.close()'''

@app.route('/taskdone/<int:task_id>', methods=['GET', 'POST', 'DELETE', 'PUT'])
def taskdone(task_id):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE Task SET status = 'Done' WHERE id = %s", (task_id,))
    mysql.connection.commit()
    cursor.close()
    return  redirect(url_for('tasks', message='done!'))


@app.route('/tasks', methods =['GET', 'POST', 'DELETE', 'PUT'])
def tasks():
    #To add a new task
    if request.method == 'POST':
        task_title = request.form['task_title']
        task_description = request.form['task_description']
        task_status = request.form['task_status']
        task_deadline = request.form['task_deadline']
        task_creation_time = request.form['task_creation_time']
        task_done_time = request.form['task_done_time']
        task_type = request.form['task_type']
        user_id = request.form['user_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO Task (title, description, status, deadline, creation_time, done_time, user_id, task_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (task_title, task_description, task_status, task_deadline, task_creation_time, task_done_time, user_id, task_type))
        mysql.connection.commit()
        cursor.close()

    ##To get the table data
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Task WHERE user_id=%s AND status ='Done' ORDER BY deadline ASC", (session['userid'],))##edit!!!!!!!
    tasks_done = cursor.fetchall()
    cursor.close()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Task WHERE user_id=%s AND status!='Done' ORDER BY done_time DESC", (session['userid'],))
    tasks_remaining = cursor.fetchall()
    cursor.close()
    return render_template('tasks.html', tasks_done = tasks_done, tasks_remaining = tasks_remaining )    


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
