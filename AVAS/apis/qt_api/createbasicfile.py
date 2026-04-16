from utils.beamconfig import BeamConfig
from utils.inputconfig import InputConfig
from utils.iniconfig import IniConfig
from utils.latticeconfig import LatticeConfig
from utils.tool import format_output
import os

class CreatBasicFile():
    def __init__(self, project_path):
        self.project_path = project_path
        self.beam_path = os.path.join(project_path, "InputFile", "beam.txt")
        self.input_path = os.path.join(project_path, "InputFile", "input.txt")
        self.lattice_mulp_path = os.path.join(project_path, "InputFile", "lattice_mulp.txt")
        self.lattice_env_path = os.path.join(project_path, "InputFile", "lattice_env.txt")
        self.ini_path = os.path.join(project_path, "InputFile", "ini.ini")
        self.beam_info = {
            'readparticledistribution': "", 'numofcharge': 1, 'particlerestmass': 938.272, 'current': 0,
            'particlenumber': 5000, 'frequency': 100000000, 'kneticenergy': 1,
            "alpha_x": 0, "beta_x": 1, "emit_x": 0.1,
            "alpha_y": 0, "beta_y": 1, "emit_y": 0.1,
            "alpha_z": 0, "beta_z": 1, "emit_z": 0.1,
            "distribution_x": "GS", "distribution_y": "GS", "use_dst": 0, "beam_type": "notdc",
        }

        self.input_info = {
            "sim_type": "mulp", 'scmethod': "SPICNIC",  'spacecharge': 1, 'steppercycle': 10, 'dumpperiodicity': 0, "spacechargelong": 100, "spacechargetype": 0,
            "device":"cpu", "pchistogram_start": 0, "pchistogram_grid": 300, "longlimits_start": 0, "longlimits_phase": 0, "longlimits_energy": 0,
            "boundary": 0, "randomseed": 0
        }

        self.ini_info = \
            {"project": {"project_path": "undefined"},
            "lattice":{"length": 0},
             "input": {"sim_type": "mulp", "device": "cpu"},
             "match": {"cal_input_twiss": 0, "match_with_twiss": 0, "use_initial_value": 0},
             "error": {"error_type": "", "seed": 0, "if_normal": 1},
             }

    def create_basic_beam_file(self):
        beam_config = BeamConfig()

        beam_config.set_param(**self.beam_info)
        item = {"projectPath": self.project_path, }
        beam_config.write_to_file(item)

    def create_basic_input_file(self):
        input_config = InputConfig()

        input_config.set_param(**self.input_info)
        item = {"projectPath": self.project_path,}
        input_config.write_to_file(item)

    def create_basic_lattice_mulp_file(self):
        lattice_config = LatticeConfig()
        item = {"projectPath": self.project_path,}
        lattice_config.write_to_file(item)

    def create_basic_lattice_env_file(self):
        lattice_config = LatticeConfig()

        item = {"projectPath": self.project_path,
                "sim_type": "env"}
        lattice_config.write_to_file(item)

    def create_basic_ini_file(self):
        ini_config = IniConfig()

        res = ini_config.set_param(**self.ini_info)
        item = {"projectPath": self.project_path, }
        ini_config.write_to_file(item)



class CreateBasicProject():
    def __init__(self, item, platform):
        # item = {"project_path": ,
        #         "beam_keys": [],
        #         "input_keys": [],
        #         ""
        #          }

        self.item = item
        self.project_path = self.item["projectPath"]
        self.platform = platform


    def validate_keys(self):
        beam_keys_back = BeamConfig().beam_parameter_keys
        input_keys_back = InputConfig().input_parameter_keys


        beam_keys_front = self.item["beamKeys"]
        input_keys_front = self.item["inputKeys"]

        beam_extra_keys = set(beam_keys_front) - set(beam_keys_back)  # 前端多出的键
        beam_missing_keys = set(beam_keys_back) - set(beam_keys_front)  # 前端缺少的键

        input_extra_keys = set(input_keys_front) - set(input_keys_back)  # 前端多出的键
        input_missing_keys = set(input_keys_back) - set(input_keys_front)  # 前端缺少的键


        msg ={
            "beamExtra": list(beam_extra_keys),
            "beamMissing": list(beam_missing_keys),
            "inputExtra": list(input_extra_keys),
            "inputMissing": list(input_missing_keys)
        }
        return msg

    def create_project(self):
        obj = CreatBasicFile(self.project_path)

        error_info = {
            "error_type": obj.ini_info["error"]["error_type"],
            "seed": obj.ini_info["error"]["seed"],
        }

        kwargs = {
            "projectPath": self.project_path,
            "beamParams": obj.beam_info,
            "inputParams": obj.input_info,
            "errorParams": error_info,
            "beamExtra": [],
            "beamMissing": [],
            "inputExtra": [],
            "inputMissing": [],
        }

        if self.platform == "qt":
            pass
        elif self.platform == "web":
            validate_res = self.validate_keys()
            validate_res_values = [v for k, v in validate_res.items()]

            if any(validate_res_values):
                msg = ("The template parameter does not match the"
                       " parameters of the AVAS project, unable to generate the basic configuration directory.")


                error_msg = {k: v for k, v in validate_res.items() if v}
                kwargs.update(error_msg)
                output = format_output(code=-1, msg=msg, **kwargs)
                return output

        if not os.path.exists(self.project_path):
            os.makedirs(self.project_path)

        elif os.path.exists(self.project_path):
            # raise FileExistsError(f"The directory '{project_path}' already exists.")
            code = -1
            msg = f"The directory '{project_path}' already exists."
            res = format_output(code, msg=msg, **kwargs)
            return res


        input_file = os.path.join(self.project_path, 'InputFile')
        output_file = os.path.join(self.project_path, 'OutputFile')


        os.makedirs(input_file)
        os.makedirs(output_file)
        if self.platform == "web":
            field_path = os.path.join(self.project_path, 'InputFile', "field")
            os.makedirs(field_path)

        obj.create_basic_beam_file()
        obj.create_basic_input_file()
        obj.create_basic_lattice_mulp_file()
        obj.create_basic_lattice_env_file()
        obj.create_basic_ini_file()

        res = format_output(**kwargs)

        return res





if __name__ == "__main__":
    project_path = r"D:\using\test_avas_qt\tc"



    item = {
        "projectPath": project_path,

        "beamKeys": ['readparticledistribution', 'numofcharge', 'particlerestmass',
                                    'current', 'particlenumber', 'frequency',
                                    'kneticenergy', 'alpha_x', 'beta_x', 'emit_x',
                                    "alpha_y", "beta_y", "emit_y",
                                    "alpha_z", "beta_z", "emit_z",
                                    'distribution_x', 'distribution_y', "use_dst"],
        # 'distribution_y', 'aaa'


        "inputKeys": ["sim_type", "scmethod",  "spacecharge", "steppercycle",
                       "dumpperiodicity", "spacechargelong",'spacechargetype', "fieldSource", "device", "pchistogram_start", "pchistogram_grid", ]
        #"spacechargetype", 'bbb'
    }
    platform = "web"
    obj = CreateBasicProject(item, "web")
    res = obj.create_project()
    print(res)

