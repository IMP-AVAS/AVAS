from hpc.stop_job import stop_job
from hpc.submit_job import submit_job


def run_hpc(item):
    # item = {
    #     "projectPath": ,
    # }
    item = {"projectPath": r"C:\Users\shliu\Desktop\test422\cafe_avas"}

    res = submit_job(**item)
    return res

def stop_hpc(item):
    # item = {
    #     'jobId': 111
    # }
    res = stop_job(**item)

    print(res)
    return res

