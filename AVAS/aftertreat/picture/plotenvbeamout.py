from aftertreat.picture.initialplot import PicturePlot_2D
import os
from dataprovision.env_beam_out import EnvBeamOutParameter

class PlotEnvBeamOut(PicturePlot_2D):
    """
    包络模拟的可视化
    """
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.beam_out_path = os.path.join(self.project_path, 'OutputFile', 'env_beam_out.txt')



    def get_x_y(self, picture_name):
        beam_out_info = EnvBeamOutParameter(self.beam_out_path)
        beam_out_info.get_parameter()
        self.x = beam_out_info.z
        if picture_name == 'beta':
            self.y = beam_out_info.beta

        elif picture_name == 'gamma':
            self.y = beam_out_info.gamma
            self.ylabel = 'gamma'

        elif picture_name == 'alpha_x':
            self.y = beam_out_info.alpha_x
            self.ylabel = 'alpha_x'

        elif picture_name == 'alpha_y':
            self.y = beam_out_info.alpha_y
            self.ylabel = 'alpha_y'

        elif picture_name == 'alpha_z':
            self.y = beam_out_info.alpha_z
            self.ylabel = 'alpha_z'

        elif picture_name == 'beta_x':
            self.y = beam_out_info.beta_x
            self.ylabel = 'beta_x'

        elif picture_name == 'beta_y':
            self.y = beam_out_info.beta_y
            self.ylabel = 'beta_y'

        elif picture_name == 'beta_z':
            self.y = beam_out_info.beta_z
            self.ylabel = 'beta_z'

        elif picture_name == 'emit_x':
            self.y = beam_out_info.emit_x
            self.ylabel = 'emit_x'

        elif picture_name == 'emit_y':
            self.y = beam_out_info.emit_y
            self.ylabel = 'emit_y'

        elif picture_name == 'emit_z':
            self.y = beam_out_info.emit_z
            self.ylabel = 'emit_z'

        self.xlabel = 'Position(m)'

if __name__ == '__main__':
    v = PlotEnvBeamOut(r'C:\Users\anxin\Desktop\tu_env')
    v.get_x_y('emit_z')
    v.run(show_= 1)