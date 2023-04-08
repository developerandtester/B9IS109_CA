from flask import Flask, redirect, url_for,request, render_template,flash,jsonify,session
import mysql.connector
import hashlib
from flask_httpauth import HTTPBasicAuth
import pandas as pd
auth = HTTPBasicAuth()



app = Flask(__name__)
app.config['SECRET_KEY'] = 'myWebCA'


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
    session['cart']=pd.DataFrame(columns=['item','qty']).to_json()
    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM pract_database.tbl_users')
    data = cursor.fetchall()
    cursor.close()
    return render_template('/index.html',form=str(data))

@app.route("/login",methods = ['GET',"POST"])
def login():
     return render_template('/login.html',form='')
 
@app.route("/verifyUser", methods = ['GET',"POST"])
def verifyUser():
    if request.method == 'POST':
        data = request.get_json()
        user = data['Username']
        password = data['Password']
        hashpassword = hashlib.md5(password.encode("utf-8")).hexdigest()
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM pract_database.tbl_users WHERE userName = %s AND userPass = %s', (user, str(hashpassword)))
        data2 = cursor.fetchall()
        cursor.close()                        
        if len(data2) > 0:
            session['user'] = str(data2[0])
            session['is_logged_in'] = True
            return jsonify({'Result': '1'})
        return jsonify({'error' : 'Missing data!'})
    
@app.route("/addToCart", methods = ['GET',"POST"])
def addToCart():
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        item = int(data['id'])
        qty = int(data['qty'])
        data2=[[item,qty]]
        dataCart=pd.read_json(session['cart'])
        df=pd.DataFrame(dataCart,columns=['item','qty'])
        #print(df)
        if(df.empty):
            df=pd.DataFrame(data2,columns=['item','qty'])
            session['cart'] = df.to_json()                        
        else:
            if((item in df['item'].unique())==True):
                new_qty=int(df[df['item'] == item]['qty'])+qty
                df.loc[df['item'] == item, 'qty'] = new_qty
                df_new=df[df['item'] == item]
                print((int(df_new['qty'])))
                session['cart'] = df.to_json()        
            else:
                df_new=pd.DataFrame(data2,columns=['item','qty'])
                df=pd.concat([df,df_new],ignore_index=True)
                print(df)
                session['cart'] = df.to_json()
        return jsonify({'Result': '1'})

@app.route("/cart")
def cart():    
     return render_template('/cart.html',cart=session['cart'])
   
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