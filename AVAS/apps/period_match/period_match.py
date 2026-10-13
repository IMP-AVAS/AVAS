#周期匹配
#该代码的功能是为把入口和每个周期的出口做失配度

class PeriodMatch():
    def __init__(self, item):
        self.item = item

        self.project_path = item.get("project_path")
        self.field_path = item.get("field_path")
        self.match_sim_type = item.get("match_sim_type")

