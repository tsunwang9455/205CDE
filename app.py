from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import *
from flask_uploads import *
from werkzeug.utils import secure_filename
import MySQLdb.cursors
import re

UPLOAD_FOLDER = '/static/image'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.secret_key = 'secret key'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'gordon'
app.config['MYSQL_PASSWORD'] = '123'
app.config['MYSQL_DB'] = 'gamefun'


mysql = MySQL(app)



class UpdateProductForm(Form):
    productName = StringField('', [validators.length(min=3, max=100)],
                            render_kw={'placeholder': 'Product Name'})
    productDetail = StringField('', [validators.length(min=3, max=500)],
                            render_kw={'placeholder': 'Detail'})
    productPrice = FloatField('', [validators.InputRequired()], 
                            render_kw={'placeholder': 'Price'})
    productCompany = StringField('', [validators.length(min=3, max=100)], 
                            render_kw={'placeholder': 'Product Company'})
    productPhoto = StringField('', [validators.length(min=3, max=100)], 
                            render_kw={'placeholder': 'Product Link'})

 


@app.route('/')
def index():
	return render_template('MainPage.html')


@app.route('/news')
def news():
	return render_template('news.html')

@app.route('/product')
def product():

	producttypea = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	gtype = 'PS4'
	producttypea.execute("SELECT * FROM Products WHERE productCompany = %s ORDER BY RAND()", (gtype,))
	PS4 = producttypea.fetchall()

	producttypeb = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	gtype = 'NS'
	producttypeb.execute("SELECT * FROM Products WHERE productCompany = %s ORDER BY RAND()", (gtype,))
	NS = producttypeb.fetchall()

    
	return render_template('product.html', PS4 =PS4, NS=NS)

@app.route('/productDetail', methods=["POST","GET"])
def proDetail():
    if 'productID' in request.args:
        productID = request.args['productID']
       
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Products WHERE productID = %s',(productID,))
        mysql.connection.commit()
        detail = cursor.fetchall()

        return render_template('proDetail.html', detail = detail)
    return render_template('proDetail.html')


@app.route('/order', methods=['POST',"GET"])
def order():
    if 'loggedin' in session:
        if 'productID' in request.args:
            productID = request.args['productID']
           
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM Products WHERE productID = %s',(productID,))
            mysql.connection.commit()
            detail = cursor.fetchall()

            return render_template('order.html', detail = detail)
        return render_template('order.html')
    else:
        flash('Please login your account')
        return render_template('Login.html')


@app.route('/confirmOrder',methods=["POST","GET"])
def confirmOrder():

    if request.method == 'POST' and 'orderName' in request.form and 'ProductID' in request.form and 'orderAddress' in request.form and 'orderPhone' in request.form:
                
        orderName = request.form['orderName']
        ProductID = request.form['ProductID']
        orderAddress = request.form['orderAddress']
        orderPhone = request.form['orderPhone']
        orderEmail = request.form['orderEmail']
                
                        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)         
        submit = cursor.execute('INSERT INTO orderlist VALUES (NULL, %s, %s,%s, %s, %s)', (orderName,ProductID,orderAddress,orderPhone, orderEmail))
        mysql.connection.commit()
                
        if submit:
            flash('Order Submitted', 'success')
            return render_template('MainPage.html', submit = submit  )
                    
        else:
            flash('Order Not Submit', 'danger') 
            return render_template('order.html', submit = submit )

    return render_template('confirmOrder.html')
                
            
        
               
        
     

@app.route("/vieworder" , methods=['GET', 'POST'])
def viewallorder():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM orderlist ")
    viewallorder = cursor.fetchall()
    return render_template ('vieworder.html' ,viewallorder = viewallorder)

@app.route("/deleteorder" , methods=['GET', 'POST'])
def deleteproduct():
    if 'orderID' in request.args:
        orderID = request.args['orderID']
        cursor = mysql.connection.cursor()
        deleted = cursor.execute("DELETE FROM orderlist where orderID=%s", (orderID,))
        mysql.connection.commit()
        if  deleted:
            flash('Order has been deleted')
            return render_template('vieworder.html')
            
    return redirect(url_for('vieworder.html'))


    

@app.route('/CustomerService', methods=['GET', 'POST'])
def customerService():

	if request.method =='POST':
		name = request.form['name']
		phoneNumber = request.form['phonenumber']
		email = request.form['email']
		problemD = request.form['question']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('INSERT INTO questions VALUES (NULL, %s, %s,%s, %s)', (name,phoneNumber,email,problemD))
		mysql.connection.commit()
		return render_template('FormSent.html')
	else:
		return render_template('CustSer.html')

@app.route('/About')
def About():
	return render_template('About.html')

@app.route('/profile')
def profile():
    
    if 'loggedin' in session:
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        user = cursor.fetchone()
        
        return render_template('profile.html', users=user)
    
    return redirect(url_for('login'))

@app.route('/adminprofile')
def adminprofile():

	if 'adminloggedin' in session:

		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM admin WHERE adminID = %s', (session['adminID'],))
		admin = cursor.fetchone()

		return render_template('adminProfile.html')
	return redirect(url_for('adminlogin.html'))


@app.route("/listalluser" , methods=['GET', 'POST'])
def listalluser():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users ")
    listalluser = cursor.fetchall()
    return render_template ('listuser.html' ,listalluser = listalluser)

@app.route("/listallproduct" , methods=['GET', 'POST'])
def listallproduct():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Products")
    listallproduct = cursor.fetchall()
    return render_template('listallproduct.html', listallproduct = listallproduct)


@app.route("/editproduct" , methods=['GET', 'POST'])
def editproduct():
    if 'productID' in request.args:
        form = UpdateProductForm(request.form)
        productID = request.args['productID']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Products WHERE productID=%s", (productID))
        result = cursor.fetchone()

        if request.method == 'POST' and 'productName' in request.form and 'productDetail' in request.form and 'productPrice' in request.form and 'productCompany' in request.form and 'productPhoto' in request.form:
            productName = form.productName.data
            productDetail = form.productDetail.data
            productPrice = form.productPrice.data
            productCompany = form.productCompany.data
            productPhoto = form.productPhoto.data

           
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            update = cursor.execute("UPDATE Products SET productName=%s,productDetail=%s, productPrice=%s, productCompany=%s , productPhoto=%s WHERE productID=%s",
                            ( productName,productDetail,productPrice,productCompany,productPhoto,productID))
            mysql.connection.commit()

            if update:
                flash('info updated', 'success')
                return render_template('editproduct.html', result= result, form=form , )
            else:
                flash('info not updated', 'danger')
                return render_template('editproduct.html',result= result, form=form, )

        return render_template('editproduct.html', result= result, form=form, )
    return render_template('editproduct.html')

@app.route("/deleteproduct" , methods=['GET', 'POST'])
def deleteP():
    if 'productID' in request.args:
        productID = request.args['productID']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM Products where productID = %s", (productID,))
        mysql.connection.commit()
        if  deleted:
            flash('Product has been deleted')
            return render_template('listallproduct.html' ,deleted = deleted)
            
    return render_template('listallproduct.html')


@app.route("/productUpload" , methods=['GET', 'POST']) 
def uploadproduct():
    
    if request.method == 'POST' and 'productName' in request.form and 'productDetail' in request.form and 'productPrice' in request.form and 'productCompany' in request.form and 'productPhoto' in request.form  : 
        productName = request.form['productName']
        productDetail = request.form['productDetail']
        productPrice = request.form['productPrice']
        productCompany = request.form['productCompany']
        productPhoto = request.form['productPhoto']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO Products ( productName, productDetail, productPrice, productCompany, productPhoto) VALUES(%s, %s, %s, %s, %s)",( productName, productDetail, productPrice, productCompany, productPhoto))
        mysql.connection.commit()
            
                      
    return render_template ('uploadproduct.html')

@app.route("/viewquestion" , methods=['GET', 'POST'])
def viewquestion():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM questions")
    viewquestion = cursor.fetchall()
    return render_template('viewquestion.html', viewquestion = viewquestion)

@app.route("/deletequestion" , methods=['GET', 'POST'])
def deletequestion():
    if 'questionID' in request.args:
        questionID = request.args['questionID']
        cursor = mysql.connection.cursor()
        deleted = cursor.execute("DELETE FROM questions where questionID=%s", (questionID,))
        mysql.connection.commit()
        if  deleted:
            flash('question has been deleted')
            return render_template('viewquestion.html', deleted = deleted)
    return render_template('viewquestion.html')


@app.route('/adminhome')
def adminhome():
	return render_template('adminHome.html')



@app.route('/adminLogin' , methods=['GET', 'POST'])
def adminLogin():
	msg =''
	if request.method =='POST' and 'adminName' in request.form and 'adminPassword' in request.form:

		adminName = request.form['adminName']
		adminPassword = request.form['adminPassword']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM admin WHERE adminName = %s AND adminPassword= %s', (adminName, adminPassword))

		admin = cursor.fetchone()
		if admin:
			session['adminloggedin'] = True
			session['adminID'] = admin['adminID']
			session['adminName'] = admin['adminName']
			session['adminPassword'] = admin['adminPassword']
			session['adminEmail'] = admin['adminEmail']

			return render_template('adminHome.html')
		else:
			msg = 'Incorrect username/password'

	return render_template('adminlogin.html')

@app.route('/gamefun/adminlogout')
def adminlogout():
    
   session.pop('adminloggedin', None)
   session.pop('adminID', None)
   session.pop('adminName', None)

   return redirect(url_for('adminhome'))



@app.route('/Login/', methods=['GET', 'POST'])
def login():
    
    msg = ''
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        
        user = cursor.fetchone()
        
        if user:
            
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            
            return render_template('LoginS.html')
        else:
            
            msg = 'Incorrect username/password!'
    
    return render_template('Login.html', msg=msg)

    
@app.route('/gamefun/logout')
def logout():
    
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   
   return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    
    msg = ''
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if user:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
           
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            return render_template('RegistS.html')
    elif request.method == 'POST':
        
        msg = 'Please fill out the form!'
    
    return render_template('Register.html', msg=msg)






if __name__ == '__main__':
	app.run(debug=True)