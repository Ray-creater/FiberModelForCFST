from matplotlib import set_loglevel
from material import Concrete02, ConcreteCM, Steel02
from section import Section, Steel02, Concrete02, ConcreteCM
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from SHAPEelement import LoadBendColumn


if __name__ == "__main__":

    # 定义截面大小
    section = Section.rectangular(100, 150, 18)
    # concrete = ConcreteCM(-120, -0.008, 30000, 0.2, 5, 0.56, 20, 0.0002, 1.5, 3, 0.67)
    steel = Steel02.new_3_para(444.6, 43400, 0.01)

    # 卢师姐 试件L1-8-0
    current_dir = os.getcwd()
    excel_path = os.path.join(current_dir, "lateralLoad.xlsx")
    exp_data = pd.read_excel(excel_path)
    exp_displacement = exp_data["disp"]
    exp_force = exp_data["force"] * 1000

    concrete = Concrete02(-128, -0.002, -10, -0.01, 0.003, 10, 30 / 0.002 * 2 / 10)

    section.splitFiber(5, 5, concrete, steel)

    column_length = 600
    steel_area = 250 * 2 * 18
    concrete_area = 100 * 150 - steel_area
    column_axial_load = 0.1 * (steel_area * 444.6 + concrete_area * 128)
    column = LoadBendColumn(section, column_length, column_axial_load)

    # 加载
    ## 轴向加载
    axial_load_list = np.linspace(0, column_axial_load, 100)
    for axial_load in axial_load_list:
        column.loadAxialForce(-axial_load)
        column.commitState()

    ## 侧向加载
    lateral_force = []
    for lateral_displacement in exp_displacement:
        column.setTrialDeformation(lateral_displacement)
        column.commitState()
        lateral_force.append(column.getForce)

    plt.xlabel("Displacement(mm)")
    plt.ylabel("Force(N)")
    plt.plot(exp_displacement, lateral_force, label="mimic")
    plt.plot(exp_displacement, exp_force, label="exp")
    plt.legend()
    plt.show()
