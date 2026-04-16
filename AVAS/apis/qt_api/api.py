import re
import sys

from fontTools.feaLib import location

from aftertreat.dataanalysis.percentemitt import PercentEmit
from utils.readfile import read_dst_fast
import os
import copy
from utils.tool import format_output
from utils.treat_directory import list_files_in_directory

from utils.iniconfig import IniConfig
from utils.inputconfig import InputConfig
import pandas as pd
from utils.beamconfig import BeamConfig
from apis.qt_api.judge_lattice import JudgeLattice
import global_varible
from dataprovision.beamparameter import DstParameter

def cal_beam_parameter(item):
    dst_path = item["dstPath"]
    kwargs = {}

    beam_parameter = {}

    if os.path.exists(dst_path):
        dst_res = read_dst_fast(dst_path)
        beam_parameter['particlerestmass'] = dst_res['basemassinmev']
        beam_parameter['current'] = dst_res['ib']
        beam_parameter['particlenumber'] = dst_res['number']
        beam_parameter['frequency'] = dst_res['freq']
        beam_parameter['kneticenergy'] = dst_res['kneticenergy']

        dst_obj = DstParameter(dst_path)
        dst_dict = dst_obj.get_parameter()

        item = {
            "ratio": 1,
            "picture_type": ["z1", "x1"],
            "dst_path": dst_path,
            "dst_dict": dst_dict,
        }
        obj = PercentEmit()

        pt = [["x", "x1"], ["y", "y1"], ["z", "z1"], ]

        twiss = []
        for i in pt:
            item["picture_type"] = i
            this_twiss = obj.get_percent_emit(item)
            twiss.append(this_twiss)


        beam_parameter['alpha_x'] = twiss[0][0]
        beam_parameter['beta_x'] = twiss[0][1]
        beam_parameter['emit_x'] = twiss[0][3]

        beam_parameter['alpha_y'] = twiss[1][0]
        beam_parameter['beta_y'] = twiss[1][1]
        beam_parameter['emit_y'] = twiss[1][3]

        beam_parameter['alpha_z'] = twiss[2][0]
        beam_parameter['beta_z'] = twiss[2][1]
        beam_parameter['emit_z'] = twiss[2][3]

        beam_parameter["readparticledistribution"] = ""
        beam_parameter["distribution_x"] = "GS"
        beam_parameter["distribution_y"] = "GS"

        demical_keys = [
            "particlerestmass", "kneticenergy", "alpha_x", "beta_x", "emit_x", "alpha_y", "beta_y", "emit_y",
            "alpha_z", "beta_z", "emit_z",
        ]
        for k, v in beam_parameter.items():
            if k in demical_keys:
                beam_parameter[k] = round(v, global_varible.decimals7)



    kwargs.update({'beamParams': copy.deepcopy(beam_parameter)})
    output = format_output(**kwargs)
    return output


def get_inputfile_path(item):
    # item = {"projectPath": "fdasf" }
    kwargs = {}
    input_path = os.path.join(item["projectPath"], "InputFile")
    kwargs.update({'inputFilePath': input_path})
    output = format_output(**kwargs)
    return output


# 获取上传位置
def get_upload_path(item):
    # item = {"projectPath": "fdasf", fileType, " "}
    kwargs = {}
    projectPath = item["projectPath"]
    fileType = item["fileType"]
    if fileType == "dst":
        upload_path = os.path.join(projectPath, "InputFile")
    elif fileType == "field":
        upload_path = os.path.join(projectPath, "InputFile", "field")
    kwargs.update({'uploadPath': upload_path})
    output = format_output(**kwargs)
    return output


# 得到模拟进度

def get_fieldname(item):
    #相对路径，没有后缀名， 去重
    kwargs = {}
    fieldPath = item["filePath"]
    if os.path.exists(fieldPath):
        all_files = list_files_in_directory(fieldPath, sort_by="mtime")
        suffix_list = ["edx", "edy", "edz", "bdx", "bdy", "bdz",
                       "bsx", "bsy", "bsz"
                       ]
        all_files = [i for i in all_files if i.split(".")[-1] in suffix_list]
        v = [i.split(r"/")[-1] for i in all_files]
        v = [i.split(".")[0] for i in v]
        field_name = list(set(v))
        kwargs.update({'fieldName': field_name})
        output = format_output(**kwargs)
    else:
        code = -1
        msg = f"FileNotFoundError: {fieldPath}"
        kwargs.update({'fieldName': []})
        output = format_output(code, msg=msg, **kwargs)
    return output


def get_bimap_name(item):
    #相对路径，没有后缀
    kwargs = {}
    bimapPath = item["filePath"] 
    if os.path.exists(bimapPath):
        all_files = list_files_in_directory(bimapPath)
        suffix_list = ["csv"
                       ]
        all_files = [i for i in all_files if i.split(".")[-1] in suffix_list]
        v = [i.split(r"/")[-1] for i in all_files]
        v = [i.split(".")[0] for i in v]
        bimap_name = list(set(v))
        kwargs.update({'bimapName': bimap_name})
        output = format_output(**kwargs)
    else:
        code = -1
        msg = f"FileNotFoundError: {bimapPath}"
        kwargs.update({'bimapName': []})
        output = format_output(code, msg=msg, **kwargs)
    return output


def get_fieldfile(item):
    #相对路径，有后缀
    kwargs = {}
    fieldpath = item["fieldPath"]
    if os.path.exists(fieldpath):
        all_files = list_files_in_directory(fieldpath, sort_by="mtime")
        suffix_list = ["edx", "edy", "edz", "bdx", "bdy", "bdz",
                       "bsx", "bsy", "bsz"
                       ]
        all_files = [i for i in all_files if i.split(".")[-1] in suffix_list]
        v = [i.split(r"/")[-1] for i in all_files]
        kwargs.update({'fieldFile': v})
        output = format_output(**kwargs)
    else:
        code = -1
        msg = f"FileNotFoundError: {fieldpath}"
        kwargs.update({'fieldFile': []})
        output = format_output(code, msg=msg, **kwargs)

    return output


def get_allfile_relative_path(item):
    #带后缀
    kwargs = {}
    default_item = {
        "filePath": None,
        "sort_by": "mtime"
    }
    default_item.update(item)

    fieldpath = default_item["filePath"]
    sort_by = default_item["sort_by"]

    if os.path.exists(fieldpath):
        all_files = list_files_in_directory(fieldpath, sort_by=sort_by)
        v = [i.split(r"/")[-1] for i in all_files]
        kwargs.update({'allFile': v})
        output = format_output(**kwargs)
    else:
        code = -1
        msg = f"FileNotFoundError: {fieldpath}"
        kwargs.update({'allFile': []})
        output = format_output(code, msg=msg, **kwargs)

    return output


def create_from_file_input_ini(item):
    # item的格式{“projectPath”： “path”}
    kwargs = {}

    input_obj = InputConfig()
    input_res = input_obj.create_from_file(item)
    # if input_res["code"] == -1:
    #     code = -1
    #     msg = input_res["data"]["msg"]
    #     kwargs.update({'inputiniParams': {}})
    #     output = format_output(code, msg=msg, **kwargs)
    #     return output

    ini_obj = IniConfig()
    ini_res = ini_obj.create_from_file(item)
    # if input_res["code"] == -1:
    #     code = -1
    #     msg = input_res["data"]["msg"]
    #     kwargs.update({'inputiniParams': {}})
    #     output = format_output(code, msg=msg, **kwargs)
    #     return output

    new_dic = {}
    new_dic.update(input_res["data"]["inputParams"])
    fieldSource_dic = {'fieldSource': ini_res["data"]["iniParams"]["project"]["fieldSource"],
                       "device": ini_res["data"]["iniParams"]["input"]["device"]
                       }
    new_dic.update(fieldSource_dic)

    kwargs.update({'inputiniParams': new_dic})
    output = format_output(**kwargs)
    return output


def write_to_file_input_ini(item, param):
    # item的格式{“projectPath”： “path”}
    # {'sim_type': 'mulp', 'scanphase': 1, 'spacecharge': 1, 'steppercycle': 50,
    #  'dumpperiodicity': 1, 'spacechargelong': None, 'spacechargetype': None,
    #  'scmethod': 'SPICNIC', 'fieldSource': '', "device": "", "outputcontrol_start": , "outputcontrol_grid": }
    kwargs = {}
    if param.get("fieldSource") == "thisProject":
        param["fieldSource"] = os.path.join(item["projectPath"], "InputFile", "field")

    input_param = copy.deepcopy(param)


    del input_param["fieldSource"]
    if input_param.get("device"):
        del input_param["device"]


    ini_param = {"project": {"fieldSource": param["fieldSource"]},
                 "input": {"sim_type": param["sim_type"], "device": param.get("device")},
                 }

    input_obj = InputConfig()
    input_res = input_obj.set_param(**input_param)
    if input_res["code"] == -1:
        code = -1
        msg = input_res["data"]["msg"]
        kwargs.update({'inputiniParams': {}})
        output = format_output(code, msg=msg, **kwargs)
        return output

    ini_obj = IniConfig()
    ini_res = ini_obj.set_param(**ini_param)
    if ini_res["code"] == -1:
        code = -1
        msg = ini_res["data"]["msg"]
        kwargs.update({'inputiniParams': {}})
        output = format_output(code, msg=msg, **kwargs)
        return output

    res1 = input_obj.write_to_file(item)
    res2 = ini_obj.write_to_file(item)
    new_dic = param
    kwargs.update({'inputiniParams': new_dic})
    output = format_output(**kwargs)
    return output


# def set_input_ini(item):
#     project_path =

def cal_mass(item):
    particletype = item["particletype"]
    nucleonnumber = item["nucleonnumber"]
    numofcharge = item["numofcharge"]

    kwargs = {}
    if particletype == "e-":
        kwargs.update({'particlerestmass': 0.511})
        output = format_output(**kwargs)
        return output
    elif particletype == "e+":
        kwargs.update({'particlerestmass': 0.511})
        output = format_output(**kwargs)
        return output

    script_directory = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在文件夹的绝对路径
    parent_directory = os.path.dirname(script_directory)  # 获取上级目录的路径
    parent_directory = os.path.dirname(parent_directory)  # 获取上级目录的路径
    mass_csv_path = os.path.join(parent_directory, "staticfile", "atomic_masses.csv")
    df = pd.read_csv(mass_csv_path, index_col=None)

    # 检测错误情况
    if 1:
        Element_lis = df["Element"].tolist()
        unique_lst = list(dict.fromkeys(Element_lis))
        if particletype not in unique_lst:
            code = -1
            msg = "This element doesn't exist"
            kwargs.update({'particlerestmass': ""})
            output = format_output(code, msg=msg, **kwargs)
            return output

        df_all_isotope = df[df["Element"] == particletype]
        all_A = df_all_isotope["A"].tolist()

        if nucleonnumber not in all_A:
            code = -1
            msg = (f"{particletype} does not have such an isotope. Its isotopes "
                   f"only exist with nucleon numbers of {all_A}.")
            kwargs.update({'particlerestmass': ""})
            output = format_output(code, msg=msg, **kwargs)
            return output

    df_filtered = df[(df["Element"] == particletype) & (df["A"] == nucleonnumber)]
    dict_rows = df_filtered.to_dict(orient='records')

    dict_rows = dict_rows[0]
    Mq = 931.4941024
    Me = 0.511

    def get_mass(Am, q):
        mass = Am * Mq - q * Me
        return mass

    Am = dict_rows["Am"]
    q = numofcharge
    particlerestmass = round(get_mass(Am, q), 5)
    kwargs.update({'particlerestmass': particlerestmass})
    output = format_output(**kwargs)
    return output


def get_atom(mode):
    # mode的选项， “common”， “all”
    kwargs = {}
    if mode == "common":
        v = ["H", "Cr", "Ar", "Ca", "Mn", "e+", "e-"]
        kwargs.update({'atomList': v})
        output = format_output(**kwargs)
        return output
    else:
        script_directory = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在文件夹的绝对路径
        parent_directory = os.path.dirname(script_directory)  # 获取上级目录的路径
        parent_directory = os.path.dirname(parent_directory)  # 获取上级目录的路径
        mass_csv_path = os.path.join(parent_directory, "staticfile", "atomic_masses.csv")
        df = pd.read_csv(mass_csv_path, index_col=None)

        Element_lis = df["Element"].tolist()
        unique_lst = list(dict.fromkeys(Element_lis))
        unique_lst.append("e+")
        unique_lst.append("e-")
        kwargs.update({'atomList': unique_lst})
        output = format_output(**kwargs)
        return output


def judge_if_is_avas_project(item):
    # item = {"projectPath": }
    # 这是一个初步的判断， 判断是否存在inputfile和outputfile
    project_path = item["projectPath"]
    inputfile_path = os.path.join(project_path, "InputFile")
    outputfile_path = os.path.join(project_path, "OutputFile")

    inputfile_exist = False
    outputfile_exist = False
    if os.path.exists(inputfile_path):
        inputfile_exist = True
    if os.path.exists(outputfile_path):
        outputfile_exist = True

    kwargs = {}
    if all([inputfile_exist, outputfile_exist]):
        kwargs.update({'projectPath': project_path})
        output = format_output(**kwargs)
    else:
        code = -1
        msg = f"{project_path} is not a  AVAS project"
        kwargs.update({'projectPath': project_path})
        output = format_output(code=code, msg=msg, **kwargs)
    return output

def get_file_choose_type(item):
    #item = {"ProjectPath":, "file_type"}
    default_item = {"projectPath": None, "fileType": None, "location": "out", "other_directory": None}
    default_item.update(item)

    file_type = default_item.get("fileType")
    project_path = default_item.get("projectPath")
    location = default_item.get("location")
    other_directory = default_item.get("other_directory")

    if location == "out":
        target_directory = os.path.join(project_path, "OutputFile")
    elif location == "in":
        target_directory = os.path.join(project_path, "InputFile")
    elif location == "other":
        target_directory = other_directory

    all_files = list_files_in_directory(target_directory)

    # print(all_files)
    can_choose_files = []
    if file_type.lower() == "errors_par":
        for i in all_files:
            v1 = re.findall("errors_par.txt", i)
            if len(v1)!= 0:
                can_choose_files.append(i)

    elif file_type.lower() == "density":
        for i in all_files:
            v1 = re.findall("density", i)
            if len(v1)!= 0:
                can_choose_files.append(i)


    elif file_type.lower() == "dst":
        for i in all_files:
            v1 = re.findall("dst", i)
            if len(v1)!= 0:
                can_choose_files.append(i)

    can_choose_files_relative = [i.split(r"/")[-1] for i in can_choose_files]

    kwargs = {}
    kwargs.update({'filesName': can_choose_files_relative})
    output = format_output(**kwargs)
    return output


def project_check(item):
    propject_path = item.get("projectPath")

    input_config = InputConfig()
    input_config.validate_run(item)

    # 检查beam文件
    beam_config = BeamConfig()
    beam_config.validate_run(item)

    ini_config = IniConfig()
    ini_info = ini_config.validate_run(item)

    ini_info = ini_info["data"]["iniParams"]
    base_mode = ini_info["input"]["sim_type"]
    err_mode = ini_info["error"]["error_type"]
    err_seed = ini_info["error"]["seed"]


    #检查lattice
    lattice_mulp_path = os.path.join(propject_path, "InputFile", "lattice_mulp.txt")
    lattice_obj = JudgeLattice(lattice_mulp_path)


    if base_mode == "mulp":
        if err_mode == "stat":
            lattice_obj.judge_lattice("stat_error")
        elif err_mode == "dyn":
            lattice_obj.judge_lattice("dyn_error")
        elif err_mode == "stat_dyn":
            lattice_obj.judge_lattice("stat_dyn_error")
        else:
            lattice_obj.judge_lattice("basic_mulp")


    output = format_output()
    return output

def get_all_files_in_project(item):
    #获取一个project下的所有后文件
    project_path = item["projectPath"]

    kwargs = {}
    kwargs["inputPath"] = "InputFile"
    kwargs["outputPath"] = "OutputFile"
    kwargs["projectPath"] = project_path
    kwargs["fileinInput"] = []
    kwargs["fileinOutput"] = []

    input_path = os.path.join(project_path, "InputFile")
    output_path = os.path.join(project_path, "OutputFile")

    item = {"filePath": input_path, "sort_by": "name"}
    file_in_input = get_allfile_relative_path(item)["data"]["allFile"]


    item = {"filePath": output_path, "sort_by": "name"}
    ori_output_files = get_allfile_relative_path(item)["data"]["allFile"]
    folders = ['error_adjust', "error_middle", 'error_output']
    folder_part = [f for f in ori_output_files if f in folders]
    file_part = [f for f in ori_output_files if f not in folders]

    kwargs["fileinInput"] = file_in_input
    kwargs["fileinOutput"] = file_part

    output = format_output(code=0, msg="success", **kwargs)


    return output

if __name__ == '__main__':
    # item = {"dstPath": r"C:\Users\anxin\Desktop\test_schedule\cafe_avas\InputFile\part_rfq.dst"}
    # res = cal_beam_parameter(item)
    # print(res)
    #
    # item = {"projectPath": r"D:\using\test_avas_qt\cafe_avas"}
    # res = get_all_files_in_project(item)
    # print(res)
    # pass
    # item = {
    # "particletype": "H",
    # "nucleonnumber": 10,
    # "numofcharge":1
    # }
    # # res = cal_mass(item)
    # # print(res)
    # item = {"projectPath": r"E:\using\test_avas_qt\test_ini"}
    # res = judge_if_is_avas_project(item)
    # print(res)



    # res = get_atom(mode="all")
    # print(res)


    # item = {"fieldPath": r"C:\Users\shliu\Desktop\field"}
    # res = get_fieldname(item)
    # print(res)

    dst_path = r"C:\Users\wangh\Desktop\phase_plot\outData_198.295500.dst"
    item = {"dstPath": dst_path}
    beam_parameter = cal_beam_parameter(item)
    print(beam_parameter)

    # path = r"C:\Users\shliu\Desktop\test_changdu"
    # item = {"projectPath": path}

    # param = {'sim_type': 'mulp', 'scmethod': 'FFT', 'scanphase': 1, 'spacecharge': 1, 'steppercycle': 100,
    #          'dumpperiodicity': 0, 'spacechargelong': 100, 'spacechargetype': 0, 'fieldSource': 'thisProject'}
    # write_to_file_input_ini(item, param)

    # res = create_from_file_input_ini(item)
    # print(res)


    # path = r"E:\using\test_avas_qt\cafe_avas\InputFile"
    # item = {"filePath": path }
    # res = get_bimap_name(item)
    # print(res)
    #
    # #
    # item = {"fieldPath": path }
    # res = get_fieldfile(item)
    # print(res)
    # projectPath = r"D:\using\test_avas_qt\cafe_avas"
    # #
    # # item = {"projectPath": projectPath, "fileType": "errors_par"}
    # # item = {"projectPath": projectPath, "fileType": "density"}
    # item = {"projectPath": projectPath, "fileType": "dst"}
    #
    # res = get_file_choose_type(item)
    # print(res)
    # project_path = r"D:\using\test_avas_qt\test_ini"
    # item = {
    #     "projectPath": project_path,
    # }
    # res = create_from_file_input_ini(item)
    # print(res)
    # param = {'sim_type': 'mulp', 'scanphase': 1, 'spacecharge': 1, 'steppercycle': 50,
    #  'dumpperiodicity': 1, 'spacechargelong': None, 'spacechargetype': None,
    #  'scmethod': 'SPICNIC', 'fieldSource': '', "device": "cpu"}
    # res = write_to_file_input_ini(item, param)