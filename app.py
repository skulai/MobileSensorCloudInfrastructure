from flask import Flask, flash, render_template, json, request, redirect, url_for, session
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from validate_email import validate_email
import itertools
import subprocess
import sys
import cgi
import time
import re
import boto3
import sys

ec2 = boto3.resource('ec2')


#app.jinja_env.add_extension('jinja2.ext.loopcontrols')

aform = cgi.FieldStorage()

vid = aform.getvalue("vid", "error")

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['TEMPLATES_AUTO_RELOAD']=True

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = ''
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = ''
app.config['MYSQL_DATABASE_HOST'] = ''
mysql.init_app(app)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/signIn',methods=['POST','GET'])
def signIn():
    username = request.form['inputName']
    password = request.form['inputPassword']
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT userid from user where username='" + username + "' and password='" + password + "'")
    data = cursor.fetchone()
    if data is None:
     print "Username or Password is wrong"
     return 'incorrect'
    elif username=='admin' and password=='admin':
     session['username'] = username
     session['usertype'] = 'admin'
     return url_for('showAdminDashboard')
    else:
     session['username'] = username
     session['userid'] = data[0]
     session['usertype'] = 'user'
     print "User logged in successfully"
     return url_for('showUserDashboard')

@app.route('/signOut')
def signOut():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('main'))

@app.route('/AdminDashboard')
def showAdminDashboard():
    return render_template('AdminIndex.html', name = 'Admin')

@app.route('/UserDashboard')
def showUserDashboard():
    if 'username' in session:
      username = session['username']
      return render_template('UserIndex.html', name = username)
    else:
      return render_template('index.html')

@app.route("/AdminBilling")
def adminBilling():
    cursor =mysql.connect().cursor()
    cursor.execute("SELECT billingid,username,totalcount,totalamount,paymentstatus,year,month FROM msd.billing inner join user on user.userid = billing.userid")
    billing = cursor.fetchall()
    return render_template('AdminBilling.html', billing = billing)

@app.route("/AdminUserListing")
def adminUserListing():
    cursor =mysql.connect().cursor()
    cursor.execute("select userid, username, fullname, address, credicardinfo, email from user where usertype='user'")
    users = cursor.fetchall()
    return render_template('AdminUserListing.html', users = users)

@app.route("/AdminSensorMonitoring")
def adminSensorMonitoring():
    return render_template('AdminSensorMonitoring.html')

@app.route("/UserBilling")
def userBilling():
  if 'username' in session:
    username = session['username']
    #SELECT count(*), userid, YEAR(time), monthname(time), time FROM msd.sensordata inner join uservnmapping on sensordata.vid = uservnmapping.vid group by userid, YEAR(time), monthname(time);
    cursor =mysql.connect().cursor()
    cursor.execute("select billingid, month, year, totalcount, totalamount, paymentstatus from billing where userid="+str(session['userid']))
    bills = cursor.fetchall()
    #return json.dumps(sensors)
    #return render_template('AddSensors.html', sensors = sensors)
    return render_template('UserBilling.html', name = username, bills = bills)
  else:
    return render_template('signup.html')

@app.route("/UserProfile")
def userProfile():
  if 'username' in session:
    username = session['username']
    cursor =mysql.connect().cursor()
    cursor.execute("Select userid,username,fullname,address,email from user where username ='"+username+"'")
    details = cursor.fetchone()
    return render_template('UserProfile.html',details=details, name = username)
  else:
    return render_template('signup.html')

@app.route("/updateProfile", methods=['POST'])
def updateProfile(): 
    if 'username' in session:
        username = session['username']
    conn = mysql.connect() 
    cursor = conn.cursor()
    cursor.execute("Select userid,username,fullname,address,email from user where username ='"+username+"'")
    details = cursor.fetchone()    
    cursor.execute("UPDATE user SET fullname='"+ request.form['fullname']+"',address ='"+request.form['address']+"',email ='"+request.form['email']+"'where username='"+ username + "'")
    conn.commit()
    cursor.close()    
    return render_template('UserProfile.html',msg="Update Successfull",details=details, name = username)
	
@app.route("/getSensors/<vid>",methods=["GET"])
def getSensorsInNetwork(vid):
        cursor =mysql.connect().cursor()
        cursor.execute("select sensorid,sensorname,sensortype,sensorlocation,sensorstatus, vnstatus from sensor natural join vnsensormapping natural join virtualnetwork where vid ='" + vid +"'")
        sensors = cursor.fetchall()
        cursor.execute("select sensorid,value,time,sensortype from sensordata natural join sensor where sensordata.vid='"+vid+"'Group by sensorid")
        sensordata = cursor.fetchall()
        print "sensor data"
        print sensordata
        retVal ={"sensors":sensors,"sensordata":sensordata}
        print json.dumps(retVal)
        return json.dumps(retVal)


@app.route("/fetchSensorData/",methods=["GET"])
def fetchSensorData():
    sid = request.args.get('sid')
    vid = request.args.get('vid')
    cursor = mysql.connect().cursor()
    cursor.execute("select value,time,sensortype from sensordata natural join sensor where sensorid ='" + sid +"' and sensordata.vid='"+vid+"'")
    sensordata = cursor.fetchall()
    return json.dumps(sensordata)

@app.route("/stop")
def stopNetwork():
    return render_template('StopNetwork.html')

@app.route("/create")
def sensorServices():
  if session.get('username'):
    username = session['username']
    cursor = mysql.connect().cursor()

    cursor.execute("SELECT sensorname, latitude, longitude, sensorid from sensor where sensortype='Temperature'")
    temperature = cursor.fetchall()

    cursor.execute("SELECT sensorname, latitude, longitude, sensorid from sensor where sensortype='Pressure'")
    pressure = cursor.fetchall()

    cursor.execute("SELECT sensorname, latitude, longitude, sensorid from sensor where sensortype='Humidity'")
    humidity = cursor.fetchall()

    return render_template('SensorServices.html', name = username, temperature=json.dumps(temperature), pressure=json.dumps(pressure), humidity=json.dumps(humidity))

  else:
        return render_template('signup.html')

@app.route('/addSensor', methods=['POST'])
def addSensor():
    print 'inside add sensor'
    sensors = request.json['sensor']
    networkName = request.json['networkName']
    username = session['username']
    cnx = mysql.connect()
    cursor = cnx.cursor()

    cursor.execute("SELECT userid from user where username='" + username + "'")
    tempid = cursor.fetchone()
    userid = int(tempid[0])

    # To fetch last vid from table
    cursor.execute("SELECT vid FROM virtualnetwork ORDER BY vid DESC LIMIT 1;")
    data = cursor.fetchone()
    vid = int(data[0]) + 1
    print vid

    add_vn = ("INSERT INTO virtualnetwork "
                "(vid, vnname, vnstatus) "
                "VALUES (%s, %s, %s)")
    data_vn = (vid,networkName, 'E')
    cursor.execute(add_vn, data_vn)
    cnx.commit()

    for i in range(0, len(sensors)):
        add_vnsensor = ("INSERT INTO vnsensormapping "
                    "(vid, sensorid, sensorstatus) "
                    "VALUES (%s, %s, %s)")
        data_vnsensor = (vid,int(sensors[i]), 'E')
        cursor.execute(add_vnsensor, data_vnsensor)
    cnx.commit()

    add_uservn = ("INSERT INTO uservnmapping "
                "(userid, vid) "
                "VALUES (%s, %s)")
    data_uservn = (userid,vid)
    cursor.execute(add_uservn, data_uservn)
    cnx.commit()
    instance_ip = getInstance()
    cursor.execute("SELECT idInstance FROM Instance where ipaddr = '"+instance_ip+"';")
    tempinstid = cursor.fetchone()
    instid = int(tempinstid[0])
    print("Instid")
    print instid
    print("Inserting into instancevnmapping")
    add_instvn = ("INSERT INTO instancevnmapping "
                "(instanceid, vid) "
                "VALUES (%s, %s)")
    data_instvn = (instid,vid)
    cursor.execute(add_instvn, data_instvn)
    cnx.commit()    
    subprocess.Popen(["ssh", "ec2-user@"+str(instance_ip), "cd /home/ec2-user; sh cscript.sh "+ str(vid) +" > /dev/null &"])

    return render_template('SensorServices.html')

@app.route("/billingMetrics")
def billingMetrics():
   if session.get('username'):
      username = session['username']
      return render_template('BillingMetrics.html',name = username)
   else:
      return render_template('signup.html')

@app.route("/view")
def viewNetwork():
    if session.get('username'):
        username = session['username']
        cursor = mysql.connect().cursor()
        cursor.execute("SELECT userid from user where username='" + username + "'")
        tempid = cursor.fetchone()
        userid = str(tempid[0])
		#getting network for each user
        cursor.execute("SELECT vid FROM uservnmapping where userid='"+ userid +"'")
        network = cursor.fetchall()
        if network:
          userNetworkList =tuple( list(itertools.chain(*network)))
          print network
          print len(userNetworkList)
          print userNetworkList
          if len(userNetworkList) == 1:
		      cursor.execute("select vn.vid,vnname,idInstance,ipaddr,status,ec2instanceid, ec2instancetype from virtualnetwork as vn Natural Join instancevnmapping Inner JOIN Instance on instancevnmapping.instanceid =Instance.idInstance where vid = "+ str(userNetworkList[0]))
          else:
              cursor.execute("select vn.vid,vnname,idInstance,ipaddr,status,ec2instanceid, ec2instancetype from virtualnetwork as vn Natural Join instancevnmapping Inner JOIN Instance on instancevnmapping.instanceid =Instance.idInstance where vid in "+ str(userNetworkList))		  
          network_details =cursor.fetchall()
          print network_details
        else:
          network = 0
          network_details = 0
        #cursor.execute("Select sensorname, sensortype, sensorlocation from sensor")
        #sensors = cursor.fetchall()
        cursor.close()
        return render_template('ViewNetwork.html',name = username,network_details = network_details, network = network)
    else:
        return render_template('signup.html')
	  
	  
@app.route("/usage")
def usage():
   if session.get('username'):
      username = session['username']
      cursor = mysql.connect().cursor()
      cursor.execute("SELECT userid from user where username='" + username + "'")
      tempid = cursor.fetchone()
      userid = str(tempid[0])
	  #getting network for each user
      cursor.execute("SELECT vid FROM uservnmapping where userid='"+ userid +"'")
      network = cursor.fetchall()
      userNetworkList =tuple( list(itertools.chain(*network)))
      print userNetworkList 
      cursor.execute("Select count(sensorid),vid from sensordata where vid in "+ str(userNetworkList)+"Group by vid")
      cntSensordata = cursor.fetchall()
      return render_template('Usage.html',name = username,cntSensordata=json.dumps(cntSensordata))
   else:
      return render_template('signup.html')

@app.route('/createInstance',methods=['POST','GET'])
def createInstance():
   if session.get('username'):
      conn = mysql.connect()
      cursor = conn.cursor()
      cursor.execute("SELECT ipaddr from Instance where status='Y'")
      available_instances = cursor.fetchall()
      print available_instances
      if available_instances is None:
        # TODO: Call API to create new instance on openstack and add the instance ip addr to Instance table
          instance_provisioned = cursor.fetchone()
      else:
          #Instance is available in pool
          instance_provisioned = available_instances[0]
          #Update status of instance to 'N' for not available
          cursor.callproc('updateStatus',instance_provisioned)
          conn.commit()

      return instance_provisioned

   else:
      return render_template('signup.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')


@app.route('/signUp',methods=['POST','GET'])
def signUp():
    #try:
    _fullname = request.form['fullName']
    _creditcardinfo = request.form['creditCard']
    _address = request.form['address']
    _username = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    _confirmPassword = request.form['confirmPassword']
    _usertype = "user"

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * from user where username='" + _username + "'")
    data = cursor.fetchone()
    if data is not None:
        return 'Username already exists. Please try other username!'

    if not validate_email(_email):
        return 'Please enter valid email id'

    if not re.match(r'[A-Za-z0-9@#$%^&+=]{5,}', _password):
        return 'Password should be of atleast 5 characters'

    if _password != _confirmPassword:
        print "not confirmed"
        return 'ConfirmPassword must match password. Please try again'

    #_hashed_password = generate_password_hash(_password)
    cursor.callproc('createUser',(_username,_password,_email,_usertype,_fullname,_address,_creditcardinfo))
    data = cursor.fetchall()

    if len(data) is 0:
        conn.commit()
    return 'User created successfully!'


@app.route("/turnoffsensor",methods=['POST'])
def turnoffsensor():
    print(request)

    #print(vid)
    j = request.json
    tvid = j['vid']
    tsid = j['sid']
    #vid2 = request.form['vid']
    #print(vid2)
    #vid3 = request.vid
    #print(vid3)
    #vid = request.json['vid']
    #print(vid)
    #print(vid+"Inside tos"+sid)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("update vnsensormapping set sensorstatus='D' where vid='"+tvid+"' and sensorid='"+tsid+"'")
    conn.commit()
    #sensors = cursor.fetchall()
    #return json.dumps(sensors)
    #return render_template('AddSensors.html', sensors = sensors)
    return "Hi"

@app.route("/mybillpayment",methods=['POST'])
def mybillpayment():
    print(request)

    #print(vid)
    jso = request.json
    print("-------")
    print(jso)
    tbillingid = jso['billing_id']
    #vid2 = request.form['vid']
    #print(vid2)
    #vid3 = request.vid
    #print(vid3)
    #vid = request.json['vid']
    #print(vid)
    #print(vid+"Inside tos"+sid)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("update billing set paymentstatus='Paid' where billingid='"+str(tbillingid)+"'")
    conn.commit()
    #sensors = cursor.fetchall()
    #return json.dumps(sensors)
    #return render_template('AddSensors.html', sensors = sensors)
    return "Hi"


@app.route("/deleteinst",methods=['POST'])
def deleteinstance():
    #print(request)
    print("Inside delete Instance")
    #print(vid)
    jso = request.json
    print("-------")
    print(jso)
    tinstanceid = jso['instanceid']
    print tinstanceid
    #vid2 = request.form['vid']
    #print(vid2)
    #vid3 = request.vid
    #print(vid3)
    #vid = request.json['vid']
    #print(vid)
    #print(vid+"Inside tos"+sid)
    
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("select ec2instanceid from Instance where idInstance='"+tinstanceid+"'")
    tec2instanceid = cursor.fetchone()
    cursor.close()
    conn.close()

    conn3 = mysql.connect()
    cursor3 = conn3.cursor()
    cursor3.execute("delete from instancevnmapping where instanceid='"+str(tinstanceid)+"'")
    conn3.commit()
    cursor3.close()
    conn3.close()
    
    conn2 = mysql.connect()
    cursor2 = conn2.cursor()
    cursor2.execute("delete from Instance where idInstance='"+str(tinstanceid)+"'")
    conn2.commit()
    print("Deleting Instance")
    print str(tec2instanceid[0])
    ec2.instances.filter(InstanceIds=[str(tec2instanceid[0])]).terminate()
    print("Instance deleted")
    cursor2.close()
    conn2.close()
    #sensors = cursor.fetchall()
    #return json.dumps(sensors)
    #return render_template('AddSensors.html', sensors = sensors)
    
    #print "Instance " + tinstanceid+ " terminated successfully"
    return "Hi"


@app.route("/turnonsensor",methods=['POST'])
def turnonsensor():
    print(request)

    #print(vid)
    j = request.json
    tvid = j['vid']
    tsid = j['sid']
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("update vnsensormapping set sensorstatus='E' where vid='"+tvid+"' and sensorid='"+tsid+"'")
    conn.commit()
    return "Hi"


@app.route("/turnoffvn",methods=['POST'])
def turnoffvn():
    print(request)

    #print(vid)
    j = request.json
    tvid = j['vid']
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("update virtualnetwork set vnstatus='D' where vid='"+tvid+"'")
    conn.commit()
    return "Hi"

@app.route("/turnonvn",methods=['POST'])
def turnonvn():
    print(request)

    #print(vid)
    j = request.json
    tvid = j['vid']
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("update virtualnetwork set vnstatus='E' where vid='"+tvid+"'")
    conn.commit()
    return "Hi"




@app.route("/AddSensors")
def addSensors():

  if session.get('username'):
    cursor =mysql.connect().cursor()
    cursor.execute("select sensorid, sensorname, sensortype, sensorlocation, sensorurl, latitude, longitude from sensor")
    sensors = cursor.fetchall()
    #return json.dumps(sensors)
    return render_template('AddSensors.html', sensors = sensors)
  else:
    return render_template('signup.html')

@app.route("/AddSensorsForm", methods=['POST'])
def addSensorsForm():
    #try:
  if session.get('username'):
    _sensorname = request.form['sensorname']
    _sensortype = request.form['sensortype']
    _sensorlocation = request.form['sensorlocation']
    _measurementunit = request.form['measurementunit']
    _sensorurl = request.form['sensorurl']
    _sensoruid = request.form['sensoruid']
    _sensorlatitude = request.form['sensorlatitude']
    _sensorlongitude = request.form['sensorlongitude']

    #_confirmPassword = request.form['confirmPassword']
    #if _password != _confirmPassword:
    #    return 'ConfirmPassword must match password. Please try again'

    conn = mysql.connect()
    cursor = conn.cursor()
    print("insert into sensor (sensorname, sensortype, sensorlocation, measurementunit, sensorurl, sensoruid, latitude, longitude) values ('"+_sensorname+"','"+_sensortype+"','"+_sensorlocation+"','"+_measurementunit+"','"+_sensorurl+"','"+_sensoruid+"','"+_sensorlatitude+"','"+_sensorlongitude+"')")
    cursor.execute("insert into sensor (sensorname, sensortype, sensorlocation, measurementunit, sensorurl, sensoruid, latitude, longitude) values ('"+_sensorname+"','"+_sensortype+"','"+_sensorlocation+"','"+_measurementunit+"','"+_sensorurl+"','"+_sensoruid+"','"+_sensorlatitude+"','"+_sensorlongitude+"')")
    conn.commit()
    #_hashed_password = generate_password_hash(_password)
    #cursor.callproc('createUser',(_username,_password,_email))
    #data = cursor.fetchall()

    cursor =mysql.connect().cursor()
    cursor.execute("select sensorid, sensorname, sensortype, sensorlocation, sensorurl, latitude, longitude from sensor")
    sensors = cursor.fetchall()
    #return json.dumps(sensors)
    return render_template('AddSensors.html', sensors = sensors)
  else:
    return render_template('signup.html')


@app.route("/AdminAddInstance")
def AdminAddInstance():
  if session.get('username'):
    cursor =mysql.connect().cursor()
    cursor.execute("select * from Instance")
    instances = cursor.fetchall()
    #return json.dumps(sensors)
    #return render_template('AddSensors.html', sensors = sensors)
    #return render_template('UserBilling.html')
    return render_template('AdminAddInstance.html', instances = instances)
  else:
    return render_template('signup.html')

@app.route("/addNewInstance",methods=['POST'])
def addNewInstance():
    from ec2.createInstance import create_instance
    print("Inside addNewInstance")
    dict = create_instance()
    string = 'ec2-user@' + str(dict['dns'])
    print(string)
    time.sleep(200)
    subprocess.Popen(["ssh", str(string), "cd /home/ec2-user; sudo yum -y update; sudo yum -y install mysql; wget -nc 'pnahar.x10.bz/cscript.sh'; wget -nc 'pnahar.x10.bz/jq' ; chmod 777 jq; chmod 777 cscript.sh; sh cscript.sh 1 > /dev/null &"])
    add_instance = ("INSERT INTO Instance "
                "(ipaddr, status, ec2instanceid, ec2instancetype) "
                "VALUES (%s, %s, %s, %s)")
    data_instance = (dict['ip_address'], 'N', dict['id'], dict['instance_type'])
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(add_instance, data_instance)
    conn.commit()
    return "Hi"

def getInstance():
   
      conn = mysql.connect()
      cursor = conn.cursor()
      cursor.execute("SELECT ipaddr from Instance where status='Y'")
      available_instances = cursor.fetchone()
      print available_instances
      if available_instances is None:
        # TODO: Call API to create new instance on openstack and add the instance ip addr to Instance table
          instance_provisioned = cursor.fetchone()
      else:
          #Instance is available in pool
          instance_provisioned = str(available_instances[0])
          print("Instance Provisioned")
          print instance_provisioned
          #Update status of instance to 'N' for not available
          cursor.callproc('updateInstanceStatus',[instance_provisioned])
          conn.commit()

      return instance_provisioned


#pn

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5002,debug=True)
