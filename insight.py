from copy import deepcopy
from section import *
from material import *
from fiber import *

import numpy as np


if __name__ == "__main__":
    # plot
    # plt.ion()
    # ax=plt.subplot(111,projection='3d')
    # section=Section.circle(200,10)
    # concrete=Concrete02(-120,-0.002,-10,-0.01,0.003,10,30/0.002*2/10)
    # steel=Steel02.new_3_para(345,345/0.002,0.1)
    # section.splitFiber(10,10,concrete,steel)
    # force_all=[]
    # moment_all=[]
    # for i in np.linspace(0,0.6,1000):
    #     force,moment=section.setTrailDeformation(0,i,0)
    #     section.commitState()
    #     force_all.append(force)
    #     moment_all.append(moment[0])
    #     concrete_fiber=section.fibers['concrete']
    #     steel_fiber=section.fibers['steel']
    #     xloc=[]
    #     yloc=[]
    #     strain=[]
    #     moment_list=[]
    #     force_list=[]
    #     for i in concrete_fiber:
    #         xloc.append(i.location[0])
    #         yloc.append(i.location[1])
    #         strain.append(i.strain)
    #         moment_list.append(i.momentX)
    #         force_list.append(i.force)
    #     for i in steel_fiber:
    #         xloc.append(i.location[0])
    #         yloc.append(i.location[1])
    #         strain.append(i.strain)
    #         moment_list.append(i.momentX)
    #         force_list.append(i.force)

    #     # ax.scatter(xloc,yloc,moment_list,cmap='rainbow')
    #     ax.scatter(xloc,yloc,force_list,cmap='rainbow')
    #     # ax.scatter(xloc,yloc,strain,cmap='rainbow')
    #     plt.show()
    #     plt.pause(1)

    figure = plt.figure()

    ax1 = figure.add_subplot(221, projection="3d")
    ax2 = figure.add_subplot(222, projection="3d")
    ax3 = figure.add_subplot(223, projection="3d")
    ax4 = figure.add_subplot(224)
    section = Section.circle(200, 10)
    # section=Section.rectangular(200,400,10)
    # section=Section.square(400,10)
    concrete = ConcreteCM(-120,-0.003,40000,1.2,3,0.56,20,0.0002,1.5,3,0.67)
    # concrete = Concrete02(-120, -0.002, -10, -0.01, 0.003, 10, 30 / 0.002 * 2 / 10)
    steel = Steel02.new_3_para(345, 345 / 0.002,0.01)
    section.splitFiber(20, 20, concrete, steel)
    force_all = []
    moment_all = []
    basetheta = np.linspace(0, 0.0001, 30)
    # theta=np.concatenate((theta,[i for i in reversed(theta)],-theta,[-i for i in reversed(theta)],theta))
    theta = np.concatenate((basetheta, [i for i in reversed(basetheta)]))
    theta = np.concatenate((theta, -basetheta, [-i for i in reversed(basetheta)]))
    theta = np.concatenate((theta, basetheta, [i for i in reversed(basetheta)]))
    theta = np.concatenate((theta, -basetheta, [-i for i in reversed(basetheta)]))
    theta = np.concatenate((theta, basetheta, [i for i in reversed(basetheta)]))
    theta = np.concatenate((theta, -basetheta, [-i for i in reversed(basetheta)]))

    for j in theta:
        section.setCurvatureAtGivenAxialForce(j)
        section.commitState()
        
        moment_all.append(section.getForce()[1])
        concrete_fiber = section.fibers["concrete"]
        steel_fiber = section.fibers["steel"]
        xloc = []
        yloc = []
        strain = []
        moment_list = []
        force_list = []
        for i in concrete_fiber:
            xloc.append(i.location[0])
            yloc.append(i.location[1])
            strain.append(i.strain)
            moment_list.append(i.moment()[0])
            force_list.append(i.force)
        for i in steel_fiber:
            xloc.append(i.location[0])
            yloc.append(i.location[1])
            strain.append(i.strain)
            moment_list.append(i.moment()[0])
            force_list.append(i.force)
            
        ax1.cla()
        ax2.cla()
        ax3.cla()
        ax1.scatter(xloc, yloc, moment_list, cmap="rainbow")
        ax1.set_title("Moment")
        # ax1.set_zlim(-5e7, 5e7)
        ax2.scatter(xloc, yloc, force_list, cmap="rainbow")
        ax2.set_title("Force")
        # ax2.set_zlim(-4e5, 4e5)
        ax3.scatter(xloc, yloc, strain, cmap="rainbow")
        ax3.set_title("strain")
        # ax3.set_zlim(-0.075, 0.075)

        ax4.scatter(j, section.getForce()[1])
        ax4.set_xlabel("Curvature")
        ax4.set_ylabel("Moment")
        # ax4.set_title("curvature_moment")

        # ax.set_zlim(-20,20)
        # plt.show()
        # plt.pause(0.001)
    plt.show()
    plt.savefig("ccc.svg")