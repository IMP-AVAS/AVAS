
import subprocess
import uuid
import os
from utils.tool import format_output
from hpc.get_errordata import get_errordata
def get_jobstatus_in_hpc(**item):
    job_id = item['jobId']

    print("job_id", job_id)
    kwargs = {"jobStatus": "", "ifFinish": 1, "errorInfo": "",  "jobLogTitle": [], "jobLogData": []}

    result = subprocess.run(["squeue", "-j", str(job_id)], capture_output=True, text=True)

    lines = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]

    rows = [line.split() for line in lines]

    jobLogTitle = rows[0]
    if len(rows) == 0:
        raise Exception("the jobId not exist")
    elif len(rows) == 1:
        if_finish = 2
        errorInfo = get_errordata(**item)["errorInfo"]
        jobLogTitle = rows[0]
        jobLogData = []

    elif len(rows) == 2:
        if_finish = 1
        errorInfo = ""
        jobLogTitle = rows[0]
        jobLogData = rows[1]
    kwargs.update({"jobStatus": rows, "ifFinish": if_finish, "errorInfo": errorInfo,
                   "jobLogTitle": jobLogTitle, "jobLogData": jobLogData})

    output = format_output(**kwargs)
    return output


def get_jobstatus_in_windows(**item):
    kwargs = {"jobStatus": "", "ifFinish": 1, "errorInfo": "" }

    rows = [['JOBID', 'PARTITION', 'NAME', 'USER', 'ST', 'TIME', 'NODES', 'NODELIST(REASON)'],
        ['961397', 'cpup8', 'AVAS56', 'lizhongy', 'PD', '0:00', '1', '(Priority)']]

    project_path = item['projectPath']

    signa_path = os.path.join(project_path, "OutputFile", "signal.txt")
    with open(signa_path, 'r') as f:
        text = f.read()

    text = text.strip()
    if text == "1":
        status_list = rows
    elif text == "2":
        status_list = [rows[0]]
    else:
        status_list = [rows[0]]

    if_finish = 1
    if len(status_list) == 1:
        if_finish = 2
        errorInfo = get_errordata(**item)["errorInfo"]
        jobLogTitle = rows[0]
        jobLogData = []

    elif len(status_list) == 2:
        if_finish = 1
        errorInfo = ""
        jobLogTitle = rows[0]
        jobLogData = rows[1]


    kwargs.update({"jobStatus": rows, "ifFinish": if_finish, "errorInfo": errorInfo,
                   "jobLogTitle": jobLogTitle, "jobLogData": jobLogData})

    output = format_output(**kwargs)
    return output

if __name__ == '__main__':
    project_path = r"C:\Users\anxin\Desktop\test_schedule\cafe_avas"
    item = {"projectPath": project_path, "jobId": 11}
    result = get_jobstatus_in_windows(**item)
    print(result)

    # result = get_jobstatus_in_hpc(**item)
    # print(result)




