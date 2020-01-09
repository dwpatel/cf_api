import requests
import sys
from lib import *

# users = [
# "https://codeforces.com/api/user.info?handles=orangesTO",
# "https://codeforces.com/api/user.info?handles=limabeans"
# ]

# f = open('test.html','w')
# f.writelines(div3()[0])
# f.close()

# txt = u"{} (id = {}), (type = {}), \n(url = {})\n"
# print(txt.format(c.name, c.id, c.type, c.url))

# get all problems
problemDict = get_parse_problems()

# get all contests
all_contests = parse_contest_list(problemDict)

# get Div.3 contests
all_div3 = []
for c in all_contests:
    if (c.type == 3):
        all_div3.append(c)

# https://codeforces.com/api/contest.status?contestId=1287&handle=orangesTO
# get html file

handle = "orangesTO"
file_name = handle + "_div3.html"
f = open(file_name, 'w')
f.write('<table>')
f.write('<head>')
f.write('<link rel="stylesheet" type="text/css" href="main.css">')
f.write('</head>')
create_div3_html(f, handle, all_div3, problemDict)
f.write('</table')
f.close()
