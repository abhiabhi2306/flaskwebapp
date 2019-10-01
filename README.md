# Flask Web Application

This is a simple web application using [Python Flask](http://flask.pocoo.org/) and [MySQL](https://www.mysql.com/) database. 
  
  
 Functions of the web application are:
 - Login
 - Sign Up
 - Post Thread
 - View Threads
 - Edit Thread
 - Delete Thread
 
 
  Below are the steps required to get this working on a base linux system.
  
  - Install all required dependencies
  - Install and Configure Web Server
  - Start Web Server
   
## 1. Install all required dependencies inorder for the application to work
  
  Python and its dependencies

    apt-get install -y python python-setuptools python-dev build-essential python-pip python-mysqldb

   
## 2. Install and Configure Web Server

Install The Required Flask Dependencies using pip.

    pip -r install requirements.txt

- Copy app.py or download it from source repository
- Configure database credentials and parameters 

## 3. Start Web Server

Start web server

    FLASK_APP=app.py flask run --host=0.0.0.0
    
## 4. Visit the web application.

Open a browser and go to URL

    http://<IP>:5000                      
    http://<IP>:5000/          
