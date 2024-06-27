from django.shortcuts import render
from datetime import datetime,timedelta,date
from django.db import connection
import time
import random

curr_dateTime = datetime.now()
curr_Time = datetime.now().strftime("%H:%M:%S")
curr_date = datetime.today().strftime("%Y-%m-%d")
cursor = connection.cursor()
veh = '0'
global skey 
skey = ''
global dic
dic = {}
global l
l = [0,0]


def test(request):
    #  return render(request,'out.html')   
    for i in range(304,351):
        cursor.execute("insert into available_slots values(%s)",[i])

def start(request):
    cursor.execute('''select count(*) from available_slots where avail_slots between 200 and 360''')
    a = cursor.fetchone()
    cursor.execute('''select count(*) from available_slots where avail_slots  between 100 and 160''')
    b = cursor.fetchone()

    global l
    l[0] = a[0]
    l[1] = b[0]
    print(l)
    if(a[0] == 0 and b[0] == 0):
        param = {'A' : 'FULL','B' : 'FULL'}
    elif(a[0] == 0):
        param = {'A' : 'FULL','B' : b[0]}
    elif(b[0] == 0):
        param = {'A' : a[0],'B' : 'FULL'}
    else :
        param = {'A' : a[0],'B' : b[0]}
    return render(request,'start.html',param)
    


def index(request):
    global l
    if(l[0] == 0 and l[1] == 0):
        param = {'A' : 'FULL','B' : 'FULL','flag' : 1,'alert' : 'ALL SLOTS ARE FULL'}
        return render(request,'start.html',param)
    return render(request,'index.html')


def parkInfo(request):
    name = request.POST.get('name','default')
    name = name.upper()
    num = request.POST.get('reg_no','XX00XX0000')
    num = num.upper()
    vehicle = request.POST.get('wheel','0')
    
    global l
    if(l[0] == 0 and vehicle == '4'):
        param = {'A' : 'FULL','B' : l[1],'flag' : 1,'alert' : 'CAR SLOTS ARE FULL'}
        return render(request,'start.html',param)
    if(l[1] == 0 and vehicle == '2'):
        param = {'A' : l[0],'B' : 'FULL','flag' : 1,'alert' : 'BIKE SLOTS ARE FULL'}
        return render(request,'start.html',param)


    global veh 
    veh = vehicle
    phone = request.POST.get('phone',000000)
    curr_dateTime = datetime.now()
    global dic
    key()
    global skey
    slot_no,floor = SF(vehicle)
    dic = {'name' : name,'num' : num, 'vehicle' : vehicle,'phone' : phone,'slot':slot_no, 'floor':floor}

    print(skey,num)
    if vehicle == '4':
        param = {'cus_name' : name, 'num' : num, 'Time' : curr_dateTime,'slot_no' : slot_no, 'floor' : floor, 'key' : skey}
        return render(request,'parkInfocar.html',param)
    if vehicle == '2':
        param = {'cus_name' : name, 'num' : num, 'Time' : curr_dateTime,'slot_no' : slot_no, 'floor' : floor, 'key' : skey}
        return render(request,'parkInfobike.html',param)


def success(request):
    global dic
    insertquery(dic["name"],dic['num'],dic['vehicle'],dic['phone'],dic['slot'],dic['floor'])
    if veh == '4':
        return render(request,'charges_car.html')
    else:
        return render(request,'charges_bike.html')


def out(request):
    flag = 0
    param = {'alert' : 'Make sure u already checked In', 'flag' : flag}
    return render(request,'out.html',param)

def pay(request):
    reg_no = request.POST.get('reg_no','000')
    reg_no = reg_no.upper()
    key = request.POST.get('key','000000')
    matchfound = key
    cursor.execute('''select cust_id 
                    from customer c,vehicle v, parking p,timing t
                    where c.veh_id = v.veh_id and v.reg_no = %s and v.parking_id = p.park_id and p.timing_id = t.time_id and date_in = %s and t.departure_time = "%s"''',[reg_no,curr_date,00])
    has = cursor.fetchone()
    if has:
        cursor.execute('''select secret_key
                                from customer where cust_id = %s''',[has[0]])
        same = cursor.fetchone()
        matchfound = same[0]
        print(same[0])

    if has and (key == same[0]):
        found = has[0]

        cursor.execute('''select t.time_id
                        from customer c, vehicle v, parking p, timing t
                        where c.cust_id = %s and c.veh_id = v.veh_id and v.parking_id = p.park_id and p.timing_id = t.time_id''',[found])
        t = cursor.fetchone()
        time_id = t[0]

        curr_Time = datetime.now().strftime("%H:%M:%S")
        cursor.execute('''update timing set departure_time = %s where time_id = %s''',[curr_Time,time_id])
        
        cursor.execute('''select p.slot_no
                        from customer c, vehicle v, parking p
                        where c.cust_id = %s and c.veh_id = v.veh_id and v.parking_id = p.park_id''',[found])
        s = cursor.fetchone()
        slot_no = s[0]
        cursor.execute('''delete from booked_slots where book_slots = %s''',[slot_no])
        cursor.execute('''insert into available_slots values(%s)''',[slot_no])

        cursor.execute('''select c.cust_name, t.arrival_time, t.departure_time
                        from customer c, vehicle v, parking p, timing t
                        where c.cust_id = %s and c.veh_id = v.veh_id and v.parking_id = p.park_id and p.timing_id = t.time_id''',[found])
        temp = cursor.fetchone()

        t1 = datetime.strptime(str(temp[1]),"%H:%M:%S")
        t2 = datetime.strptime(str(temp[2]),"%H:%M:%S")
        diff = abs(t2 - t1)
        tsec = diff.total_seconds()
        tot_time = time.strftime("%H:%M:%S",time.gmtime(tsec))
        if tsec > 10800:
            fare = (tsec//60)*1 if veh == '4' else (tsec//60)*0.667
        else:
            fare = (tsec//60)*0.833 if veh == '4' else (tsec//60)*0.5
        

        fare = fare + 20
        fare = "{0:.3f}".format(fare) 
        cursor.execute('''select max(ticket_id) from ticket_generation''') 
        temp1 = cursor.fetchone()
        tck_id = temp1[0] + 1
        cursor.execute('''insert into ticket_generation values(%s,%s,%s,%s,%s,%s,%s)''',[tck_id, found, reg_no, t1, t2, curr_date, fare])
        
        
        curr_dateTime = datetime.now()
        param = {'cust_name' : temp[0], 'curr_dt' : curr_dateTime, 'arr_time' : temp[1], 'dep_time' : temp[2], 'totalTime' : tot_time, 'fare' : fare}
        return render(request,'pay.html',param)
    else:
        flag = 1
        if key == matchfound:
            param = {'alert' : 'NO VEHICLE FOUND', 'flag' : flag}
            flag = 0
            return render(request,'out.html',param)
        else:
            param = {'alert' : 'KEY DOESNOT MATCH', 'flag' : flag}
            flag = 0
            return render(request,'out.html',param)


def final(request):
    return render(request,'final.html')

def SF(vehicle):
    veh_type = 'car' if vehicle == '4' else 'Bike'
    if veh_type == 'car' :
        cursor.execute('''select * from available_slots where avail_slots>%s''',[150])
        s = cursor.fetchone()
        slot_no = int(s[0])
        floor = 3 if slot_no > 250 else 2
    else :
        cursor.execute('''select * from available_slots where avail_slots<%s''',[160])
        s = cursor.fetchone()
        slot_no = int(s[0])
        floor = 1

    return slot_no,floor

def insertquery(name,reg_num,vehicle,phone,slot_no,floor):
    print(name,reg_num,vehicle,phone,slot_no,floor)
    cursor.execute('''select max(cust_id) from customer''') 
    temp1 = cursor.fetchone()
    cust_id = temp1[0] + 1

    cursor.execute('''select max(veh_id) from vehicle''') 
    temp2 = cursor.fetchone()
    veh_id = temp2[0] + 1

    cursor.execute('''select max(park_id) from parking''') 
    temp3 = cursor.fetchone()
    park_id = temp3[0] + 1

    cursor.execute('''select max(time_id) from timing''') 
    temp4 = cursor.fetchone()
    time_id = temp4[0] + 1

    global skey
    sqlquery = 'insert into customer values(%s,%s,%s,%s,%s);' 
    cursor.execute(sqlquery,[cust_id,name,phone,veh_id,skey])

    veh_type = 'CAR' if vehicle == '4' else 'BIKE'
    sqlquery = 'insert into vehicle values(%s,%s,%s,%s);' 
    cursor.execute(sqlquery,[veh_id,reg_num,veh_type,park_id])

    
    cursor.execute('''delete from available_slots where avail_slots = %s''',[slot_no])
    cursor.execute('''insert into booked_slots values(%s)''',[slot_no])

    sqlquery = 'insert into parking(park_id,slot_no,timing_id) values(%s,%s,%s);' 
    cursor.execute(sqlquery,[park_id,slot_no,time_id])

    cursor.execute('''call FloorNum(%s,%s);''',[slot_no,park_id])

    curr_Time = datetime.now().strftime("%H:%M:%S")
    sqlquery = 'insert into timing values(%s,%s,%s,%s);' 
    cursor.execute(sqlquery,[time_id,curr_Time,00,curr_date])

def key():
    l = [0,1,2,3,4,5,6,7,8,9]
    a = ['A','S','D','F','G','H','J','K','L','Q','W','E','R','T','Y','U','I','O','P','Z','X','C','V','B','N','M']
    s = ['@','#','*','&','$','%']
    global skey
    skey = str(random.choice(l)) + random.choice(a) + random.choice(s) + str(random.choice(l)) + random.choice(s) + random.choice(a)
