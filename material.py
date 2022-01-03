from abc import ABCMeta, abstractmethod, abstractproperty
from matplotlib.colors import TwoSlopeNorm
import matplotlib.pyplot as plt
import numpy as np
import copy
import concreteCMpy


class Material(object):

    def __init__(self) -> None:
        super().__init__()
        self.sig = 0
        self.eps = 0

    @abstractmethod
    def setTrialStrain(self, trial_strain: float):
        pass

    @abstractmethod
    def commitState(self):
        pass

    @abstractmethod
    def revertToLastCommit(self):
        pass

    @abstractmethod
    def revertToStart(self):
        pass


class ConcreteCM(Material):

    def __init__(self, fc, ec, Ec, rc, xcrn, ulc, ft, et, rt, xtrn, ult) -> None:

        super().__init__()
        self.wapperred = concreteCMpy.ConcreteCMpy(
            1, fc, ec, Ec, rc, xcrn, ulc, ft, et, rt, xtrn, ult)
        self.para = (fc, ec, Ec, rc, xcrn, ulc, ft, et, rt, xtrn, ult)

    @property
    def getCopy(self):
        copyedConcreteCM = ConcreteCM(*self.para)

        return copyedConcreteCM

    def setTrialStrain(self, trial_strain: float):
        self.wapperred.setTrialStrain(trial_strain, 0)

    def commitState(self):
        self.wapperred.commitState()
        return super().commitState()

    def revertToLastCommit(self):
        self.wapperred.revertToLastCommit()
        return super().revertToLastCommit()

    def revertToStart(self):
        self.wapperred.revertToStart()
        return super().revertToStart()

    @property
    def getStress(self):
        return self.wapperred.getStress()

    @property
    def getStrain(self):
        return self.wapperred.getStrain()


class Steel02(Material):

    def __init__(self, Fy: float, E0: float, b: float, R0: float, cR1: float, cR2: float, a1: float, a2: float, a3: float, a4: float, sigInit: float) -> None:
        super().__init__()
        self.Fy = Fy
        self.E0 = E0
        self.b = b
        self.R0 = R0
        self.cR1 = cR1
        self.cR2 = cR2
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
        self.sigini = sigInit

        self.EnergyP = 0
        self.konP = 0
        self.kon = 0
        self.eP = self.E0
        self.epsP = 0
        self.sigP = 0
        self.sig = 0
        self.eps = 0
        self.e = self.E0

        self.epsmaxP = self.Fy/self.E0
        self.epsminP = -self.epsmaxP
        self.epsplP = 0
        self.epss0P = 0
        self.sigs0P = 0
        self.epssrP = 0
        self.sigsrP = 0

        # self.epsmax=Fy/E0
        # self.epsmin=-self.epsmaxP
        # self.epspl=0
        # self.epss0=0
        # self.sigs0=0
        # self.epsr=0
        # self.sigr=0

        if (self.sigini != 0):
            self.epsP = self.sigini/E0
            self.sigP = self.sigini

    @property
    def getCopy(self):
        return copy.deepcopy(self)

    @classmethod
    def new_6_para(cls, Fy: float, E0: float, b: float, R0: float, cR1: float, cR2: float):
        return cls(Fy, E0, b, R0, cR1, cR2, 0, 1, 0, 1, 0)

    @classmethod
    def new_3_para(cls, Fy: float, E0: float, b: float):
        return cls.new_6_para(Fy, E0, b, 15, 0.925, 0.15)

    @property
    def getStress(self):
        return self.sig

    def setTrialStrain(self, trial_strain: float):

        Esh = self.b*self.E0
        epsy = self.Fy/self.E0

        # 是否考虑初应力
        if self.sigini != 0:
            epsini = self.sigini/self.E0
            self.eps = trial_strain+epsini
        else:
            self.eps = trial_strain

        deps = self.eps-self.epsP

        self.epsmax = self.epsmaxP
        self.epsmin = self.epsminP
        self.epspl = self.epsplP
        self.epss0 = self.epss0P
        self.sigs0 = self.sigs0P
        self.epsr = self.epssrP
        self.sigr = self.sigsrP
        self.kon = self.konP

        # kon 当前材料处于的加载状态  0 1 2 3

        if self.kon == 0 or self.kon == 3:

            if abs(deps) < 0.00000000000001:
                self.e = self.E0
                self.sig = self.sigini
                self.kon = 3
                return 0
            else:
                self.epsmax = epsy
                self.epsmin = -epsy
                if deps < 0:
                    self.kon = 2  # 应变负方向加载
                    self.epss0 = self.epsmin
                    self.sigs0 = -self.Fy
                    self.epspl = self.epsmin
                else:
                    self.kon = 1      # 应变正方向加载
                    self.epss0 = self.epsmax
                    self.sigs0 = self.Fy
                    self.epspl = self.epsmax

        elif self.kon == 2 and deps > 0:  # 负方向应变卸载
            self.kon = 1
            self.epsr = self.epsP
            self.sigr = self.sigP
            if self.epsP < self.epsmin:
                self.epsmin = self.epsP
            d1 = (self.epsmax-self.epsmin)/(2*self.a4*epsy)
            shft = 1+self.a3*d1**0.8
            self.epss0 = (self.Fy*shft-Esh*epsy*shft-self.sigr +
                          self.E0*self.epsr)/(self.E0-Esh)
            self.sigs0 = self.Fy*shft+Esh*(self.epss0-epsy*shft)
            self.epspl = self.epsmax
        elif self.kon == 1 and deps < 0:     # 正方向应变卸载
            self.kon = 2
            self.epsr = self.epsP
            self.sigr = self.sigP

            if self.epsP > self.epsmax:
                self.epsmax = self.epsP

            d1 = (self.epsmax-self.epsmin)/(2*self.a2*epsy)
            shft = 1.0+self.a1*d1**0.8
            self.epss0 = (-self.Fy*shft+Esh*epsy*shft -
                          self.sigr+self.E0*self.epsr)/(self.E0-Esh)
            self.sigs0 = -self.Fy*shft+Esh*(self.epss0+epsy*shft)
            self.epspl = self.epsmin

        #

        xi = abs((self.epspl-self.epss0)/epsy)
        R = self.R0*(1-(self.cR1*xi)/(self.cR2+xi))
        epsrat = (self.eps-self.epsr)/(self.epss0-self.epsr)
        dum1 = 1+abs(epsrat)**R
        dum2 = dum1**(1/R)

        # 更新当前应力
        self.sig = self.b*epsrat+(1-self.b)*epsrat/dum2
        self.sig = self.sig*(self.sigs0-self.sigr)+self.sigr

        self.e = self.b+(1-self.b)/(dum1*dum2)
        self.e = self.e*(self.sigs0-self.sigr)/(self.epss0-self.epsr)
        return super().setTrialStrain(trial_strain)

    def commitState(self):

        self.epsminP = self.epsmin
        self.epsmaxP = self.epsmax
        self.epsplP = self.epspl
        self.epss0P = self.epss0
        self.sigs0P = self.sigs0
        self.epssrP = self.epsr
        self.sigsrP = self.sigr
        self.konP = self.kon

        self.EnergyP += 0.5*(self.sig+self.sigP)*(self.eps-self.epsP)
        self.eP = self.e
        self.sigP = self.sig
        self.epsP = self.eps

        return super().commitState()

    def revertToLastCommit(self):
        self.epsmin = self.epsminP
        self.epsmax = self.epsmaxP
        self.epspl = self.epsplP
        self.epss0 = self.epss0P
        self.sigs0 = self.sigs0P
        self.epsr = self.epssrP
        self.sigr = self.sigsrP
        self.kon = self.konP
        self.e = self.eP

        return super().revertToLastCommit()

    def revertToStart(self):
        self.EnergyP = 0
        self.konP = 0
        self.kon = 0
        self.eP = 0
        self.sigP = 0
        self.sig = 0
        self.eps = 0
        self.e = self.E0

        self.epsmaxP = self.Fy/self.E0
        self.epsminP = -self.epsmaxP
        self.epsplP = 0
        self.epss0P = 0
        self.sigs0P = 0
        self.epssrP = 0
        self.sigsrP = 0

        if (self.sigini != 0):
            self.epsP = self.sigini/self.E0
            self.sigP = self.sigini
        return super().revertToStart()


class Concrete02(Material):

    def __init__(self, fc: float, epsc0: float, fcu: float, epscu: float, rat: float, ft: float, Ets: float) -> None:

        super().__init__()
        self.fc = fc
        self.epsc0 = epsc0
        self.fcu = fcu
        self.epscu = epscu
        self.rat = rat
        self.ft = ft
        self.Ets = Ets

        self.ecminP = 0
        self.deptP = 0

        self.ecmin = 0
        self.dept = 0

        self.eP = 2.0*self.fc/self.epsc0
        self.epsP = 0
        self.sigP = 0
        self.eps = 0
        self.sig = 0
        self.e = 2.0*self.fc/self.epsc0

    @property
    def getCopy(self):
        return copy.deepcopy(self)

    @property
    def getStress(self):
        return self.sig

    def setTrialStrain(self, trial_strain: float):

        ec0 = self.fc*2/self.epsc0

        self.ecmin = self.ecminP
        self.dept = self.deptP

        self.eps = trial_strain
        deps = self.eps-self.epsP
        if abs(deps) < 0.00000000000000001:
            return 0
        if self.eps < self.ecmin:
            self.sig, self.e = self.Compr_Envlp(self.eps)
            self.ecmin = self.eps
        else:
            epsr = (self.fcu-self.rat*ec0*self.epscu)/(ec0*(1-self.rat))
            sigmr = ec0*epsr
            self.espr = epsr
            self.sigmr = sigmr
            sigmm, dumy = self.Compr_Envlp(self.ecmin)
            er = (sigmm-sigmr)/(self.ecmin-epsr)
            ept = self.ecmin-sigmm/er

            if self.eps <= ept:
                sigmin = sigmm+er*(self.eps-self.ecmin)
                sigmax = er*0.5*(self.eps-ept)
                self.sig = self.sigP+ec0*deps
                self.e = ec0
                if self.sig <= sigmin:
                    self.sig = sigmin
                    self.e = er
                elif self.sig >= sigmax:
                    self.sig = sigmax
                    self.e = 0.5*er
            else:
                epn = ept+self.dept
                if(self.eps <= epn):
                    sicn, self.e = self.Tens_Envlp(self.dept)
                    if self.dept != 0:
                        self.e = sicn/self.dept
                    else:
                        self.e = ec0
                    self.sig = self.e*(self.eps-ept)
                else:
                    epstmp = self.eps-ept
                    self.sig, self.e = self.Tens_Envlp(epstmp)
                    self.dept = self.eps-ept

        return super().setTrialStrain(trial_strain)

    def Compr_Envlp(self, epsc: float):
        Ec0 = 2.0*self.fc/self.epsc0
        ratlocal = epsc/self.epsc0

        if (epsc >= self.epsc0):
            sigc = self.fc*ratlocal*(2-ratlocal)
            Ect = Ec0*(1-ratlocal)
        else:
            if(epsc > self.epscu):
                sigc = (self.fcu-self.fc)*(epsc-self.epsc0) / \
                    (self.epscu-self.epsc0)+self.fc
                Ect = (self.fcu-self.fc)/(self.epscu-self.epsc0)
            else:
                sigc = self.fcu
                Ect = 0.00000000000001
        return sigc, Ect

    def Tens_Envlp(self, epsc: float):
        Ec0 = 2.0*self.fc/self.epsc0

        eps0 = self.ft/Ec0
        epsu = self.ft*(1/self.Ets+1/Ec0)
        if epsc <= eps0:
            sigc = epsc*Ec0
            Ect = Ec0
        else:
            if epsc <= epsu:
                Ect = -self.Ets
                sigc = self.ft-self.Ets*(epsc-eps0)
            else:
                Ect = 0.0000000000001
                sigc = 0

        return sigc, Ect

    def commitState(self):
        self.ecminP = self.ecmin
        self.deptP = self.dept

        self.eP = self.e
        self.sigP = self.sig
        self.epsP = self.eps
        return super().commitState()

    def revertToLastCommit(self):
        self.ecmin = self.ecminP
        self.dept = self.deptP

        self.e = self.eP
        self.sig = self.sigP
        self.eps = self.epsP
        return super().revertToLastCommit()

    def revertToStart(self):

        self.ecminP = 0
        self.deptP = 0

        self.eP = 2.0*self.fc/self.epsc0
        self.epsP = 0
        self.sigP = 0
        self.eps = 0
        self.sig = 0
        self.e = 2.0*self.fc/self.epsc0
        return super().revertToStart()


if __name__ == "__main__":

    figure = plt.figure()
    ax1 = figure.add_subplot(121)
    ax2 = figure.add_subplot(122)
    # Concrete_check

    # concrete=Concrete02(-50,-0.002,-10,-0.01,0.003,10,30/0.002*2/10)
    concreteOrigin = ConcreteCM(-45, -0.002, 30000, 1.2, 1.5,
                                0.67, 5, 0.002, 1.3, 2, 0.57)
    concrete = concreteOrigin.getCopy
    print("id compare", id(concreteOrigin), "----------", id(concrete))
    concrete_stress = []
    steel = Steel02.new_3_para(345, 345/0.002, 0.01)
    steel_stress = []
    basestrain = np.linspace(0, 0.01, 2000)
    strain = basestrain
    strain = np.concatenate((strain, [i for i in reversed(basestrain)]))
    strain = np.concatenate((strain, -basestrain))
    strain = np.concatenate((strain, [-i for i in reversed(basestrain)]))
    strain = np.concatenate((strain, 2*basestrain))
    strain = np.concatenate((strain, [2*i for i in reversed(basestrain)]))
    strain = np.concatenate((strain, -2*basestrain))
    strain = np.concatenate((strain, [-2*i for i in reversed(basestrain)]))
    strain = np.concatenate((strain, 3*basestrain))
    strain = np.concatenate((strain, [3*i for i in reversed(basestrain)]))

    for i in strain:
        concrete.setTrialStrain(-i)
        concrete.commitState()
        concrete_stress.append(concrete.getStress)
        steel.setTrialStrain(i)
        steel.commitState()
        steel_stress.append(steel.getStress)
    ax1.plot(-strain, concrete_stress)
    ax1.set_title('concrete')
    ax2.plot(strain, steel_stress)
    ax2.set_title('steel')
    plt.show()
