import pymysql
from flask import Flask, request, jsonify,render_template
from werkzeug import secure_filename
from flask import send_file
import datetime 
import calendar 
from datetime import date

#connect sql to python
my=pymysql.connect(host='localhost',user='user_name',password='password',db='database_name')
con=my.cursor()
    
app = Flask('api')

#HTML Page to interact withh user
@app.route('/')
def home():
    return render_template('home.html')


#check available bus according to requirement
@app.route('/checkBus', methods=['POST'])
def checkBus():
    # get data from html page
    source = str(request.form['source'])
    destination = str(request.form['destination'])
    date = str(request.form['date'])

    # convert date to fay and number
    born = datetime.datetime.strptime(date, '%d %m %Y').weekday() 
    day=calendar.day_name[born] 

    day_num=0
    
    if day=="Monday":
        day_num=0
    if day=="Tuesday":
        day_num=1
    if day=="Wednesday":
        day_num=2
    if day=="Thursday":
        day_num=3
    if day=="Friday":
        day_num=4
    if day=="Saturday":
        dat_num=5
    if day=="Sunday":
        day_num=6
        
    # select data from database accprding to the conditions
    query="select * from BusInfo where source='"+source+"' and destination='"+destination+"';"
    v= con.execute(query)
    data=con.fetchall()
    res=[]
    for i in range(len(data)):
        a1=6+day_num
        # -1 denotes that bus will not work that day
        print(data[i][a1])
        if data[i][a1]!="-1":
            res.append(data[i][1])
    # return required result
    return render_template('result.html',data=res)

# reserve seat for the user in required bus    
@app.route('/reserveseat', methods=['POST'])
def reserveseat():
    # get data from HTML page
    username = str(request.form['username'])
    BusNumber = str(request.form['BusNumber'])
    date = str(request.form['date'])
    seat = str(request.form['seat'])

    # convert date to day and number
    born = datetime.datetime.strptime(date, '%d %m %Y').weekday() 
    day=calendar.day_name[born] 

    day_num=0
    
    if day=="Monday":
        day_num=0
    if day=="Tuesday":
        day_num=1
    if day=="Wednesday":
        day_num=2
    if day=="Thursday":
        day_num=3
    if day=="Friday":
        day_num=4
    if day=="Saturday":
        dat_num=5
    if day=="Sunday":
        day_num=6
        
    # select data from database
    query="select * from BusInfo where BusNumber='"+BusNumber+"'"
    v= con.execute(query)
    data=con.fetchall()

    #result
    res=[]
    
    a1=6+day_num
    required=int(seat)
    available=int(data[0][a1])
    if available>=required:
        #required number of seats are available
        available=available-required
        available=str(available)
    else:
        #required number of seats not available
        return render_template('result.html',data="Failure")

    # update bus seats
    sql = "update BusInfo set "+day+"='"+available+"' where BusNumber='"+BusNumber+"'"
    v=con.execute(sql)
    my.commit()  

    # insert user info into user table
    sql = "INSERT INTO userinfo(UserName,BusNumber,source,destination,date,NumberofSeats) VALUES (%s, %s,%s,%s,%s,%s)"
    val = (username,BusNumber,data[0][2],data[0][3],date,str(required))
    con.execute(sql, val)
    my.commit()

    # return required result
    return render_template('result.html',data="Success")


# check seats booked by the user
@app.route('/checkUserReserved', methods=['POST'])
def checkUserReserved():
    # fetch data from html page
    username = str(request.form['username'])
    today = date.today()
    today=str(today)
    #2020-08-10
    year=int(today[0:4])
    month=int(today[5:7])
    day=int(today[8:10])
    print(year,month,day)

    query="select * from userInfo where username='"+username+"'"
    v=con.execute(query)
    data=con.fetchall()

    # for past reservations
    past=["past reservations"]

    #for future reservations
    post=["Future reservations"]
    for i in range(len(data)):
        temp=data[i][4]
        temp_year=int(temp[6:10])
        temp_month=int(temp[3:5])
        temp_day=int(temp[0:2])
        #check fectch date is older of current date or not
        if temp_year< year:
            past.append(data[i])
        elif temp_year==year and temp_month<month:
            past.append(data[i])
        elif temp_year==year and temp_month==month and temp_day<day:
            past.append(data[i])
        else:
            post.append(data[i])
            
    res=[]
    if len(past)>1:
        res.append(past)
    if len(post)>1:
        res.append(post)

    # return required result
    return render_template('result.html',data=res)
    
if __name__ == '__main__':
  #app.debug = True
  #app.run(host='0.0.0.0', port=port)
  app.run(host='127.0.0.1', port=7070)


