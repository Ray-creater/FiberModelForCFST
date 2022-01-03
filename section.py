from scipy import optimize
from material import Concrete02, Steel02, ConcreteCM
from fiber import Material, Fiber
import numpy as np
import matplotlib.pyplot as plt
import copy


class Section(object):
    def __init__(self, shape: str, size, thickness: float) -> None:
        super().__init__()
        if shape == "circle" or shape == "square":
            if isinstance(size, float):
                self.size = size
            else:
                pass

        elif shape == "rectangular":
            if isinstance(size, tuple):
                self.size = size
            else:
                pass
        self.thickness = thickness
        self.fiber_info = {
            "concrete": {"x_location": [], "y_location": [], "area": []},
            "steel": {"x_location": [], "y_location": [], "area": []},
        }
        self.shape = shape
        self.size = size
        self.fibers = {"concrete": [], "steel": []}

        self.axial_strain = 0
        self.axial_strain_previous = 0
        self.axial_force = 0
        self.axial_force_previous = 0

        self.x_curvature = 0
        self.x_curvature_previous = 0
        self.x_moment = 0
        self.x_moment_previous = 0

        self.y_curvature = 0
        self.y_curvature_previous = 0
        self.y_moment = 0
        self.y_moment_previous = 0

    @classmethod
    def rectangular(cls, x_length: float, y_length: float, thickness: float):
        size = (x_length, y_length)
        return cls("rectangular", size, thickness)

    @classmethod
    def square(cls, length: float, thickness: float):
        return cls.rectangular(length, length, thickness)

    @classmethod
    def circle(cls, radius: float, thickness: float):
        return cls("circle", radius, thickness)

    @property
    def getCopy(self):
        return copy.deepcopy(self)

    def splitFiber(
        self, x_dimension_num, y_dimension_num, concrete: Material, steel: Material
    ):
        if self.shape == "circle":
            # Concrete
            r_direction_gap = (self.size - self.thickness) / x_dimension_num
            r_direction_value_list = [
                r_direction_gap * (i + 0.5) for i in range(1, x_dimension_num)
            ]
            theta_direction_gap = 360 / y_dimension_num
            theta_direction_value_list = [
                theta_direction_gap * i for i in range(y_dimension_num)
            ]
            for i in r_direction_value_list:
                for j in theta_direction_value_list:
                    self.fiber_info["concrete"]["x_location"].append(
                        i * np.cos(j / 360 * 2 * np.pi)
                    )
                    self.fiber_info["concrete"]["y_location"].append(
                        i * np.sin(j / 360 * 2 * np.pi)
                    )
                    self.fiber_info["concrete"]["area"].append(
                        i * theta_direction_gap / 360 * 2 * np.pi * r_direction_gap
                    )
            self.fiber_info["concrete"]["x_location"].append(0)
            self.fiber_info["concrete"]["y_location"].append(0)
            self.fiber_info["concrete"]["area"].append(np.pi * r_direction_gap ** 2)

            # Steel tube
            x_dimension_num = 2
            r_direction_gap = self.thickness / x_dimension_num
            r_direction_value_list = [
                j + self.size
                for j in [
                    r_direction_gap * (i + 0.5) for i in range(0, x_dimension_num)
                ]
            ]
            theta_direction_gap = 360 / y_dimension_num
            theta_direction_value_list = [
                theta_direction_gap * i for i in range(y_dimension_num)
            ]
            for i in r_direction_value_list:
                for j in theta_direction_value_list:
                    self.fiber_info["steel"]["x_location"].append(
                        i * np.cos(j / 180 * 2 * np.pi)
                    )
                    self.fiber_info["steel"]["y_location"].append(
                        i * np.sin(j / 180 * 2 * np.pi)
                    )
                    self.fiber_info["steel"]["area"].append(
                        i * theta_direction_gap / 360 * 2 * np.pi * r_direction_gap
                    )

        elif self.shape == "rectangular":
            # concrete
            x_left_value = -self.size[0] / 2 + self.thickness
            x_gap = abs(x_left_value) * 2 / x_dimension_num
            x_location_list = np.linspace(
                x_left_value + x_gap / 2, -x_left_value - x_gap / 2, x_dimension_num
            )
            y_down_value = -self.size[1] / 2 + self.thickness
            y_gap = abs(y_down_value) * 2 / y_dimension_num
            y_location_list = np.linspace(
                y_down_value + y_gap / 2, -y_down_value - y_gap / 2, y_dimension_num
            )
            area = x_gap * y_gap
            for i in x_location_list:
                for j in y_location_list:
                    self.fiber_info["concrete"]["x_location"].append(i)
                    self.fiber_info["concrete"]["y_location"].append(j)
                    self.fiber_info["concrete"]["area"].append(area)

            # steel
            steel_mesh_num = 1
            steel_gap = self.thickness / steel_mesh_num
            x_location_left_list = np.linspace(
                -self.size[0] / 2 + steel_gap / 2,
                x_left_value - steel_gap / 2,
                steel_mesh_num,
            )
            y_location_down_list = np.linspace(
                -self.size[1] / 2 + steel_gap / 2,
                y_down_value - steel_gap / 2,
                steel_mesh_num,
            )

            steel_x_whole_num = int(abs(x_left_value) * 2 / steel_gap)
            x_location_x_whole_list = np.linspace(
                x_left_value + steel_gap / 2,
                -x_left_value - steel_gap / 2,
                steel_x_whole_num,
            )
            steel_y_whole_num = int(abs(y_down_value) * 2 / steel_gap)
            y_location_y_whole_list = np.linspace(
                y_down_value + steel_gap / 2,
                -y_down_value - steel_gap / 2,
                steel_y_whole_num,
            )

            area = steel_gap * steel_gap

            for i in x_location_left_list:
                for j in y_location_y_whole_list:
                    self.fiber_info["steel"]["x_location"].append(i)
                    self.fiber_info["steel"]["y_location"].append(j)
                    self.fiber_info["steel"]["area"].append(area)
            for i in -x_location_left_list:
                for j in y_location_y_whole_list:
                    self.fiber_info["steel"]["x_location"].append(i)
                    self.fiber_info["steel"]["y_location"].append(j)
                    self.fiber_info["steel"]["area"].append(area)
            for i in x_location_x_whole_list:
                for j in y_location_down_list:
                    self.fiber_info["steel"]["x_location"].append(i)
                    self.fiber_info["steel"]["y_location"].append(j)
                    self.fiber_info["steel"]["area"].append(area)
            for i in x_location_x_whole_list:
                for j in -y_location_down_list:
                    self.fiber_info["steel"]["x_location"].append(i)
                    self.fiber_info["steel"]["y_location"].append(j)
                    self.fiber_info["steel"]["area"].append(area)
            for i in x_location_left_list:
                for j in y_location_down_list:
                    self.fiber_info["steel"]["x_location"].append(i)
                    self.fiber_info["steel"]["y_location"].append(j)
                    self.fiber_info["steel"]["area"].append(area)
            for i in x_location_left_list:
                for j in -y_location_down_list:
                    self.fiber_info["steel"]["x_location"].append(i)
                    self.fiber_info["steel"]["y_location"].append(j)
                    self.fiber_info["steel"]["area"].append(area)
            for i in -x_location_left_list:
                for j in y_location_down_list:
                    self.fiber_info["steel"]["x_location"].append(i)
                    self.fiber_info["steel"]["y_location"].append(j)
                    self.fiber_info["steel"]["area"].append(area)
            for i in -x_location_left_list:
                for j in -y_location_down_list:
                    self.fiber_info["steel"]["x_location"].append(i)
                    self.fiber_info["steel"]["y_location"].append(j)
                    self.fiber_info["steel"]["area"].append(area)

        for i, j, k in zip(
            self.fiber_info["concrete"]["x_location"],
            self.fiber_info["concrete"]["y_location"],
            self.fiber_info["concrete"]["area"],
        ):
            self.fibers["concrete"].append(Fiber(concrete.getCopy, (i, j), k))
        for i, j, k in zip(
            self.fiber_info["steel"]["x_location"],
            self.fiber_info["steel"]["y_location"],
            self.fiber_info["steel"]["area"],
        ):
            self.fibers["steel"].append(Fiber(steel.getCopy, (i, j), k))

    def setTrialDeformation(
        self, axial_strain: float, x_curvature: float, y_curvature: float
    ):
        """
        输入的为曲率（单位:长度分之弧度 ）
        """
        self.axial_strain = axial_strain
        for i in self.fibers["concrete"]:
            i.setTrialStrain(
                axial_strain + i.location[1] * x_curvature + i.location[0] * y_curvature
            )
        for i in self.fibers["steel"]:
            i.setTrialStrain(
                axial_strain + i.location[1] * x_curvature + i.location[0] * y_curvature
            )
        self.x_curvature = x_curvature
        self.y_curvature = y_curvature
        self.axial_force = self.getAxialForce()
        self.x_moment, self.y_moment = self.getMoment()

    def setTrialForce(
        self,
        axial_force: float,
        x_moment: float,
        y_moment: float,
    ):
        self.axial_force = axial_force
        self.x_moment = x_moment
        self.y_moment = y_moment

        def momentEquation(curvature: list):
            _, x_moment_simu, y_moment_simu, _ = self.setCurvatureAtGivenAxialForce(
                curvature[0], curvature[1], axial_force
            )
            return (x_moment_simu - x_moment), (y_moment_simu - y_moment)

        res = optimize.fsolve(
            momentEquation, [self.x_curvature_previous, self.y_curvature_previous]
        )

        self.x_curvature = res[0]
        self.y_curvature = res[1]
        self.axial_force = axial_force

        (
            _,
            self.x_moment,
            self.y_moment,
            self.axial_strain,
        ) = self.setCurvatureAtGivenAxialForce(res[0], res[1], axial_force)

        print(
            f"x_curvature:{self.x_curvature}----y_curvature:{self.y_curvature}-----axial_strain:{self.axial_strain}"
        )

    def loadAxialForce(self, given_force: float):
        self.setCurvatureAtGivenAxialForce(0, 0, given_force)

    def getDeformation(self):
        return self.axial_strain, self.x_curvature, self.y_curvature

    def getForce(self):
        return self.axial_force, self.x_moment, self.y_moment

    def getMoment(self, reference_point: tuple = (0, 0)):
        x_moment, y_moment = 0, 0
        for i in self.fibers["concrete"]:
            m1, m2 = i.moment(reference_point)
            x_moment += m1
            y_moment += m2
        for i in self.fibers["steel"]:
            m1, m2 = i.moment(reference_point)
            x_moment += m1
            y_moment += m2
        return x_moment, y_moment

    def getAxialForce(self):
        force_cumuli = 0
        for i in self.fibers["concrete"]:
            force_cumuli += i.force
        for i in self.fibers["steel"]:
            force_cumuli += i.force
        return force_cumuli

    def commitState(self):
        for i in self.fibers["concrete"]:
            i.commitState()
        for j in self.fibers["steel"]:
            j.commitState()
        self.axial_strain_previous = self.axial_strain
        self.x_curvature_previous = self.x_curvature
        self.y_curvature_previous = self.y_curvature

    def revertToLast(self):
        for i in self.fibers["concrete"]:
            i.revertToLast()
        for i in self.fibers["steel"]:
            i.revertToLast()
        self.axial_strain = self.axial_strain_previous
        self.x_curvature = self.x_curvature_previous
        self.y_curvature = self.y_curvature_previous

    def revertToStart(self):
        self.axial_strain = 0
        self.axial_strain_previous = 0
        self.axial_force = 0
        self.axial_force_previous = 0

        self.x_curvature = 0
        self.x_curvature_previous = 0
        self.x_moment = 0
        self.x_moment_previous = 0

        self.y_curvature = 0
        self.y_curvature_previous = 0
        self.y_moment = 0
        self.y_moment_previous = 0

        for i in self.fibers["concrete"]:
            i.revertToStart()
        for i in self.fibers["steel"]:
            i.revertToStart()

    def setCurvatureAtGivenAxialForce(
        self, x_curvature: float, y_curvature: float = 0, given_axial_force: float = 0
    ):
        self.x_curvature = x_curvature
        self.y_curvature = y_curvature

        def setCurvatureAtGivenAxialForceEquation(axial_strain):
            self.setTrialDeformation(axial_strain, x_curvature, y_curvature)
            equationforce, _, _ = self.getForce()
            return (equationforce - given_axial_force) ** 2

        res = optimize.brent(setCurvatureAtGivenAxialForceEquation)

        solution_strain = res
        # print(f"Current optimize: {res}")

        self.setTrialDeformation(solution_strain, x_curvature, y_curvature)
        # print(f"Current axial_strain: {solution_strain}")


def curvatureLoadAtGivenAxialForce(
    section: Section, curvature_path: list, given_axial_force: float
):
    (
        output_force_list,
        output_x_moment_list,
        output_y_moment_list,
        output_axial_strain_list,
    ) = ([], [], [], [])
    for (x_curvature, y_curvature) in curvature_path:
        section.setCurvatureAtGivenAxialForce(
            x_curvature, y_curvature, given_axial_force
        )
        section.commitState()
        output_force, output_x_moment, output_y_moment = section.getForce()
        output_axial_strain, _, _ = section.getDeformation()
        output_force_list.append(output_force)
        output_x_moment_list.append(output_x_moment)
        output_y_moment_list.append(output_y_moment)
        output_axial_strain_list.append(output_axial_strain)
        print(f"Current curvature:{x_curvature}")
    return (
        output_force_list,
        output_x_moment_list,
        output_y_moment_list,
        output_axial_strain_list,
    )


if __name__ == "__main__":

    # 定义整个截面
    # 定义截面大小
    section = Section.circle(108, 6)
    # 定义构成截面的材料
    # concrete = Concrete02(-50, -0.002, -10, -0.01,
    #                       0.003, 10, 30 / 0.002 * 2 / 10)

    concrete = ConcreteCM(-150, -0.002, 30000, 1.2, 1.5, 0.67, 5, 0.002, 1.3, 2, 0.57)

    steel = Steel02.new_3_para(345, 345 / 0.002, 0.1)
    # 定义对截面进行划分
    section.splitFiber(30, 10, concrete, steel)

    # 定义加载路径
    x_curvature = np.linspace(0, 0.0005, 500)
    x_curvature = np.concatenate(
        (x_curvature, np.linspace(0.0005, -0.0005, 500)), axis=0
    )
    x_curvature = np.concatenate(
        (x_curvature, np.linspace(-0.0005, 0.0005, 500)), axis=0
    )
    x_curvature = np.concatenate(
        (x_curvature, np.linspace(0.0005, -0.0005, 500)), axis=0
    )
    x_curvature = np.concatenate(
        (x_curvature, np.linspace(-0.0005, 0.001, 500)), axis=0
    )
    x_curvature = np.concatenate((x_curvature, np.linspace(0.001, -0.001, 500)), axis=0)
    x_curvature = np.concatenate((x_curvature, np.linspace(-0.001, 0.001, 500)), axis=0)
    x_curvature = np.concatenate((x_curvature, np.linspace(0.001, -0.001, 500)), axis=0)
    curvature_path = [(i, 0) for i in x_curvature]
    given_axial_force = -100000
    for force in np.linspace(0, given_axial_force):
        section.loadAxialForce(force)
        section.commitState()

    (
        force_list,
        x_moment_list,
        y_moment_list,
        axial_strain_list,
    ) = curvatureLoadAtGivenAxialForce(section, curvature_path, given_axial_force)

    figure = plt.figure()
    ax1 = figure.add_subplot(221, projection="3d")
    ax2 = figure.add_subplot(222)
    ax3 = figure.add_subplot(223)
    ax4 = figure.add_subplot(224)
    ax2.plot(x_curvature, axial_strain_list)
    ax2.set_title("curvature Vs axial strain")
    ax3.plot(x_curvature, force_list)
    ax3.set_title("curvature VS force")
    ax3.set_ylim((0, given_axial_force * 2))
    ax4.plot(x_curvature, x_moment_list)
    ax4.set_title("curvature VS moment")
    plt.show()

    # # 定义整个截面
    # # 定义截面大小
    # section = Section.circle(108, 6)
    # # 定义构成截面的材料
    # concrete = Concrete02(-50, -0.002, -10, -0.01, 0.003, 10, 30 / 0.002 * 2 / 10)
    # steel = Steel02.new_3_para(345, 345 / 0.002, 0.1)
    # # 定义对截面进行划分
    # section.splitFiber(30, 10, concrete, steel)
    # axial_strain_list = []

    # #Force Load Path
    # axialForces = np.linspace(0,-1500000,50)
    # for axialForce in axialForces:
    #     section.setTrialForce(axialForce,0,0)
    #     section.commitState()
    #     axial_strain = section.getDeformation()
    #     axial_strain_list.append(axial_strain)

    # plt.plot(axial_strain_list,axialForces)
    # plt.show()
