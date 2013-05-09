import web
from web import form
from settings import *
import MySQLdb as DB
from time import localtime, strptime
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict


urls = (
    '/', 'index',
    '/index', 'index',
    '/about', 'about',
    '/register', 'register',
    '/teams', 'teams',
    '/submit', 'submit',
    '/status', 'status',
    '/problems', 'problems',
    '/rankings', 'rankings',
    '/(.+)', 'problem', 
    )
render = web.template.render('templates/')

app_header = '''<html>
	<head>
		<meta http-equiv="Cintent-Type" content="text/html; charset=iso-8859-1">
		<title>AlgoJudge</title>
		<link href="static/bootstrap.css" rel="stylesheet" media="screen" type="text/css"/>
		<link href="static/bootstrap.min.css" rel="stylesheet" media="screen" type="text/css"/>
		<link href="static/bootstrap-responsive.css" rel="stylesheet" media="screen" type="text/css"/>
		<link href="static/bootstrap-responsive.min.css" rel="stylesheet" media="screen" type="text/css"/>
	</head>
	<body>
		<div class="container">
			<div class="header">
				<h1>AlgoJudge</h1>
			</div>
			<div id="mainbody">
			    <div class='navbar navbar-inverse'>
                    <div class='navbar-inner nav-collapse' style="height: auto;">
                        <ul class="nav">
                            <li><a href="index">Home</a></li>
                            <li><a href="about">About</a></li>
                            <li><a href="register">Register</a></li>
                            <li><a href="teams">Teams</a></li>
						    <li><a href="submit">Submit</a></li>
						    <li><a href="status">Status</a></li>
						    <li><a href="problems">Problems</a></li>
						    <li><a href="rankings">Ranks</a></li>
                        </ul>
                    </div>
                </div>
	    '''

app_footer = '''
</div>
			<footer class="footer">
				<center>Designed By Team AlgoJudge</center>
			</footer>
		</div>
	</body>
</html>
             '''

class index:
    def GET(self):
        bodycontent = ""
        rules = "<h1>Rules</h1><ul><li>Submissions are allowed in all the GNU supported languages.</li><li>Individual participation is preferred.</li><li>Judges decision in any awkward situation that might arise will be final and unquestionalble.</li></ul>"
        bodycontent += rules
        return render.index(app_header, bodycontent, app_footer)
        
class about:
    def GET(self):
        bodycontent = ""
        about = "<h1>Uses</h1><ul><li>Can be used by the college to give programming assignments.</li><li>Can be used by the students to hold practice contests to prepare for ACM-ICPC</li><li>Can be used by students to hold contests during fests.</li></ul>"
        reason = "<h1>Why this judge?</h1><ul><li>Automated judging is amazing.</li><li>Students will actually write some CODE.</li><li>I wanted to learn some Web Technologies. :P</li></ul>"
        technologies = "<h1>What technologies used to build this?</h1><ul><li><emp><a href='http://webpy.org/'>web.py</a></emp></li><li><emp><a href='http://python.org/'>Python</a></emp></li><li><emp><a href='http://twitter.github.io/bootstrap/'>Bootstrap</a></emp></li></ul>"
        bodycontent += about + reason + technologies
        return render.index(app_header, bodycontent, app_footer)

vemail = form.regexp(r".*@.*", "must be a valid email address")

reg_form = form.Form(
            form.Textbox('username',
                form.Validator('Must be of size greater than 0', lambda i: len(i)), description='Username'),
            form.Password('password',
                form.Validator('Must be of size greater than 6', lambda i: len(i)>6), description='Password'),
            form.Password('password_again', description='Password Again'),
            form.Textbox('name',
                form.Validator('Must be of size greater than 0', lambda i: len(i)), description='Name'),
            form.Textbox('email', vemail, description='E-mail'),
            form.Textbox('college',
                form.Validator('Must be of size greater than 0', lambda i: len(i)), description='College'),
            validators = [form.Validator("Passwords didn't match.", lambda i: i.password == i.password_again)]
            )

class register:
    def GET(self):
        form = reg_form()
        return render.register(app_header, form, app_footer)
        
    def POST(self):
        form = reg_form()
        if not form.validates():
            return render.register(app_header, form, app_footer)
        else:
            username = form['username'].value
            password = hashlib.sha1(form['password'].value).hexdigest()
            name = form['name'].value
            email = form['email'].value
            college = form['college'].value
            conn = DB.connect(host=MYSQL_HOST,passwd=MYSQL_PASS,user=MYSQL_USER,db=MYSQL_DB)
            cursor = conn.cursor()
            try:
                cursor.execute("""insert into user(username,password,name,email,college) values (%s,%s,%s,%s,%s)""",(username,password,name,email,college))
                cursor.close()
                conn.commit()
                conn.close()
                raise web.seeother('/teams')
            except Exception as e:
                pass
            cursor.close()
            conn.commit()
            conn.close()
            raise web.seeother('/teams')

class teams:
    def GET(self):
        conn = DB.connect(host=MYSQL_HOST,passwd=MYSQL_PASS,user=MYSQL_USER,db=MYSQL_DB)
        cursor = conn.cursor()
        cursor.execute("select username,name,college from user")
        teamsTuples = cursor.fetchall()
        bodycontent = ""
        for teamsTuple in teamsTuples:
            bodycontent += "<tr><td>"+teamsTuple[0]+"</td>"
            bodycontent += "<td>"+teamsTuple[1]+"</td>"
            bodycontent += "<td>"+teamsTuple[2]+"</td></tr>"
        total = len(teamsTuples)
        cursor.close()
        conn.commit()
        conn.close()
        return render.teams(app_header, bodycontent, total, app_footer)

def valid_username(username, password):
    conn = DB.connect(host=MYSQL_HOST,passwd=MYSQL_PASS,user=MYSQL_USER,db=MYSQL_DB)
    cursor = conn.cursor()
    cursor.execute("select username from user where password=%s LIMIT 1", (hashlib.sha1(password).hexdigest()))
    userTuple = cursor.fetchone()
    cursor.close()
    conn.commit()
    conn.close()
    if userTuple:
        return True
    else:
        return False
        
class submit:
    submit_form  = form.Form(
            form.Textbox('username', description='Username', class_="input-xlarge", id="input01"),
            form.Password('password', description='Password'),
            form.Dropdown('problem', PROBLEMS_ID, description='Problem', id="select01"),
            form.Dropdown('language', LANG_NICK, description='Language'),
            form.Textarea('code', description='Paste Code', rows=3, class_="input-xlarge"), 
            validators = [form.Validator("Username or Password Wrong!", lambda i: valid_username(i.username, i.password)), form.Validator("Enter some code", lambda i: len(i.code))]        
            )
    def GET(self):
        form = self.submit_form()
        start = strptime(startTime, "%d %b %Y %H:%M")
        end = strptime(endTime, "%d %b %Y %H:%M")
        if localtime() < start:
            return render.index(app_header, "<div class='alert-message info'><a class='close' href='#'>&times;</a><p>Contest has not started!!</p></div>", app_footer)
        elif localtime() >= end:
            return render.index(app_header, "<div class='alert-message info'><a class='close' href='#'>&times;</a><p>Contest is over!!</p></div>", app_footer)
        return render.submit(app_header, form, app_footer)
    
    def POST(self):
        form = self.submit_form()
        if not form.validates():
            return render.submit(app_header, form, app_footer)
        else:
            username = form['username'].value
            problem = form['problem'].value
            language = form['language'].value
            code = form['code'].value
            count = 1
            try:
                conn = DB.connect(host=MYSQL_HOST,passwd=MYSQL_PASS,user=MYSQL_USER,db=MYSQL_DB)
                cursor = conn.cursor()
                cursor.execute("""select count, time from submission where problemid=%s and username=%s order by count desc""", (str(problem), username))
                subTuple = cursor.fetchone()
                flag = 0
                if subTuple:
                    problem_max_submission = MAX_SUBMISSION[PROBLEMS_ID.index(problem)]
                    if subTuple[0] == problem_max_submission:
                        flag = 1
                        return render.index(app_header, "<div class='alert-message error'><a class='close' href='#'>&times;</a><p>Not allowed to submit more than %s times for this problem!!</p></div>" % (int(problem_max_submission)), app_footer)
                    if datetime.timetuple(subTuple[1]+timedelta(seconds=TIME_DIFF)) > localtime():
                        flag = 1
                        return render.index(app_header, "<div class='alert-message error'><a class='close' href='#'>&times;</a><p>Wait for %s seconds between submissions!!</p></div>" % (TIME_DIFF), app_footer)
                    count = subTuple[0] + 1
                if not flag:
                    cursor.execute("""insert into submission (username, problemid, language, count, program) values (%s, %s, %s, %s, %s)""", (username, problem, language, count, code))
                    cursor.close()
                    conn.commit()
                    conn.close()
                raise web.seeother('/status')
            except:
                return render.index(app_header, "<div class='alert-message error'><a class='close' href='#'>&times;</a><p>Unknown Error Occured!!</p></div>", app_footer)
    
class status:
    def GET(self):
        conn = DB.connect(host=MYSQL_HOST,passwd=MYSQL_PASS,user=MYSQL_USER,db=MYSQL_DB)
        cursor = conn.cursor()
        cursor.execute("select sid, username, problemid, status from submission order by sid desc LIMIT 20")
        subTuples = cursor.fetchall()
        conn.commit()
        conn.close()
        bodycontent = ""
        for subTuple in subTuples:
            if subTuple[3] == 'AC':
                bodycontent += "<tr>"
                bodycontent += "<td><span class=\"label label-success\">"+str(subTuple[0])+"</span></td>"
                bodycontent += "<td><span class=\"label label-success\">"+str(subTuple[1])+"</span></td>"
                bodycontent += "<td><span class=\"label label-success\">"+str(subTuple[2])+"</span></td>"
                bodycontent += "<td><span class=\"label label-success\">"+str(subTuple[3])+"</span></td></tr>"
            elif subTuple[3] == 'Queued...':
                bodycontent += "<tr>"
                bodycontent += "<td><span class=\"label label-info\">"+str(subTuple[0])+"</span></td>"
                bodycontent += "<td><span class=\"label label-info\">"+str(subTuple[1])+"</span></td>"
                bodycontent += "<td><span class=\"label label-info\">"+str(subTuple[2])+"</span></td>"
                bodycontent += "<td><span class=\"label label-info\">"+str(subTuple[3])+"</span></td></tr>"
            else:
                bodycontent += "<tr>"
                bodycontent += "<td><span class=\"label label-warning\">"+str(subTuple[0])+"</span></td>"
                bodycontent += "<td><span class=\"label label-warning\">"+str(subTuple[1])+"</span></td>"
                bodycontent += "<td><span class=\"label label-warning\">"+str(subTuple[2])+"</span></td>"
                bodycontent += "<td><span class=\"label label-warning\">"+str(subTuple[3])+"</span></td></tr>"
        return render.status(app_header, bodycontent, app_footer)

class problems:
    def GET(self):
        total = len(PROBLEMS_ID)
        bodycontent = ""
        start = strptime(startTime,"%d %b %Y %H:%M")
        end = strptime(endTime,"%d %b %Y %H:%M")
        if localtime() >= start and localtime() < end:
            for i in range(total):
                bodycontent += "<tr>"
                bodycontent += "<td>" + PROBLEMS_ID[i] + "</td>"
                bodycontent += "<td><a href='%s'>%s</a></td>" % (PROBLEMS_PAGE[i],PROBLEMS_NAME[i])
                bodycontent += "<td>" + str(PROBLEMS_SCORE[i]) + "</td>"
                bodycontent += "<td>"+str(MAX_SUBMISSION[i]) + "</td>"
                bodycontent += "</tr>"
            return render.problems(app_header, bodycontent, app_footer)
        if localtime() < start:
            return render.index(app_header, "<div class='alert-message info'><a class='close' href='#'>&times;</a><p>Contest has not started!!</p></div>", app_footer)
        elif localtime() >= end:
            return render.index(app_header, "<div class='alert-message info'><a class='close' href='#'>&times;</a><p>Contest is over!!</p></div>", app_footer)

class problem:
    def GET(self, a):
        try:
            f = open('problem/' + a, 'r')
            prob = f.read()
            f.close()
        except Exception as e:
            return render.index(app_header, "<div class='alert-message info'><a class='close' href='#'>&times;</a><p>Problem not found!!!</p></div>", app_footer)
        return render.problem(app_header, prob, app_footer)

def cmp(a, b):
    if a[0] > b[0]:
        return -1
    elif a[0] < b[0] or (a[0]==b[0] and a[1] < b[1]):
        return 1
    elif a[0] == b[0]:
        return 0

class rankings:
    def GET(self):
        conn = DB.connect(host=MYSQL_HOST,passwd=MYSQL_PASS,user=MYSQL_USER,db=MYSQL_DB)
        cursor = conn.cursor(DB.cursors.DictCursor)
        cursor.execute("select username, problemid, score, count, time from submission where score > 0 order by sid desc")
        datas = cursor.fetchall()
        record = defaultdict(dict)
        for data in datas:
            record[data['username']][data['problemid']] = [data['score'], data['count'], data['time']]
        point_table = {user: len(record[user]) for user in record}
        time_table = {user: max([record[user][problem][2] for problem in record[user]]) for user in record}
        penalty_table = {}
        for user in record:
            total_penalty = 0
            for problem in record[user]:
                total_penalty += record[user][problem][1] - 1
            penalty_table[user] = total_penalty
        for user in point_table:
            for j in range(penalty_table[user]):
                time_table[user] = time_table[user] + timedelta(minutes=20)
        to_sort = zip(point_table.values(), time_table.values(), time_table.keys())
        to_sort.sort(cmp)
        bodycontent = ""
        for i, mytuple in enumerate(to_sort, 1):
            bodycontent += "<tr>"
            bodycontent += "<td><span class=\"badge badge-success\">" + str(i) + "</span></td>"
            bodycontent += "<td>" + str(mytuple[2]) + "</td>"
            bodycontent += "<td>" + str(mytuple[0]) + "</td></tr>"
        return render.rankings(app_header, bodycontent, app_footer)

if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()       
