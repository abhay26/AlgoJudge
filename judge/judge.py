import MySQLdb as db
import platform, re, os, sys, thread, time, urllib
from settings import *

# sudo apt-get install g++ openjdk-6-jdk

if '-judge' not in sys.argv:
    print "\nAlgoJudge"
    print "\nUse  -judge to start checking submissions"
    print
    sys.exit(0)

ioredirect = " 0<prob/input.txt 1>prob/output.txt 2>prob/error.txt"


running = 0
mypid = int(os.getpid())
languages = []


def file_read(filename):
    if not os.path.exists(filename): return "";
    f = open(filename, 'r'); d = f.read(); f.close(); return d.replace('\r', '')


def file_write(filename, data):
    f = open(filename, 'w'); f.write(data.replace('\r', '')); f.close()


def system():
    global languages
    if not os.path.isdir("prob"): os.mkdir("prob")
    if os.popen('find /usr/bin -name gcc').read() != '':
        languages.append('C')
    if os.popen('find /usr/bin -name javac').read() != '':
        languages.append('Java')
    if os.popen('find /usr/bin -name g++').read() != '':
        languages.append('C++')
    if os.popen('find /usr/bin -name python').read() != '':
        languages.append('Python')


def create(codefilename, language):
    if language not in ['C', 'CPP', 'JAVA']: return
    print "Compiling Code File..."
    result = None
    if language == 'C':
        os.system("gcc prob/" + codefilename + ".c -lm -lcrypt -O2 -pipe -ansi -DONLINE_JUDGE -w -o prob/" + codefilename + ioredirect)
        if not os.path.exists("prob/" + codefilename): result = "CE"
    elif language == 'CPP':
        os.system("g++ prob/" + codefilename + ".cpp -lm -lcrypt -O2 -pipe -DONLINE_JUDGE -o prob/" + codefilename + ioredirect)
        if not os.path.exists("prob/" + codefilename): result = "CE"
    elif language == 'JAVA':
        os.system("javac -g:none -Xlint -d prob prob/Main.java" + ioredirect)
        if not os.path.exists("prob/" + codefilename + ".class"): result = "CE"
    if not result:
        print "Code File Compiled!"
    else:
        print "Compile Error"
    return result


def execute(exename, language):
    global running, timediff
    starttime = time.time()
    running = 1
    if language == "CPP": os.system("prob/" + exename + ioredirect)
    elif language == 'C': os.system("prob/" + exename + ioredirect)
    elif language == 'JAVA': os.system("java -client -classpath prob Main" + ioredirect)
    elif language == 'PYTHON': os.system("python prob/" + exename + '.py' + ioredirect)
    running = 0
    endtime = time.time()
    timediff = endtime - starttime


def kill(langexec, lang):
    if lang == 'C': process = langexec
    elif lang == 'C++': process = langexec
    elif lang == 'Java': process = 'java'
    elif lang == 'python': process = 'python'
    for process in os.popen('ps -A | grep' + str(process)).read().split('\n'):
        pdata = process.split()
        pid = int(pdata[0]) if pdata else -1
        if pid in [-1, mypid]:
            continue
        os.system('kill -9 ' + str(pid))


if platform.system() != 'Linux':
    print "Error: Please run this script on Linux."
    sys.exit(0)

if os.path.exists('lock.txt'):
    print "Error: Run only 1 instance of this script on one system."
    sys.exit(0)
else:
    lock = open('lock.txt', 'w')

system()
if not languages:
    print 'Error: No Languages supported on this system!'
    sys.exit(0)

print 'Supported Languages: ' + str(languages) + '\n'

try:
    while True:
        print 'Connecting to server...'
        conn = db.connect(host=MYSQL_HOST, passwd=MYSQL_PASS, user=MYSQL_USER, db=MYSQL_DB)
        cursor = conn.cursor(db.cursors.DictCursor)
        print 'Connected to server...'
        print 'Searching un-judged problem...'
        cursor.execute("select sid, username, problemid, language, count, program, status from submission where status = 'Queued...' order by sid asc LIMIT 1")
        print "#"
        if cursor.rowcount > 0:
            work = cursor.fetchone()
            cursor.execute("""update submission set status='...' where sid=%s""", (work['sid']))
            print "Executing Submission ID %d.." % (work["sid"])
            while len(os.listdir('prob')) > 0:
                try:
                    for file in os.listdir('prob'): os.unlink('prob/' + file)
                except: pass
            print "Ready to Excecute.."
            result, timetaken, running = None, 0, 0
            if not result and work["language"] in 'CPP' and re.match(r"#include\s*['\"<]\s*[cC][oO][nN]\s*['\">]", work["program"]):
                print "Language C/C++ : #include<CON> detected."
                file_write("prob/error.txt", "Error : Including CON is not allowed.")
                result = "CE"
                timetaken = 0

            if not result and work["language"] == "PYTHON" and (
                re.match(r"import os", work["program"])):
                print "Suspicious code."
                file_write("prob/error.txt", "Error : Suspicious code.");
                result = "SC"; timetaken = 0

            if not result:
                if work['language'] == 'JAVA': codefilename = 'Main'
                else: codefilename = 'currentCode'
                codefile = open("prob/" + codefilename + "." + LANG_EXT[LANG_NICK.index(work["language"])], 'w')
                codefile.write(work['program'].replace('\r', ''))
                codefile.close()
                inputfile = open('test/' + work['problemid'] + '.in', 'r')
                inp = inputfile.read().replace('\r', '')
                file_write('prob/input.txt', inp)
                inputfile.close()
                print "Code & Input File Created."

            if not result:
                result = create(codefilename, work['language'])

            if not result:
                running = 0
                thread.start_new_thread(execute, (codefilename, work['language']))
                while running == 0: pass
                print 'Spawning Process...'
                for timetaken in range(TIME_LIMITS[PROBLEMS_ID.index(work['problemid'])]):
                    print "Timer : " + str(timetaken + 1) + "/" + str(TIME_LIMITS[PROBLEMS_ID.index(work['problemid'])])
                    if running == 0: break
                    time.sleep(1)
                if running == 0:
                    print "Process Complete"
                    timetaken = timediff
                else:
                    result = 'TLE'
                    timetaken = TIME_LIMITS[PROBLEMS_ID.index(work['problemid'])]
                    kill(codefilename, work['language'])
                    print "Time Limit Exceeded - Process Killed."
            output = ""
            if not result and file_read('prob/error.txt') != "":
                output = file_read('prob/output.txt')
                result = 'RTE'
            if not result:
                output = file_read('prob/output.txt')
                correct = file_read('test/' + work['problemid'] + '.out')
                file_write('prob/correct.txt', correct)
                if output == correct: result = "AC"
                elif re.sub(" +", " ", re.sub("\n *", "\n", re.sub(" *\n", "\n", output))) == re.sub(" +", " ", re.sub("\n *", "\n", re.sub(" *\n", "\n", correct))): result = "AC"
                elif(re.sub(r"\s", "", output) == re.sub(r"\s", "", correct)): result = "PE"
                else: result = "WA"
            print "Judging Complete"
            if result == 'AC' and work['status'] != 'AC':
                score = PROBLEMS_SCORE[PROBLEMS_ID.index(work['problemid'])]
                cursor.execute("UPDATE submission SET status='AC', score=%s WHERE sid=%s", (score, work['sid']))
            else:
                cursor.execute("UPDATE submission SET status=%s where sid=%s", (result, work['sid']))
            conn.commit()
            print 'Updated on Server'
            time.sleep(1)
        else:
            try: cursor.close()
            except: pass
            try: conn.close()
            except: pass
            print "Disconnected from Server.\n"

            #os.system('clear')
            print 'Currently no un-judged submissions on the server.\n'
            print 'Press Ctrl+C to terminate'
            time.sleep(1)
            countdown = 3
            while countdown > 0:
                #os.system('clear')
                print 'Contacting server in ' + str(countdown) + ' seconds...\n'
                print 'Press Ctrl+C to terminate'
                time.sleep(1)
                countdown -= 1

except db.Error as e:
    print "MySQL Error %d : %s\n" % (e.args[0], e.args[1])
except KeyboardInterrupt as e:
    print " Keyboard Interrupt Detected.\n"
except Exception as e:
    print "Exception : " + str(e) + '\n'

try:
    lock.close()
    os.unlink('lock.txt')
except:
    pass
print 'Released Lock\n'

print 'Judge stopped.'
