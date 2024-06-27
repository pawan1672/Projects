from django.shortcuts import render
from django.db import connection
from datetime import datetime,timedelta,date

global back
gback = False
curr_date = datetime.today().strftime("%Y-%m-%d")
m = 'stabbers'
p = 'qwer02'
cursor = connection.cursor()

def index(request):
    global gback
    gback = False
    param = {'flag' : 0}
    return render(request,'admin.html',param)

def option(request):
    global gback
    param = {}
    user = request.POST.get('user','user')
    password = request.POST.get('password','pass')
    if not gback:
        if user != m or password != p:
            param['flag'] = 1
            return render(request,'admin.html',param)
    return render(request,'option.html')

def data(request):
    num = request.POST.get('90','0')
    param = {}
    cur = connection.cursor()

    #present day
    if num == '1':
        cursor.execute('''select t.ticket_id,c.cust_name,t.vehicle_regno,t.arrival_time,t.departure_time,t.date_out, t.Total_Fare
                        from customer c,ticket_generation t 
                        where c.cust_id = t.cust_id and t.ticket_id != %s and t.date_out = %s''',[50000,curr_date])

        cur.execute('''select sum(Total_Fare) 
                        from customer c,ticket_generation t 
                        where c.cust_id = t.cust_id and t.ticket_id != %s and t.date_out = %s''',[50000,curr_date])
    
    #previous day
    if num == '2':
        prev_date = (datetime.today()-timedelta(1)).strftime("%Y-%m-%d")
        cursor.execute('''select t.ticket_id,c.cust_name,t.vehicle_regno,t.arrival_time,t.departure_time,t.date_out, t.Total_Fare
                        from customer c,ticket_generation t 
                        where c.cust_id = t.cust_id and t.ticket_id != %s and t.date_out = %s''',[50000,prev_date])
        
        cur.execute('''select sum(Total_Fare)
                        from customer c,ticket_generation t 
                        where c.cust_id = t.cust_id and t.ticket_id != %s and t.date_out = %s''',[50000,prev_date])
    
    #this month
    if num == '3':
        this_month = date.today().replace(day=1)
        print(this_month)
        cursor.execute('''select t.ticket_id,c.cust_name,t.vehicle_regno,t.arrival_time,t.departure_time,t.date_out, t.Total_Fare 
                        from customer c,ticket_generation t 
                        where c.cust_id = t.cust_id and t.ticket_id != %s and t.date_out >= %s
                        order by t.date_out''',[50000,this_month])

        cur.execute('''select sum(Total_fare)
                        from customer c,ticket_generation t 
                        where c.cust_id = t.cust_id and t.ticket_id != %s and t.date_out >= %s''',[50000,this_month])
    
    #previous month
    if num == '4':
        prev_last_date = date.today().replace(day=1) - timedelta(days=1)
        prev_first_date = date.today().replace(day=1) - timedelta(days=prev_last_date.day)
        cursor.execute('''select t.ticket_id,c.cust_name,t.vehicle_regno,t.arrival_time,t.departure_time,t.date_out, t.Total_Fare
                        from customer c,ticket_generation t 
                        where c.cust_id = t.cust_id and t.ticket_id != %s and t.Date_out between %s and %s
                        order by t.date_out''',[50000,prev_first_date,prev_last_date])

        cur.execute('''select sum(Total_Fare)
                        from customer c,ticket_generation t 
                        where c.cust_id = t.cust_id and t.ticket_id != %s and t.Date_out between %s and %s''',[50000,prev_first_date,prev_last_date])

    #ALL
    if num == '5':
        cursor.execute('''select t.ticket_id,c.cust_name,t.vehicle_regno,t.arrival_time,t.departure_time,t.date_out, t.Total_Fare
                        from customer c,ticket_generation t 
                        where c.cust_id = t.cust_id and t.ticket_id != %s
                        order by t.date_out''',[50000])

        cur.execute('''select sum(Total_Fare)
                        from customer c,ticket_generation t 
                        where c.cust_id = t.cust_id and t.ticket_id != %s''',[50000])

    #check-in vehicles
    if num == '6':
        cursor.execute('''select c.cust_id, c.cust_name, v.reg_no, v.veh_type, p.slot_no, t.arrival_time, t.date_in
                        from customer c,vehicle v, timing t,parking p 
                        where t.departure_time = %s and c.veh_id = v.veh_id and v.parking_id = p.park_id and p.timing_id = t.time_id and t.time_id != %s''',[00,40000])


    if num == '7':
        return render(request,'basic/adinput.html')

    if num == '8':
        return render(request,'dateby.html')



    global gback
    gback = True
    data = cursor.fetchall()
    if num == '6':
        param = {'data' : data}
        return render(request,'data_in.html',param) 
    fare = cur.fetchone()
    fare = fare[0]
    fare = "{0:.3f}".format(fare) if fare else 0
    param = {'data' : data, 'fare' : fare}
    return render(request,'data.html',param)        


def spec_date(request):
    reg = request.POST.get('reg_no','default')
    reg = reg.upper()
    date = request.POST.get('date','datedefault')
    cur = connection.cursor()
    if date == 'datedefault' :
        cursor.execute('''select t.ticket_id,c.cust_name,t.vehicle_regno,t.arrival_time,t.departure_time,t.date_out, t.Total_Fare
                        from customer c,ticket_generation t 
                        where c.cust_id = t.cust_id  and t.vehicle_regno = %s''',[reg])

        cur.execute('''select sum(Total_Fare)
                        from customer c,ticket_generation t 
                        where c.cust_id = t.cust_id and t.vehicle_regno = %s''',[reg])
    
    else :
        cursor.execute('''select t.ticket_id,c.cust_name,t.vehicle_regno,t.arrival_time,t.departure_time,t.date_out, t.Total_Fare
                        from customer c,ticket_generation t 
                        where c.cust_id = t.cust_id  and t.date_out = %s''',[date])

        cur.execute('''select sum(Total_Fare)
                        from customer c,ticket_generation t 
                        where c.cust_id = t.cust_id and t.date_out = %s''',[date])

    global gback
    gback = True
    data = cursor.fetchall()
    fare = cur.fetchone()
    fare = fare[0]
    fare = "{0:.3f}".format(fare) if fare else 0
    param = {'data' : data, 'fare' : fare}
    return render(request,'data.html',param)
