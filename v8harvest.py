import git
from fnmatch import fnmatch
import time
import datetime
import collections
import sys, os, re
from sys import argv
from tqdm import tqdm
import urllib.request

#---------------------------------------------------
# _log : Prints out logs for debug purposes
#---------------------------------------------------
def _log(s):
    print(s)

#---------------------------------------------------
# _log : Prints out Ascii Art
#---------------------------------------------------
def logo():
    print('\n')
    print(' ______     __  __     __     ______   ______        ______     ______     ______     __  __     ______     __   __   ')
    print('/\  ___\   /\ \_\ \   /\ \   /\__  _\ /\  ___\      /\  == \   /\  == \   /\  __ \   /\ \/ /    /\  ___\   /\ "-.\ \  ')
    print('\ \___  \  \ \  __ \  \ \ \  \/_/\ \/ \ \___  \     \ \  __<   \ \  __<   \ \ \/\ \  \ \  _"-.  \ \  __\   \ \ \-.  \ ')
    print(' \/\_____\  \ \_\ \_\  \ \_\    \ \_\  \/\_____\     \ \_____\  \ \_\ \_\  \ \_____\  \ \_\ \_\  \ \_____\  \ \_\\\\"\_\\ ')
    print('  \/_____/   \/_/\/_/   \/_/     \/_/   \/_____/      \/_____/   \/_/ /_/   \/_____/   \/_/\/_/   \/_____/   \/_/ \/_/')
    print('\n')
    print(" Grab the v8 Regression Commits!")
    print(" Đào Tuấn Linh & Jacob Soo")
    print(" Copyright (c) 2021\n")


pattern = "regress-*" # all regress-* files
iYear = 2020
after_date = datetime.date(iYear, 1, 1) # YY/MM/DD
before_date = datetime.date(iYear, 12, 31) # YY/MM/DD

after_date = int(time.mktime(after_date.timetuple()))
before_date = int(time.mktime(before_date.timetuple()))

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

def grab_commits(GitPath):
    g = git.Git(GitPath) #path to repo, use gitpython because it's much much much faster than os.popen()
    root = GitPath + "\\test\\mjsunit\\" # only search in /test/mjsunit
    d = {}
    global output
    for path, subdirs, files in tqdm(os.walk(root)):
        for name in files:
            if fnmatch(name, pattern):
                tmp = os.path.join(path, name)
                dt = int(g.log('-1', '--format=%ct', tmp)) # get commit date in unix time to sort
                if dt <= before_date and dt >= after_date:
                    d[dt] = tmp
                    dt = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt))
                    _log("[+] Datetime : {} Path : {}".format(str(dt), tmp))
    od = collections.OrderedDict(sorted(d.items(), reverse=True))
    for p in od.items():
        path = p[1]
        log = g.log('-1', '--name-only', path)
        # _log(g.log('--', '--name-only', path))
        # Parse commit hash
        commit_hash = re.search("commit .*\n", log)
        commit_hash = commit_hash.group(0).split()[1]

        commit_link = "https://chromium.googlesource.com/v8/v8/+/" + commit_hash
        commit_content = g.log('-1', "--pretty=format:%s", path)
        # Parse crbug id
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

        # Parse date
        date = g.log('-1', "--pretty=format:%aD", path)

        # Parse code_review_link
        code_review_link = re.search("Reviewed-on:.*", log)
        if code_review_link == None:
            code_review_link = ""
        else:
            code_review_link = code_review_link.group(0)[13:]

        # Parse regress path and regress link
        regress_link = "https://chromium.googlesource.com/v8/v8/+/master/" + path.replace(".\\", "").replace("\\", "/")

        # Parse regress code
        f = open(path, 'rb')
        regress_code = f.read()
        f.close()
        output += format_string.format(commit_content=commit_content, date=date, path=path.replace(".\\", ""), issue_link=issue_link, commit_link=commit_link, code_review_link=code_review_link, regress_link=regress_link, regress_code=regress_code)
    szFilename = str(iYear)+".md"
    f = open(szFilename, "wb")
    f.write(output.encode())
    f.close()

if __name__ == "__main__":
    logo()
    if (len(sys.argv) < 2):
        _log("[+] Usage: {} [path_to_v8]".format(sys.argv[0]))
        sys.exit(0)
    else:
        GitPath = sys.argv[1]
        grab_commits(GitPath)
