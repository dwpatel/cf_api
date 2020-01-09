import requests
import sys
from sets import Set

bad_verdicts = Set(["FAILED", "PARTIAL", "COMPILATION_ERROR", "RUNTIME_ERROR", "WRONG_ANSWER", "PRESENTATION_ERROR", "TIME_LIMIT_EXCEEDED", "MEMORY_LIMIT_EXCEEDED", "IDLENESS_LIMIT_EXCEEDED", "SECURITY_VIOLATED", "CRASHED", "INPUT_PREPARATION_CRASHED", "CHALLENGED", "SKIPPED", "TESTING", "REJECTED"])

class Contest:
    """
    id = unique integer that identifies the Contest
    type = integer (1 = Div1 or Div2),(3 = Div3),(4 = Global),(5 = other)
    url = https url (string) to the contest dashboard
    name = unicode (string?) name
    problem = set of problem indices - strings (e.x. A,B,C1, etc.)
    """
    def __init__(self, id, type, url, name, probs):
        self.id = id
        self.type = type
        self.url = url
        self.name = name
        self.problems = probs
        # contest["name"].encode('ascii', errors='ignore')


class Problem:
    def __init__(self, contestId, index, rating = 0):
        self.contestId = contestId
        self.index = index
        self.rating = rating
        self.solvedCount = 0


def parse_into_contest(contest, problemDict):
    # make url
    txt = "https://codeforces.com/contest/{}"
    raw_url = txt.format(contest["id"])

    # get type
    type = 0
    if ("Div. 1" in contest["name"] or "Div. 2" in contest["name"]):
        type = 1
    elif ("Div. 3" in contest["name"]):
        type = 3
    elif ("Global" in contest["name"] or "Hello" in contest["name"] or
             "Goodbye" in contest["name"]):
        type = 4
    else:
        type = 5

    # get problems
    probs = Set([])
    for key, value in problemDict.items():
        if (value.contestId == contest["id"]):
            probs.add(value.index)

    return Contest(contest["id"], type, raw_url, contest["name"], sorted(probs))


def get_parse_problems():
    # sending get request and saving the response as response object
    response = requests.get(url = "https://codeforces.com/api/problemset.problems?")
    if (response.status_code != 200):
        print("Failed in requesting problems list.")
        sys.exit(0)

    # extracting data in json format
    raw_data = response.json()
    if (raw_data["status"] != "OK"):
        print(raw_data["comment"])
        sys.exit(0)

    all_problems_raw = raw_data["result"]["problems"]
    all_problems_statistics_raw = raw_data["result"]["problemStatistics"]

    problemDict = {}
    for prob in all_problems_raw:
        prob_name = str(prob["contestId"]) + str(prob["index"])
        problemDict[prob_name] = Problem(prob["contestId"], prob["index"])
        if ("rating" in prob.keys()):
            problemDict[prob_name].rating = prob["rating"]

    for prob in all_problems_statistics_raw:
        prob_name = str(prob["contestId"]) + prob["index"]
        problemDict[prob_name].solvedCount = prob["solvedCount"]

    return problemDict


def parse_contest_list(problemDict):
    """
    return: List of Contest Objects
    """
    # sending get request and saving the response as response object
    response = requests.get(url = "https://codeforces.com/api/contest.list")
    if (response.status_code != 200):
        print("Failed in requesting contest list.")
        sys.exit(0)

    # extracting data in json format
    raw_data = response.json()
    if (raw_data["status"] != "OK"):
        print(raw_data["comment"])
        sys.exit(0)

    all_contests_raw = raw_data["result"]

    # parse raw data into contest objects
    all_contests = []
    for c_raw in all_contests_raw:
        c = parse_into_contest(c_raw, problemDict)
        all_contests.append(c)

    return all_contests


def create_div3_html(f, handle, all_div3, problemDict):
    """
    Auto-generates html file
    """

    for c in all_div3:
        # sending get request and saving the response as response object
        url_raw = "https://codeforces.com/api/contest.status?contestId={}&handle={}"
        response = requests.get(url_raw.format(c.id, handle))
        if (response.status_code != 200):
            print("Failed in getting request.")
            sys.exit(0)

        # extracting data in json format
        raw_data = response.json()
        if (raw_data["status"] != "OK"):
            print(raw_data["comment"])
            sys.exit(0)

        # organize all good submissions first
        good_subs = Set([])
        for sub in raw_data["result"]:
            if (sub["verdict"] == "OK"):
                good_subs.add(sub["problem"]["index"])

        # then, get all bad submissions
        bad_subs = Set([])
        for sub in raw_data["result"]:
            if (sub["problem"]["index"] not in good_subs and sub["verdict"] in bad_verdicts):
                bad_subs.add(sub["problem"]["index"])

        # finally, get not attempted problems
        no_subs = Set([])
        for prob in c.problems:
            if (prob not in good_subs and prob not in bad_subs):
                no_subs.add(prob)

        # generate html

        print_txt = "Working on {} ({})"
        print(print_txt.format(c.name, c.id))

        # start table row for this contest info
        f.write('<tr>')

        # write to html file a link to the contest
        contest_url_html = '<a href = "' + c.url + '">' + c.name + '</a><br>\n'
        f.write('<td>' + contest_url_html + '</td>')

        for prob in c.problems:
            prob_name = str(c.id) + str(prob)
            if (prob in good_subs):
                f.write('<td class="problem-good">' + '<div><b>' + prob + '</b></div>' + '<div class="moreinfo">' + str(problemDict[prob_name].rating) + '</div>' + '<div class="moreinfo">' + str(problemDict[prob_name].solvedCount) + '</div>' + '</td>')
            elif (prob in bad_subs):
                f.write('<td class="problem-bad">' + '<div><b>' + prob + '</b></div>' + '<div class="moreinfo">' + str(problemDict[prob_name].rating) + '</div>' + '<div class="moreinfo">' + str(problemDict[prob_name].solvedCount) + '</div>' + '</td>')
            else:
                f.write('<td>' + '<div><b>' + prob + '</b></div>' + '<div class="moreinfo">' + str(problemDict[prob_name].rating) + '</div>' + '<div class="moreinfo">' + str(problemDict[prob_name].solvedCount) + '</div>' + '</td>')

        # end table row
        f.write('</tr>')
