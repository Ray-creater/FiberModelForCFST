from material import Concrete02, ConcreteCM, Steel02
from section import Section, Steel02, Concrete02, ConcreteCM
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

strains = np.linspace(0, 0.2, 100)

for r in np.linspace(0.1, 0.9, 9):
    concrete = ConcreteCM(-120, -0.008, 30000, r, 5, 0.56, 20, 0.0002, 1.5, 3, 0.67)
    stress = []
    for strain in strains:
        concrete.setTrialStrain(-strain)
        concrete.commitState()
        stress.append(-concrete.getStress)
    plt.plot(strains, stress, label=f"r:{r}")

plt.legend()
plt.show()
