from flask import Flask, redirect, url_for,request, render_template,flash,jsonify,session
import mysql.connector
import hashlib
from flask_httpauth import HTTPBasicAuth
import pandas as pd
import json
import http.client
from datetime import datetime

auth = HTTPBasicAuth()



app = Flask(__name__)
app.config['SECRET_KEY'] = 'myWebCA'


# Initialize the Flask-MySQL extension

mydb = mysql.connector.connect(
  host="eu-cdbr-west-03.cleardb.net",
  user="bd5b45754d9419",
  password="cfd3aeb8",
  database="heroku_f7fc2d46da75047"
)


@app.route("/", methods = ['GET',"POST"])
@app.route("/index", methods = ['GET',"POST"])
def home():
    if('is_logged_in' not in session):
        session['is_logged_in']=False
    else:
        session['is_logged_in']=session['is_logged_in']
    if('cart' not in session):
        session['cart']=pd.DataFrame(columns=['item','qty','itemName','price','amount']).to_json()    
    else:
        session['cart']=session['cart']
    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM pract_database.tbl_users')
    data = cursor.fetchall()
    cursor.close()
    return render_template('/index.html',form=str(data),cart=session['cart'],is_logged_in=session['is_logged_in'])

@app.route("/login",methods = ['GET',"POST"])
def login():
     return render_template('/login.html',form='')
 
@app.route("/logout",methods = ['GET',"POST"])
def logout():    
    session.clear()
    session['is_logged_in']=False
    return redirect(url_for('home'))

@app.route("/getAddrFromEIRCode",methods = ['GET',"POST"])
def getAddrFromEIRCode():    
    freeformaddress=''
    if request.method == 'POST':
        input = request.get_json()
        EIR= input['eircode']         
        conn = http.client.HTTPSConnection("api.tomtom.com")
        payload = ''
        headers = {}        
        conn.request("GET", "/search/2/search/"+EIR+".json?key=jsDTi8Erj86YCGzh3dLkRcGh20W0d1oM&limit=1&countrySet=IE&idxSet=Str", payload, headers)
        res = conn.getresponse()
        print('2')        
        data = res.read()        
        res_dict = json.loads(data.decode("utf-8"))
        freeformaddress = res_dict['results'][0]['address']['freeformAddress']
        print(freeformaddress)
    return jsonify({'Result': freeformaddress})
 
def check_sql_injection(text):
    keywords = ['select', 'insert', 'update', 'delete', 'drop', 'alter', 'create', 'rename', 'truncate']
    for keyword in keywords:
        if keyword in text.lower():
            return True
    return False

# check for user existence
def check_user_existence(username):
    cursor = mydb.cursor()
    query = "SELECT * FROM tbl_users WHERE userName = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    if user is not None:
        return True
    return False

# insert user data into the database
def insert_user_data(data):
    cursor = mydb.cursor()
    query = "INSERT INTO tbl_users (userPass, userFirstName, userLastName, userName, userDefaultAddr, userPhone, userAccess,userEIRcode) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"
    cursor.execute(query, (data['userPass'], data['userFirstName'], data['userLastName'], data['userName'], data['userDefaultAddr'], data['userPhone'], 2,data['userEirCode']))
    mydb.commit()

# Flask route to handle the signup form
@app.route('/signup', methods=['GET', 'POST'])
def signup():    
   return render_template('signup.html')

@app.route("/addUser", methods=['GET','POST'])
def addUser():
    if request.method == 'POST':
        # get form data
        input = request.get_json()
        userPass = input['userPass']
        userFirstName = input['userFirstName']
        userLastName = input['userLastName']
        userName = input['userName']
        userDefaultAddr = input['userDefaultAddr']
        userPhone = input['userPhone']
        userEirCode=input['eircode']
        
        userPass=str(hashlib.md5(userPass.encode("utf-8")).hexdigest())
        # check for SQL injection
        if check_sql_injection(userPass) or check_sql_injection(userFirstName) or check_sql_injection(userLastName) or check_sql_injection(userName) or check_sql_injection(userDefaultAddr) or check_sql_injection(userPhone):
            return jsonify({'Result':'Error: SQL injection detected!'})
        
        # check for user existence
        if check_user_existence(userName):

            return jsonify({'Result': 'User already exists!'})
        
        # insert user data into the database
        data = {
            'userPass': userPass,
            'userFirstName': userFirstName,
            'userLastName': userLastName,
            'userName': userName,
            'userDefaultAddr': userDefaultAddr,
            'userPhone': userPhone,
            'userEirCode':userEirCode
        }
        insert_user_data(data)
        session['is_logged_in'] = True
        session['userPass'] = userPass
        session['userFirstName'] = userFirstName
        session['userLastName'] = userLastName
        session['userName'] = userName
        session['userDefaultAddr'] = userDefaultAddr
        session['userPhone'] = userPhone
        session['userEirCode'] = userEirCode
        return jsonify({'Result': 'User added successfully!'})
 
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
            session['userID']=data2[0][0]
            session['userFirstName'] = data2[0][2]
            session['userLastName'] = data2[0][3]
            session['userName'] = data2[0][4]
            session['userDefaultAddr'] = data2[0][5]
            session['userPhone'] = data2[0][6]
            session['userEirCode'] = data2[0][8]
            session['user'] = str(data2[0][3])
            session['is_logged_in'] = True
            session['useraccess'] = data2[0][7]
            return jsonify({'Result': '1'})
        return jsonify({'error' : 'Missing data!'})
    
@app.route("/addToCart", methods = ['GET',"POST"])
def addToCart():
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        item = int(data['id'])
        itemName = (data['name'])
        qty = int(data['qty'])        
        dataCart=pd.read_json(session['cart'])
        itemsJson = pd.read_json('Static\json\menuDetails.json')
        price=float(itemsJson[itemsJson['id'] == item]['Value'])
        amount=float(price*qty)
        data2=[[item,qty,itemName,price,amount]]
        df=pd.DataFrame(dataCart,columns=['item','qty','itemName','price','amount'])        
        #print(df)
        if(df.empty):
            df=pd.DataFrame(data2,columns=['item','qty','itemName','price','amount'])
            session['cart'] = df.to_json()                        
        else:
            if((item in df['item'].unique())==True):
                new_qty=int(df[df['item'] == item]['qty'])+qty
                new_amount=float(price*new_qty)
                df.loc[df['item'] == item, 'qty'] = new_qty
                df.loc[df['item'] == item, 'amount'] = new_amount
                df_new=df[df['item'] == item]
                print((int(df_new['qty'])))
                session['cart'] = df.to_json()        
            else:
                df_new=pd.DataFrame(data2,columns=['item','qty','itemName','price','amount'])
                df=pd.concat([df,df_new],ignore_index=True)
                print(df)
                session['cart'] = df.to_json()
        return jsonify({'Result': '1'})
    
    
@app.route('/update_cart', methods=['POST'])
def update_cart():
    data = request.get_json()
    item_id = int(data['id'])
    new_qty = int(data['new_qty'])
    
    dataCart = pd.read_json(session['cart'])
    
    # Check if item is in the cart
    if item_id in dataCart['item'].unique():
        # Update quantity and amount for the item
        dataCart.loc[dataCart['item'] == item_id, 'qty'] += new_qty
        
        # Check if new quantity is 0 and remove item from cart
        if dataCart.loc[dataCart['item'] == item_id, 'qty'].values[0] == 0:
            dataCart = dataCart[dataCart['item'] != item_id]        
        session['cart'] = dataCart.to_json()
        return jsonify({'Result': '1'})
    else:
        # Item not found in the cart
        return jsonify({'Result': '0'})


@app.route("/cart")
def cart():
    return render_template('/cart.html',cart=pd.read_json(session['cart']))

@app.route("/checkout", methods = ['GET',"POST"])
def checkout():
    if(session['is_logged_in'] == False):
        return redirect(url_for('login'))
    elif('is_logged_in' not in session):
        return redirect(url_for('login'))
    else:
        print(session['cart'])
        return render_template('/checkout.html',cart=pd.read_json(session['cart']))
   
@app.route("/successful", methods = ['GET',"POST"])
def successful():
    return render_template('/successful.html')
  
@app.route("/about", methods = ['GET',"POST"])
def about():
    return render_template('/about.html')

@app.route("/contact", methods = ['GET',"POST"])
def contact():
    return render_template('/contact.html')

@app.route("/order", methods = ['GET',"POST"])
def order():
    if(request.method == 'POST'):
        
             
        orderDate = datetime.now().strftime('%Y-%m-%d')
        orderTime = datetime.now().strftime('%H:%M:%S')        
        customer_id=session['userID']
        dataCart = pd.read_json(session['cart'])
        df = pd.DataFrame(dataCart, columns=['item', 'qty', 'itemName', 'price', 'amount'])
        session

    # Calculate order value
        orderValue = df['amount'].sum() 
        mycursor = mydb.cursor()
        sql = "INSERT INTO tbl_orders (customerID, addressID, orderValue, orderDate, orderTime,orderStatus) VALUES (%s, %s, %s, %s, %s,%s)"
        val = (customer_id, '0', orderValue, orderDate, orderTime,'New')
        mycursor.execute(sql, val)
        order_id = mycursor.lastrowid
        mydb.commit()
    
        for index, row in df.iterrows():
            cursor = mydb.cursor()
            sql = """INSERT INTO tbl_orderdetails
                    (orderID, productID, productQuantity, productPrice)
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (order_id, row['item'], row['qty'], row['price']))
            mydb.commit()
        return jsonify({'Result': '1'})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Get the order ID and status from the form
        order_id = request.form.get('order_id')
        status = request.form.get('status')
        
        # Update the order status in the database
        cursor = mydb.cursor()
        query = "UPDATE tbl_orders SET orderStatus = %s WHERE ordersID = %s"
        values = (status, order_id)
        cursor.execute(query, values)
        mydb.commit()
        
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_orders")
    orders = cursor.fetchall()
    for order in orders:
        cursor.execute("SELECT * FROM tbl_orderdetails WHERE orderID = %s", (order['ordersID'],))
        order['details'] = cursor.fetchall()
    
    # Render the admin template with the orders and order details
    return render_template('admin.html', orders=orders)


if __name__ == "__main__":
    app.run(debug=True)