from material import Concrete02, ConcreteCM, Steel02
from section import Section ,Steel02, Concrete02,ConcreteCM
import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd 
import os 
from sko.GA  import GA,GA_TSP
from sko.operators import crossover,mutation


if __name__ =="__main__":
    
    # 定义截面大小
    section = Section.circle(54, 8)
    # concrete = ConcreteCM(-96.1,-0.002,30000,1.2,3,0.56,20,0.0002,1.5,3,0.67)

    steel = Steel02.new_3_para(351, 351 / 0.002, 0.01)
    concrete = Concrete02(-96.1,-0.003, -40, -0.005, 0.003, 10, 30 / 0.002 * 2 / 10)





     # 卢师姐 试件L1-8-0
    current_dir = os.getcwd()
    excel_path = os.path.join(current_dir,"L1_8_0.xlsx")
    exp_data = pd.read_excel(excel_path)
    exp_strain = exp_data['strain']
    exp_force = exp_data['stress']*1000 
    exp_force = exp_force.to_numpy()



    # def loss_func(fcc,ecc,fcu,ecu):
    #     print("Running loss")
    #     concrete = Concrete02(fcc,ecc, fcu, ecu, 0.003, 10, 30 / 0.002 * 2 / 10)
    #     section.splitFiber(5, 5, concrete, steel)

    #     axial_strain_list = exp_strain
    #     axial_force_list = []
    #     axial_force_list_concrete=[]
    #     axial_force_list_steel=[]

    #     for axial_strain in axial_strain_list:
    #         section.setTrialDeformation(-axial_strain,0,0)
    #         section.commitState()
    #         axial_force,_,_ = section.getForce()
    #         axial_force_list.append(-axial_force)
    #         axial_force_concrete =  0
    #         axial_force_steel = 0
    #         for fiber_concrete in section.fibers['concrete']:
    #             axial_force_concrete += fiber_concrete.getForce
    #         for fiber_steel in section.fibers['steel']:
    #             axial_force_steel += fiber_steel.getForce
    #         axial_force_list_concrete.append(-axial_force_concrete)
    #         axial_force_list_steel.append(-axial_force_steel)

    #     axial_force_list = np.array(axial_force_list)
    #     return np.sum((exp_force-axial_force_list)**2)


    # opt_paras_lb=[-200,-0.01,-100,-0.1]
    # opt_paras_ub=[-50,-0.0003,-5,-0.02]

    # ga = GA(loss_func, 4, lb=opt_paras_lb, ub=opt_paras_ub)
    # ga.register(operator_name="crossover", operator=crossover.crossover_2point)
    # best = ga.run()
    # print(best)

    # concrete = Concrete02(best[0][0],best[0][1], best[0][2], best[0][3], 0.003, 10, 30 / 0.002 * 2 / 10)
    section.splitFiber(5, 5, concrete, steel)


    axial_strain_list = exp_strain
    axial_force_list = []
    axial_force_list_concrete=[]
    axial_force_list_steel=[]


    for axial_strain in axial_strain_list:
        section.setTrialDeformation(-axial_strain,0,0)
        section.commitState()
        axial_force,_,_ = section.getForce()
        axial_force_list.append(-axial_force)
        axial_force_concrete =  0
        axial_force_steel = 0
        for fiber_concrete in section.fibers['concrete']:
            axial_force_concrete += fiber_concrete.getForce
        for fiber_steel in section.fibers['steel']:
            axial_force_steel += fiber_steel.getForce
        axial_force_list_concrete.append(-axial_force_concrete)
        axial_force_list_steel.append(-axial_force_steel)

    exp_force,axial_force_list = np.array(exp_force),np.array(axial_force_list)
    plt.plot(axial_strain_list,axial_force_list,label='mimic')  
    plt.plot(axial_strain_list,axial_force_list_concrete,label='concrete')
    plt.plot(axial_strain_list,axial_force_list_steel,label='steel')
    plt.plot(exp_strain,exp_force,label="exp")
    plt.xlabel("strain")
    plt.ylabel("force(N)")




    plt.legend()
    plt.show()

