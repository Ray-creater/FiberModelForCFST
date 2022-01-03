from material import Concrete02, ConcreteCM, Steel02
from section import Section, Steel02, Concrete02, ConcreteCM
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os


if __name__ == "__main__":

    # 定义截面大小
    section = Section.circle(54, 8)
    # concrete = ConcreteCM(-120, -0.008, 30000, 0.2, 5, 0.56, 20, 0.0002, 1.5, 3, 0.67)
    steel = Steel02.new_3_para(351, 351 / 0.002, 0.015)

    # 卢师姐 试件L1-8-0
    current_dir = os.getcwd()
    excel_path = os.path.join(current_dir, "L1_8_0.xlsx")
    exp_data = pd.read_excel(excel_path)
    exp_strain = exp_data["strain"]
    exp_force = exp_data["stress"] * 1000
    exp_force = exp_force.to_numpy()

    concrete = Concrete02(-110, -0.006, -100, -0.01, 0.003, 10, 30 / 0.002 * 2 / 10)

    section.splitFiber(5, 5, concrete, steel)

    axial_strain_list = exp_strain
    axial_force_list = []
    axial_force_list_concrete = []
    axial_force_list_steel = []

    for axial_strain in axial_strain_list:
        section.setTrialDeformation(-axial_strain, 0, 0)
        section.commitState()
        axial_force, _, _ = section.getForce()
        axial_force_list.append(-axial_force)
        axial_force_concrete = 0
        axial_force_steel = 0
        for fiber_concrete in section.fibers["concrete"]:
            axial_force_concrete += fiber_concrete.getForce
        for fiber_steel in section.fibers["steel"]:
            axial_force_steel += fiber_steel.getForce
        axial_force_list_concrete.append(-axial_force_concrete)
        axial_force_list_steel.append(-axial_force_steel)

    exp_force, axial_force_list = np.array(exp_force), np.array(axial_force_list)
    plt.xlabel("strain")
    plt.ylabel("Force")
    plt.plot(axial_strain_list, axial_force_list, label="mimic")
    plt.plot(axial_strain_list, axial_force_list_concrete, label="concrete")
    plt.plot(axial_strain_list, axial_force_list_steel, label="steel")
    plt.plot(exp_strain, exp_force, label="exp")

    plt.legend()
    plt.show()
