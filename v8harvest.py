import os
import git
from fnmatch import fnmatch
import time
import datetime
import collections
import re

root = '.\\test\\mjsunit\\' # only search in /test/mjsunit
pattern = "regress-*" # all regress-* files
after_date = datetime.date(2015, 1, 1) # YY/MM/DD
before_date = datetime.date(2015, 12, 31) # YY/MM/DD

after_date = int(time.mktime(after_date.timetuple()))
before_date = int(time.mktime(before_date.timetuple()))

g = git.Git('C:\\Users\\kuqad\\Downloads\\V8Harvest\\v8') #path to repo, use gitpython because it's much much much faster than os.popen()
d = {}
for path, subdirs, files in os.walk(root):
    for name in files:
        if fnmatch(name, pattern):
            tmp = os.path.join(path, name)
            dt = int(g.log('-1', '--format=%ct', tmp)) # get commit date in unix time to sort
            if dt <= before_date and dt >= after_date:
            	d[dt] = tmp
            	print dt, tmp
    #         if len(d) > 3:
    #         	break
    # break

od = collections.OrderedDict(sorted(d.items(), reverse=True))

output = ""
format_string = '''
## **{path}**
**[Issue: {issue_link}]({issue_link})**\n
**[Commit: {commit_content}]({commit_link})**\n

Date(Commit): {date}\n
Code Review : [{code_review_link}]({code_review_link})\n
Regress : [{path}]({regress_link})\n
```{regress_code}```\n
'''
# print od
for p in od.items():
	path = p[1]
	log = g.log('-1', '--name-only', path)
	# print g.log('--', '--name-only', path)
	#parse commit hash
	commit_hash = re.search("commit .*\n", log)
	commit_hash = commit_hash.group(0).split()[1]

	commit_link = "https://chromium.googlesource.com/v8/v8/+/" + commit_hash
	commit_content = g.log('-1', "--pretty=format:%s", path)
	#parse crbug id
	bug_id = re.search("Bug: .*:.*\n", log)
	if bug_id != None:
		bug_id = bug_id.group(0)
	else:
		bug_id = ""
	chromium_bug_id = re.search("chromium:[0-9]+", bug_id)
	v8_bug_id = re.search("v8:[0-9]+", bug_id)

	issue_link = ""
	if(chromium_bug_id != None):
		issue_link = "https://crbug.com/" + chromium_bug_id.group(0).split(':')[1]
	elif(v8_bug_id != None):
		issue_link = "https://crbug.com/v8/" + v8_bug_id.group(0).split(':')[1]

	#parse date
	date = g.log('-1', "--pretty=format:%aD", path)

	#parse code_review_link
	code_review_link = re.search("Reviewed-on:.*", log)
	if code_review_link == None:
		code_review_link = ""
	else:
		code_review_link = code_review_link.group(0)[13:]

	#parse regress path and regress link
	regress_link = "https://chromium.googlesource.com/v8/v8/+/master/" + path.replace(".\\", "").replace("\\", "/")

	#parse regress code
	f = open(path, 'rb')
	regress_code = f.read()
	f.close()

	# print log
	# print issue_link
	# print commit_link
	# print date
	# print code_review_link
	# print path
	# print regress_link
	# print regress_code
	output += format_string.format(commit_content=commit_content, date=date, path=path.replace(".\\", ""), issue_link=issue_link, commit_link=commit_link, code_review_link=code_review_link, regress_link=regress_link, regress_code=regress_code)

f = open("output.md", "wb")
f.write(output)
f.close()