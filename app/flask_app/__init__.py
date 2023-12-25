# python -m flask --app ./flask/myapp run
from datetime import datetime, timedelta
import pandas as pd

from flask import Flask, request, redirect, url_for, session
from flask import render_template, make_response

import pymysql
import folium
from folium import plugins

usr_name = ""
database_password__ = "houpr1013"
name_forget = ''
name_exists :bool = True
devices = []

app = Flask(__name__)
app.secret_key="my_key"

def get_devices():
    conn = pymysql.connect(
        host='mysql',
        user='houpr',
        password=database_password__,
        database='IoT'
        )
    cursor = conn.cursor()
    sql = "select * from device order by add_date asc"
    cursor.execute(sql)
    res = cursor.fetchall()
    #print(res)
    global devices
    devices = []
    for p in res:
        dic = dict()
        dic["id"] = p[0]
        dic["category"] = p[1]
        dic["add_date"] = p[2].strftime("%Y-%m-%d %H:%M:%S")[0:10]
        dic["name"] = p[3]
        dic["price"] = p[4]
        devices.append(dic)
    #print(devices)

@app.route('/index.html')
def index():
    conn = pymysql.connect(
        host='mysql',
        user='houpr',
        password=database_password__,
        database='IoT'
        )
    cursor = conn.cursor()
    sql = "select count(id) from device"    # get the number of devices
    cursor.execute(sql)
    num = cursor.fetchone()[0]
    sql = "select min(add_date) from device"    # get the add date for first device
    cursor.execute(sql)
    duration = cursor.fetchone()[0]
    nday = datetime.now()
    if duration == None:
        duration = 0
    else:
        duration = nday - duration
        duration = duration.days

    sql = "select count(*) as row_cnt from data"
    cursor.execute(sql)
    data = cursor.fetchone()[0]

    sql = "select id, count(*) as row_cnt from data group by id order by row_cnt desc limit 1"
    cursor.execute(sql)
    id = cursor.fetchone()[0]
    sql = "select name from device where id = %s"
    cursor.execute(sql, id)
    active = cursor.fetchone()[0]

    sql = "select min(add_date) as min_date, max(add_date) as max_date from device"
    cursor.execute(sql)
    res = cursor.fetchall()[0]
    min_date = res[0]
    max_date = res[1]

    step = timedelta(days=30)
    current_date = min_date

    month_cnt = []
    while True:
        sql = "select count(id) as count from device where add_date <= %s"
        cursor.execute(sql, current_date)
        res = cursor.fetchone()
        month_cnt.append({"month": current_date.strftime('%Y-%m-%d'), "count": res[0]})
        current_date += step
        if current_date > max_date + step:
            break

    #print(month_cnt)
    get_devices()

    return render_template("index.html", number = num, time = duration, data = data, active = active, home = usr_name, member=devices, area_chart=month_cnt)

@app.route('/device.html/<name>')
def device(name):
    conn = pymysql.connect(
        host='mysql',
        user='houpr',
        password=database_password__,
        database='IoT'
        )
    cursor = conn.cursor()
    sql = 'select id from device where name = %s'
    cursor.execute(sql, name)
    id = cursor.fetchall()[0]
    sql = "SELECT id, timestamp, lng, lat, info, value, alert FROM data where id = %s ORDER BY id, timestamp"
    cursor.execute(sql, id)
    res = cursor.fetchall()
    data_list = [list(row) for row in res]
    sql = 'select timestamp, value from data where id = %s order by timestamp asc'
    cursor.execute(sql, id)
    res = cursor.fetchall()
    value = []
    for row in res:
        value.append({"time": row[0].strftime('%Y-%m-%d %H:%M:%S'), "value": row[1]})
        
    sql = 'select count(id) from data where id = %s and alert = 1'
    cursor.execute(sql, id)
    alert_cnt = cursor.fetchone()[0]
    sql = 'select count(id) from data where id = %s and alert = 0'
    cursor.execute(sql, id)
    normal_cnt = cursor.fetchone()[0]
    pie_data = [normal_cnt, alert_cnt]

    return render_template("device.html", home = usr_name, result = data_list, person=name, member=devices, value = value, pie_data = pie_data)

@app.route('/statistic.html')
def statistic():
    get_devices()
    conn = pymysql.connect(
        host='mysql',
        user='houpr',
        password=database_password__,
        database='IoT'
        )
    cursor = conn.cursor()
    sql = "SELECT id, timestamp, lng, lat, info, value, alert FROM data ORDER BY id, timestamp"
    cursor.execute(sql)
    res = cursor.fetchall()
    data_list = [list(row) for row in res]
        
    sql = 'select count(id) from data where alert = 1'
    cursor.execute(sql)
    alert_cnt = cursor.fetchone()[0]
    sql = 'select count(id) from data where alert = 0'
    cursor.execute(sql)
    normal_cnt = cursor.fetchone()[0]
    pie_data = [normal_cnt, alert_cnt]

    sql = "select name, count(*) from data natural join device group by id order by add_date"
    cursor.execute(sql)
    res = cursor.fetchall()
    bar_label = []
    bar_value = []
    for row in res:
        bar_label.append(row[0])
        bar_value.append(row[1])

    bar_data = {"label": bar_label, "data": bar_value}
    #print(bar_data["label"])
    #现在貌似数据没穿进去

    return render_template("statistic.html", home = usr_name, bar_data = bar_data, data_list = data_list, result = devices, member=devices, pie_data = pie_data)


def is_positive_number(s):
    try:
        number = float(s)
        return number > 0
    except ValueError:
        return False

@app.route('/add.html', methods=['GET', 'POST'])
def add():
    name_duplicate_error = False
    empty_error = False
    price_error = False
    success = False
    get_devices()
    if request.method == "POST":
        insert = True
        if request.form['category']=="" or request.form['name']=="" or request.form['price']=="":
            empty_error = True
            insert = False
        elif not is_positive_number(request.form['price']):
            price_error = True
            insert = False
        else:
            conn = pymysql.connect(
            host='mysql',
            user='houpr',
            password=database_password__,
            database='IoT'
            )
            cursor = conn.cursor()
            sql = "select name from device where name=%s"
            cursor.execute(sql, request.form['name'])
            res = cursor.fetchone()
            if res!=None:
                name_duplicate_error = True
                insert = False
                
        if insert:
            sql = "insert into device(category, add_date, name, price) values(%s,%s,%s,%s)"
            cursor.execute(sql,(request.form['category'],datetime.now(),request.form['name'],request.form['price']))
            conn.commit()
            success = True
            get_devices()
            session.clear()

        if name_duplicate_error or empty_error or price_error:
            session['category'] = request.form['category']
            session['name'] = request.form['name']
            session['price'] = request.form['price']

    return render_template("add.html", home = usr_name, member=devices, result=devices, name_duplicate_error=name_duplicate_error, empty_error = empty_error, price_error = price_error, session = session, success=success)

@app.route('/delete.html', methods=['GET', 'POST'])
def delete():
    not_exist_error = False
    empty_error = False
    success = False
    get_devices()
    if request.method == "POST":

        if request.form['name']=="":
            empty_error = True
        else:
            conn = pymysql.connect(
            host='mysql',
            user='houpr',
            password=database_password__,
            database='IoT'
            )
            cursor = conn.cursor()
            sql = "select name from device where name=%s"
            cursor.execute(sql, request.form['name'])
            res = cursor.fetchone()
            if res==None:
                not_exist_error = True
            else:
                sql = "delete from device where name=%s"
                cursor.execute(sql, request.form['name'])
                conn.commit()
                success = True
                get_devices()
                session.clear()
        
        if not_exist_error:
            session['name'] = request.form['name']

    return render_template("delete.html", home = usr_name, member=devices, result=devices, empty_error=empty_error, session=session, not_exist_error=not_exist_error, success=success)

id = ""
@app.route('/modify.html', methods=['GET', 'POST'])
def modify():
    global id
    empty_error = False
    price_error = False
    success = False
    not_found = False
    name_duplicate_error = False
    search_first = False
    get_devices()
    if request.method == "POST":
        if request.form["action"] == "Submit":
            insert = True
            if request.form['category']=="" or request.form['name']=="" or request.form['price']=="":
                empty_error = True
                insert = False
            elif not is_positive_number(request.form['price']):
                price_error = True
                insert = False
            if insert:
                conn = pymysql.connect(
                    host='mysql',
                    user='houpr',
                    password=database_password__,
                    database='IoT'
                    )
                cursor = conn.cursor()
                sql = "select id from device where name = %s"
                cursor.execute(sql, request.form['name'])
                res = cursor.fetchone()
                if id == "":
                    search_first = True
                    return render_template("modify.html", home = usr_name, member=devices, result=devices, empty_error = empty_error, price_error = price_error, not_found = not_found, session = session, success=success, name_duplicate_error = name_duplicate_error, search_first = search_first)
                if res!=None and int(res[0]) != int(id):
                    name_duplicate_error = True
                else:
                    sql = "UPDATE device SET category = %s, price = %s, name = %s WHERE id = %s"
                    cursor.execute(sql,(request.form['category'],request.form['price'],request.form['name'], id))
                    conn.commit()
                    success = True
                    get_devices()
                    session.clear()

        elif request.form["action"] == "Search":
            if request.form['id']!='':
                get_devices()
                conn = pymysql.connect(
                    host='mysql',
                    user='houpr',
                    password=database_password__,
                    database='IoT'
                    )
                cursor = conn.cursor()
                sql = "select category, price, name from device where id = %s"
                cursor.execute(sql, request.form['id'])
                res = cursor.fetchall()
                if res!=():
                    res = res[0]
                    session['category'] = res[0]
                    session['name'] = res[2]
                    session['price'] = res[1]
                    id = request.form['id']
                else:
                    not_found = True
                    session['id'] = ""
                    session['category'] = ""
                    session['name'] = ""
                    session['price'] = ""
    else:
        if empty_error or price_error:
            session['category'] = request.form['category']
            session['name'] = request.form['name']
            session['price'] = request.form['price']
        else:
            session['category'] = ""
            session['name'] = ""
            session['price'] = ""

    return render_template("modify.html", home = usr_name, member=devices, result=devices, empty_error = empty_error, price_error = price_error, not_found = not_found, session = session, success=success, name_duplicate_error = name_duplicate_error, search_first = search_first)


@app.route('/')
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        global usr_name
        usr_name = request.form['name']
        password = request.form['password']
        res = deal_login(usr_name, password)
        if res==0:
            return redirect(url_for('index'))
        elif res==1:
            return render_template('login.html', error1=True)
        else:
            return render_template('login.html', error2=True)
    return render_template('login.html')


def deal_login(name, password):

    conn = pymysql.connect(
        host='mysql',
        user='houpr',
        password=database_password__,
        database='IoT'
        )
    cur = conn.cursor()
    sql = 'select password from users where name=\'{}\''.format(name)
    sql_return = cur.execute(sql)
    if sql_return == 0:
        # the user does not exist
        return 2
    else:
        res = cur.fetchall()
        for r in res:
            if r[0] == password:
                return 0    # correct
    return 1 # wrong password  

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        res = deal_register(name, email, password)
        if res == 1:
            return render_template('register.html', error1=True)
        elif res==2:
            return render_template('register.html', error2=True)
        elif res==3:
            return render_template('register.html', error3=True)
        else:
            return redirect(url_for('login'))
    return render_template('register.html')


def deal_register(name, email, password):
    if len(name) == 0 or len(email) == 0 or len(password) == 0:
        return 1
    elif len(name) < 6 or len(password) < 6:
        return 2
    conn = pymysql.connect(
        host='mysql',
        user='houpr',
        password=database_password__,
        database='IoT'
        )
    cur = conn.cursor()
    sql = 'select * from users where name=\'{}\' and password=\'{}\''.format(name, password)
    num = cur.execute(sql)
    if num!=0:
        return 3
    sql = 'insert into users values(%s,%s,%s)'
    sql_return = cur.execute(sql, (name, email, password))
    conn.commit()
    return 0

@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    if request.method=='POST':
        conn = pymysql.connect(
            host='mysql',
            user='houpr',
            password=database_password__,
            database='IoT'
        )
        cur = conn.cursor()

        name_forget = request.form['name']
        email_forget = request.form['email']
        sql = 'select * from users where name=\'{}\' and email=\'{}\''.format(name_forget, email_forget)
        num = cur.execute(sql)
        if num==0:
            return render_template('forgot-password.html', error=True)
        else:
            return redirect(url_for('reset_password', **{'name': name_forget, 'email': email_forget}))
    return render_template('forgot-password.html')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    empty_error = False
    invalid_pass = False
    global name_forget
    if request.method=='GET':
        name_forget = request.args.get('name')
        email_forget = request.args.get('email')
    if request.method=='POST':
        password1 = request.form['password1']
        password2 = request.form['password2']
        if password1 == "" or password2 == "" or len(password1) < 6:
            empty_error = True
            return render_template('reset_password.html', empty_error = empty_error)
        name = name_forget
        name_forget = ''
        if password1 == password2:
            conn = pymysql.connect(
                host='mysql',
                user='houpr',
                password=database_password__,
                database='IoT'
            )
            cur = conn.cursor()
            sql = 'select * from users where name=\'{}\' and password=\'{}\''.format(name, password1)
            num = cur.execute(sql)
            if num!=0:
                invalid_pass = True
                return render_template('reset_password.html', empty_error = empty_error, invalid_pass = invalid_pass)
            sql='update users set password=\'{}\' where name=\'{}\''.format(password1, name)
            cur.execute(sql)
            conn.commit()
            return redirect(url_for('login'))

    return render_template('reset_password.html', empty_error = empty_error, invalid_pass = invalid_pass)

def fetch_data_from_db():
    conn = pymysql.connect(
                host='mysql',
                user='houpr',
                password=database_password__,
                database='IoT',
                autocommit=False
            )
    cur = conn.cursor()
    sql_query = "SELECT id, timestamp, lng, lat, info, value, alert FROM data ORDER BY id, timestamp"
    try:
        cur.execute(sql_query)
        result = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(result, columns=columns)
        return df
    finally:
        conn.close()

@app.route("/map_total.html")
def map_total():
    get_devices()

    # Fetch data from the database
    df = fetch_data_from_db()

    # Create the map
    m = folium.Map(location=[30.3, 120.2], zoom_start=10)
    root = folium.FeatureGroup(name = "Enable")
    m.add_child(root)

    colors = ['darkpurple', 'orange', 'black', 'green', 'cadetblue', 'purple', 'pink', 'darkblue', 'darkred']

    # Create a feature group for each device
    groups = []
    for device_id, device_data in df.groupby('id'):
        target_name = next((device['name'] for device in devices if device['id'] == device_id), None)
        feature_group = plugins.FeatureGroupSubGroup(root, f"Device {device_id}: {target_name}")
        m.add_child(feature_group)
        groups.append(feature_group)

        # Add coordinates to each feature group
        coordinates = device_data.apply(lambda row: [row['lat'], row['lng']], axis=1).tolist()

        # Add Markers for each coordinate
        for index, row in device_data.iterrows():
            lat, lng = row['lat'], row['lng']
            info, value, alert = row['info'], row['value'], row['alert']

            # Use a different color for markers when alert is 1
            color = 'red' if alert == 1 else colors[device_id % len(colors)]
            
            # Create a popup with all information
            popup_content = f"<strong>Device ID:</strong> {device_id}<br>" \
                            f"<strong>Longitude:</strong> {lng}<br>" \
                            f"<strong>Latitude:</strong> {lat}<br>" \
                            f"<strong>Timestamp:</strong> {row['timestamp']}<br>" \
                            f"<strong>Info:</strong> {info}<br>" \
                            f"<strong>Value:</strong> {value}<br>" \
                            f"<strong>Alert:</strong> {alert}"

            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(color=color),
            ).add_to(feature_group)

        # Add PolyLine to show the trajectory
        folium.PolyLine(
            locations=coordinates,
            color=colors[device_id % len(colors)],  
            weight=3,
            tooltip=f"Device {device_id} trajectory",
        ).add_to(feature_group)

    
    folium.TileLayer(tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}', name='Gaode street map', attr='Gaode street map').add_to(m)
    folium.TileLayer(tiles='http://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}', name='Gaode satellite map', attr='Gaode satellite map').add_to(m)

    folium.LayerControl(auto_add = False).add_to(m)

    plugins.GroupedLayerControl(
        groups={'Select Device<br>(Single):': groups},
        collapsed=True,
    ).add_to(m)

    plugins.GroupedLayerControl(
        groups={'Select Device<br>(Multiple):': groups},
        collapsed=True,
        exclusive_groups=False
    ).add_to(m)
    
    return render_template('map_total.html', member=devices, home = usr_name, map_html=m.get_root().render())