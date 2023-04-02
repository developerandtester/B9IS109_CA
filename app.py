from flask import Flask, redirect, url_for,request, render_template,flash
from flask_mysqldb import MySQL
from config import Config


app = Flask(__name__)
app.config['SECRET_KEY'] = ''
app.config.from_object(Config)

# Initialize the Flask-MySQL extension
mysql = MySQL(app)

# Connect to the MySQL database



@app.route("/", methods = ['GET',"POST"])
@app.route("/index", methods = ['GET',"POST"])
def home():  
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM pract_database.tbl_users')
    data = cursor.fetchall()
    cursor.close()
    return render_template('/index.html',form=str(data))

@app.route("/login")
def login():
     return render_template('/login.html')



if __name__ == "__main__":
    app.run(debug=True)