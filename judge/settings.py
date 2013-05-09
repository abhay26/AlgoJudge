# Defining Constants

# The location on your system where AlgoJudge folder is placed. It is required to serve static content.
SYS_ROOT   = "/var/www/oj/"

MYSQL_HOST = "localhost"           # Host address of MySQL server. Maybe "localhost" or an IP.
MYSQL_PORT = "3306"                # The port on which MySQL server is listening. The default for MySQL is 3306
MYSQL_USER = "root"            # USERNAME to which you have granted the database access.
MYSQL_PASS = "gta123"            # PASSWORD for the abode user.
MYSQL_DB   = "algo_judge"                  # The database to use for OJ.


# Language Support [ Just remove all the corresponding entries in following variables to disable submission in them ]
LANGUAGES = ["GNU G++ 4.3","GNU GCC 4.3","OPENJDK-6-JDK","PYTHON 2.7"]
LANG_NICK = ["CPP","C","JAVA","PYTHON"]
LANG_EXT  = ["cpp","c","java","py"]
TIME_FACTOR = [1,1,2,2]                           # Time limit are multiple by this factor for corresponding language

# Add a entry for each problem
PROBLEMS_ID = ["A+B", "A-B"]                             # ID of problem.
PROBLEMS_NAME = ["Add two given numbers", "Substract two given numbers"]         # Name of problem.
PROBLEMS_PAGE = ["ADD.html", "SUB.html"]                      # File which contains the description of this corresponding entry. It should exists in OJ folder.
PROBLEMS_SCORE = [1, 1]                            # Total score attainable for corresponding problem
MAX_SUBMISSION = [500, 500]                              # Max. Submission allowed for corresponding problem
TIME_LIMITS = [1, 1]

TIME_DIFF = 60                                    # Minimum gap in seconds between two consecutive submission for same problem.

# Please stick to the time format. Time is in 24-hours format. And month short nick should be used.

startTime = "4 Jan 2009 16:15"                    # The time the contest start, evaluation starts and problems are visible.
endTime   = "10 Jan 2015 23:00"                   # The time contest ends, evaluation stops and submissions are freezed.
regTime   = "10 Jan 2013 23:00"	                  # The time when registration stops. TeamList is freezed.
