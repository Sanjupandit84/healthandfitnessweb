from flask import Flask , render_template,request,redirect,flash,session
import json

from flask_mysqldb import MySQL 
app = Flask(__name__,template_folder='template')

app.secret_key="qwertyuiop"
database_conn = open('config.json','r')
configuration=json.load(database_conn)
app.config['MYSQL_HOST']=configuration['host']
app.config['MYSQL_USER']=configuration['user']
app.config['MYSQL_PASSWORD']=configuration['password']
app.config['MYSQL_DB']=configuration['database']

mysql= MySQL(app)

#HOME PAGE
@app.route('/',methods=['POST','GET'])
def homePage():
    return render_template("index.html")


#LOGIN PAGE
@app.route('/login',methods=['POST','GET'])
def loginPage():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM details where email= %s and password= %s' , (email, password))
        user=cur.fetchall()
        if user:
            return redirect('admin')
        else :
            error = 'Invalid Credentials : Please enter right details'
            return render_template('login.html',msg = error)
                
    return render_template("login.html")

#LOGOUT
@app.route('/logout')
def logout():
    return render_template('login.html')
#REGISTRATION TABLE


@app.route('/register',methods=['POST','GET'])
def registerPage():
    
    if request.method=='POST':
        user_name=request.form['name']
        user_email=request.form['email']
        user_password=request.form['password']
        user_mobile=request.form['mobile_no']
        user_dob=request.form['dob']
        queries=("insert into details(name, email, password, mobile, dob) values ('{}','{}','{}','{}','{}')").format(user_name,user_email ,user_password, user_mobile,user_dob)
        cur= mysql.connection.cursor()
        cur.execute(queries)    
        mysql.connection.commit()
        cur.close()    
        return render_template('index.html')                    
    return render_template('form.html')


# DASHBOARD- ALL DATAS

@app.route('/admin',methods=['POST','GET'])
def adminPage():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM details ORDER BY id")
    row = cur.fetchall()   
    return render_template("table.html", data=row) 

#EDIT SECTION

@app.route('/edit/<int:id>',methods=['POST','GET'])
def edit(id):
    return render_template('edit.html', id =id)

@app.route('/update',methods=['POST'])
def update():
    if request.method=='POST':
        cur = mysql.connection.cursor()
        user_id = request.form['id']
        user_name=request.form['name']  
        user_email=request.form['email']
        queries=("update details set name = '{}', email = '{}' where id = '{}'".format(user_name,user_email,user_id))  
        cur.execute(queries)
        cur.connection.commit()
        return redirect('/admin')

    return render_template('edit.html', id =id)

#DELETE SECTION

@app.route('/delete/<int:id>',methods=['POST','GET'])
def delete(id):
    return render_template('delete.html', id=id)

@app.route('/flush',methods=['POST'])
def deleteData():
   
   if request.method=='POST':
        cur = mysql.connection.cursor()
        id=request.form['id']
        queries=("DELETE FROM DETAILS where id = '{}'").format(id)  
        cur.execute(queries)
        cur.connection.commit()
        cur.close()  
        return redirect('/admin')
   return render_template('delete.html',id=id)



if __name__=='__main__':
    app.run(debug=True)  
    