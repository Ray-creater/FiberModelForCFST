from matplotlib.pyplot import axline
from numpy.lib.function_base import disp
from numpy.lib.shape_base import dsplit
from scipy.optimize.optimize import rosen_hess_prod
from section import *


class AxialLoadColmun(object):

    def __init__(self,section:Section,length:float) -> None:
        super().__init__()
        self.critical_section = section
        self.length=length
        self.axial_displacment =None 
        self.axial_displacment_previous = None 
        self.axial_force = None 
        self.axial_force_previous = None 

    def setTrialDeformation(self,axial_displacment:float):
        self.axial_displacment = axial_displacment
        section_strain = self.axial_displacment/self.length
        self.critical_section.setTrialDeformation(section_strain,0,0)
        self.axial_force,_,_ = self.critical_section.getForce

    def setTrialForce(axialForce:float,shear_force:float,moment:float):
        pass

    def commitState(self):
        self.axial_force_previous ,self.axial_displacment_previous = self.axial_force,self.axial_displacment
        self.critical_section.commitState()

    def revertToLast(self):
        pass

    def revertToStart(self):
        pass 

class LoadBendColumn():
    '''
    压弯柱，输出参数
    '''
    def __init__(self,critical_section:Section,length:float,axial_load:float) -> None:
        self.critical_section = critical_section
        self.length = length
        self.axial_load = axial_load
        self.lateral_displacement = None
        self.lateral_displacement_previous = None 
        self.lateral_force = None
        self.lateral_force_previous = None

    def setTrialDeformation(self,lateral_displacment:float):
        
        self.lateral_displacement = lateral_displacment
        curvature = np.pi**2/4/self.length**2*self.lateral_displacement
        self.critical_section.setCurvatureAtGivenAxialForce(curvature,0,self.axial_load)
        _,moment,_ = self.critical_section.getForce()
        self.lateral_force = moment/self.length

    def loadAxialForce(self,current_axial_force:float):
        self.critical_section.loadAxialForce(current_axial_force)

    @property
    def getDeformation(self):
        return self.lateral_displacement

    @property
    def getForce(self):
        return self.lateral_force

    def commitState(self):
        self.lateral_displacement_previous = self.lateral_displacement
        self.lateral_force_previous = self.lateral_force
        self.critical_section.commitState()

    def revertToLast(self):
        pass

    def revertToStart(self):
        pass 


# class PartialLoadColmun(object):

#     def __init__(self,section:Section,length:float,eccentrial_distance:float) -> None:
#         super().__init__()
#         self.critical_section = section
#         self.length=length
#         self.eccentrial_distence = eccentrial_distance
#         self.axial_displacment =None 
#         self.axial_displacment_previous = None 
#         self.axial_force = None 
#         self.axial_force_previous = None 
#         self.x_moment = None 
#         self.y_moment = None 
#         self.x_moment_previous = None 
#         self.y_moment_previous = None 
        

#     def setTrailDeformation(self,axial_displacment:float):
#         self.axial_displacment = axial_displacment
#         section_strain = self.axial_displacment/self.length
#         self.critical_section.setTrialDeformation(section_strain,0,0)
#         self.axial_force,_,_ = self.critical_section.getForce 


#     def setTrailForce(axialForce:float,shear_force:float,moment:float):
#         pass

#     @property
#     def getDeformation(self):
        
#     @property
#     def getForce(self):


#     def commitState(self):
#         self.axial_force_previous ,self.axial_displacment_previous = self.axial_force,self.axial_displacment
#         self.critical_section.commitState()

#     def revertToLast(self):
#         pass

#     def revertToStart(self):
#         pass 





if __name__=="__main__":

    # 定义截面
    # 定义截面大小
    section = Section.circle(108, 6)
    # 定义构成截面的材料
    # concrete = Concrete02(-50, -0.002, -10, -0.01,
    #                       0.003, 10, 30 / 0.002 * 2 / 10)

    concrete = ConcreteCM(-150, -0.002, 30000, 1.2, 1.5,
                                0.67, 5, 0.002, 1.3, 2, 0.57)

    steel = Steel02.new_3_para(345, 345 / 0.002, 0.01)
    # 定义对截面进行划分
    section.splitFiber(30, 10, concrete, steel)

    # 定义柱子参数
    column_length = 900
    columns_axial_load = 800000

    test_column = LoadBendColumn(section,column_length,columns_axial_load)

    # 定义加载路径
    displacement_limit = [10,20,30,40,50,60,70]
    displacement_path = []
    loop_point_num = 50
    for limit in displacement_limit:
        current_loop = np.concatenate([np.linspace(0,limit,loop_point_num),
        np.linspace(limit,-limit,loop_point_num*2),
        np.linspace(-limit,limit,loop_point_num*2),
        np.linspace(limit,-limit,loop_point_num*2),
        np.linspace(-limit,0,loop_point_num*2),])
        [displacement_path.append(i) for i in current_loop]

    # 加载
    ## 轴向加载
    axial_load_list = np.linspace(0,columns_axial_load,100)
    for axial_load in axial_load_list:
        test_column.loadAxialForce(-axial_load)
        test_column.commitState()
    
    ## 侧向加载
    lateral_force = []
    for lateral_displacement in displacement_path:
        test_column.setTrialDeformation(lateral_displacement)
        test_column.commitState()
        lateral_force.append(test_column.getForce)
    
    plt.plot(displacement_path,lateral_force)
    plt.show()


    

