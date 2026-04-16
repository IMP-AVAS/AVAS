import os
from utils.tool import format_output
def get_errordata(**item):

    project_path = item['projectPath']
    err_path = os.path.join(project_path, "OutputFile", "tmp", "errordata.log")

    #判断文件是否存在
    if os.path.exists(err_path):
        error_exist = False
        with open(err_path, 'r', encoding="UTF-8") as file:
            text = file.read()
            if text.strip():  # 去除空格和换行后仍有内容
                error_exist = True
            else:
                error_exist = False

        if error_exist:
            kwargs = {"errorInfo": text,}
        else:
            kwargs = {"errorInfo": ""}


    else:
    #如果文件不存在,证明还没有模拟完
        kwargs = {"errorInfo": ""}

    return kwargs



if __name__ == '__main__':
    item = {
        "projectPath": r"C:\\Users\\anxin\\Desktop\\test_schedule\\cafe_avas"
    }
    res = get_errordata(**item)
    print(res)