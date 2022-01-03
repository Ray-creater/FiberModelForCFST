from material import *


class Fiber(object):

    def __init__(self,material:Material,loc:tuple,area:float):
        super().__init__()
        self.material=material
        self.location=loc
        self.area=area
        self.strain=0
        self.force=0
        self.strain_previous=0
        self.force_previous=0

    @property
    def getCopy(self):
        return Fiber(self.material,self.location,self.area)

    @property
    def getForce(self):
        return self.force

    def setTrialStrain(self, trail_strain: float):
        self.strain=trail_strain
        self.material.setTrialStrain(trail_strain)
        self.force=self.material.getStress*self.area

    def revertToLast(self):
        self.strain=self.strain_previous
        self.force=self.force_previous
        self.material.revertToLastCommit()

    def revertToStart(self):
        self.strain=0
        self.force=0
        self.strain_previous=0
        self.force_previous=0
        self.material.revertToStart()

    def commitState(self):
        self.strain_previous=self.strain
        self.force_previous=self.force
        self.material.commitState()

    def moment(self,loc_reference:tuple=(0,0)):
        x_dimension=self.location[0]-loc_reference[0]
        y_dimension=self.location[1]-loc_reference[1]
        x_moment=self.force*y_dimension
        y_moment=self.force*x_dimension
        return x_moment,y_moment


if __name__=="__main__":
    # steel=Steel02.new_3_para(345,345/0.002,0.1)
    # fiber=Fiber(steel,(1,1),1)
    # for i in np.linspace(0,10,10):
    #     fiber.setTrailDisp(i)
    #     fiber.commitState()
    # plt.plot(fiber.history_disp,fiber.history_force,color='red')
    # fiber.revertToLast()
    # fiber.setTrailDisp(10)
    # fiber.commitState()
    # fiber.setTrailDisp(9)
    # fiber.commitState()
    # plt.plot(fiber.history_disp,fiber.history_force,color='g')
    # plt.show()

    #钢筋 在左右两端都相同受力
    steel1=Steel02.new_3_para(420,420/0.002,0.01)
    concrete=Concrete02(-150,-0.002,-100,-0.01,0.003,20,30/0.002*2/10)

    fiber1=Fiber(steel1.getCopy,(1,1),1)
    fiber2=fiber1.getCopy
    force1=[]
    force2=[]
    disp=np.linspace(0,30,100)
    for i in disp:
        fiber1.setTrailDisp(i)
        force1.append(fiber1.material.getStress)
        fiber1.material.commitState()
        fiber2.setTrailDisp(-i)
        force2.append(fiber2.material.getStress)
        fiber2.material.commitState()
    plt.plot(disp,force1,label='force1')
    plt.plot(disp,force2,label='force2')
    plt.legend()
    plt.show()
