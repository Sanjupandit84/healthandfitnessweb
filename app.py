from flask import Flask , render_template, request, redirect, url_for
import json
from flask_mysqldb import MySQL 
import base64

app = Flask(__name__,template_folder='templates')

app.secret_key="qwertyuiop"
database_conn = open('config.json','r')
configuration=json.load(database_conn)
app.config['MYSQL_HOST']=configuration['host']
app.config['MYSQL_USER']=configuration['user']
app.config['MYSQL_PASSWORD']=configuration['password']
app.config['MYSQL_DB']=configuration['database']

mysql= MySQL(app)

@app.route('/',methods=['POST','GET'])
def homePage():
    return render_template("home.html")

@app.route('/about',methods=['POST','GET'])
def about():
    return render_template("about.html")

@app.route('/welcome',methods=['POST','GET'])
def welcome():
    return render_template("about.html")

@app.route('/service',methods=['POST','GET'])
def service():
    return render_template("service.html")

@app.route('/contact',methods=['POST','GET'])
def contact():
    return render_template("contact.html")
 

@app.route('/OurTeam',methods=['POST','GET'])
def Team():
    return render_template("ourTeam.html")

@app.route('/Gymshedule',methods=['POST','GET'])
def shedule():
    return render_template("schedule.html")

@app.route('/gym',methods=['POST','GET'])
def gym():
    return render_template("gymRegist.html")


@app.route('/blog',methods=['POST','GET'])
def showblog():
    cur = mysql.connection.cursor()
    cur.execute("SELECT title, image, content FROM blog_details ")
    images=[]
    fetch = cur.fetchall() 
     
    for row in fetch:
        title=row[0]
        content=row[2] 
        image_id =row[0]
        image_data =row[1]
        image_bytes = bytes(image_data)
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        images.append((image_id,title,image_base64,content))

    return render_template("blog.html", images=images) 
 
@app.route('/Registration',methods=['POST','GET'])
def entry():
    
    if request.method=='POST':
      username=  request.form['name']
      useremail=  request.form['email']
      usermobile=  request.form['mobile']
      userqualification=  request.form['qualification']
      useraddress=  request.form['address']
      
      query=("insert into registration(name, email, mobile, qualification, address) values('{}','{}','{}','{}','{}')").format(username,useremail,usermobile,userqualification,useraddress)
      cur=mysql.connection.cursor()
      cur.execute(query)
      mysql.connection.commit()
      return render_template('memberWelcome.html' , message="you are successsfuly submit your registration")
    # return render_template('gymRegist.html' , message="you are successsfuly submit your registration")
    



@app.route('/Contact',methods=['POST','GET'])
def call():
    
    if request.method=='POST':
      username=  request.form['name']
      useremail=  request.form['email']
      usermobile=  request.form['message']
     
      
      query=("insert into contact(name, email, message ) values('{}','{}','{}')").format(username,useremail,usermobile)
      cur=mysql.connection.cursor()
      cur.execute(query)
      
      mysql.connection.commit()
      return render_template('contact.html' , message="successsfuly send")

@app.route('/search')
def search():
    query = request.args.get('search')
    cur = mysql.connection.cursor()
    cur.execute("SELECT title, image, content FROM blog_details WHERE LOWER(title) LIKE %s", ('%' + query.lower() + '%',))
    images=[]
    data = cur.fetchall() 
    if data:
        for row in data:
            title=row[0]
            content=row[2] 
            image_id =row[0]
            image_data =row[1]
            image_bytes = bytes(image_data)
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            images.append((image_id,title,image_base64,content))
        cur.close()
        return render_template("search.html", result = images)
    else:
        cur.close()
        return render_template("search.html", msg='Blog not found')

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

 

@app.route('/write',methods=['POST','GET'])
def writeBlog():
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files['file']
        image=file.read()
        
        cur= mysql.connection.cursor()
        cur.execute(" INSERT INTO blog_details (title, image, content) VALUES (%s, %s, %s)", (title, image ,content))
        mysql.connection.commit() 
        return redirect(url_for('showblog'))                 
    return render_template('write_blog.html')


@app.route('/admin',methods=['POST','GET'])
def admin():
    cur = mysql.connection.cursor()
    cur.execute("SELECT title, image, content, id  FROM blog_details ")
    images=[]
    fetch = cur.fetchall() 
    for row in fetch:
        
        title=row[0]
        content=row[2] 
        image_id =row[0]
        image_data =row[1]
        id=row[3]
        image_bytes = bytes(image_data)
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        images.append((image_id,title,image_base64,content,id))

    return render_template("admin_panel.html", images=images) 




@app.route('/edit/<int:id>',methods=['POST','GET'])
def edit(id):
    return render_template('edit.html', id =id)

@app.route('/update',methods=['POST'])
def update():
    if request.method == 'POST':
        post_id = request.form['id']
        new_title = request.form['title']
        new_content = request.form['content']
        filename = request.files['file']
        post_image=filename.read()
        cur = mysql.connection.cursor()
        update_query = "UPDATE blog_details SET title=%s, content=%s, image=%s WHERE id=%s"
        cur.execute(update_query, (new_title, new_content, post_image, post_id))
        cur.connection.commit()
        return redirect('/admin')
    return render_template('edit.html', id=id)



@app.route('/delete/<int:id>',methods=['POST','GET'])
def delete(id):
    return render_template('delete.html', id=id)

@app.route('/flush',methods=['POST'])
def deleteData():
   
   if request.method=='POST':
        cur = mysql.connection.cursor()
        post_id=request.form['id']
        queries=("DELETE FROM blog_details where id = '{}'").format(post_id)  
        cur.execute(queries)
        cur.connection.commit()
        cur.close()  
        return redirect('/admin')
   return render_template('delete.html',id=post_id)

if __name__=='__main__':
    app.run(debug=True) 