from hpc.stop_job import stop_job
from hpc.submit_job import submit_job


def run_hpc(item):
    #输入格式
    # item = {
    #     "projectPath": aa ,
    # }
    item = {"projectPath": item["projectPath"]}

    res = submit_job(**item)
    return res
    #返回
    #{'code': 0,
    # 'data': {
    # 'msg': 'success',
    # 'jobInfo': {'projectPath': 'C:\\Users\\anxin\\Desktop\\test_schedule\\cafe_avas',
    # 'jobName': 'AVAS56',
    # 'jobId': 111}
    # }
    # }

def stop_hpc(item):
    # item = {
    #     'jobId': 111
    # }
    res = stop_job(**item)

    print(res)
    return res
    #返回
    #{'code': 0, 'data': {'msg': 'success', 'jobStatus': []}}

