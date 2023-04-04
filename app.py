from flask import Flask, redirect, url_for,request, render_template,flash
import mysql.connector


app = Flask(__name__)
app.config['SECRET_KEY'] = ''


# Initialize the Flask-MySQL extension

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="pass",
  database="pract_database"
)

# Connect to the MySQL database



@app.route("/", methods = ['GET',"POST"])
@app.route("/index", methods = ['GET',"POST"])
def home():  
    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM pract_database.tbl_users')
    data = cursor.fetchall()
    cursor.close()
    return render_template('/index.html',form=str(data))

@app.route("/login")
def login():
     return render_template('/login.html')

@app.route("/cart")
def cart():
     return render_template('/cart.html')
   
@app.route("/successful", methods = ['GET',"POST"])
def successful():
    return render_template('/successful.html')
  
@app.route("/about", methods = ['GET',"POST"])
def about():
    return render_template('/about.html')

@app.route("/contact", methods = ['GET',"POST"])
def contact():
    return render_template('/contact.html')

if __name__ == "__main__":
    app.run(debug=True)