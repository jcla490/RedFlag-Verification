from verification_funcs import verify
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd



sns.set()

########################################################################################################################
# 90th PERCENTILE FIRES, CAUSES, FORESTED, FD INDICES                                                                  #
########################################################################################################################

# All causes POD_SS - 0.264180
# Human POD_SS - 0.140523
# Lightning POD_SS - 0.434921
# Forest YES POD_SS - 0.254910
# Forest NO POD_SS - 0.334467
# 1000-hr FM - 0.477619
# 100-hr FM - 0.440048
# ERC - 0.426711
# BI -  0.428538

df = pd.DataFrame({'Cause': ['All', 'Human', 'Lightning'], 'POD_SS': [0.264180, 0.140523, 0.434921]})
df2 = pd.DataFrame({'Land Cover': ['Forested', 'Non-Forested'], 'POD_SS': [0.254910, 0.334467]})
df3 = pd.DataFrame({'Fire Danger': ['ERC', 'BI', 'FM1000', 'FM100'], 'POD_SS': [0.426711, 0.428538, 0.477619, 0.440048]})

fig, axes = plt.subplots(1, 3, figsize=(10, 7), sharey=True)

ax = sns.barplot(x='Cause', y='POD_SS', data=df, color='b', ax=axes[0])
ax1 = sns.barplot(x='Land Cover', y='POD_SS', data=df2, color='g', ax=axes[1])
ax2 = sns.barplot(x='Fire Danger', y='POD_SS', data=df3, color='r', ax=axes[2])

ax.set_xlabel('Cause', fontsize=16)
ax1.set_xlabel('Land Cover', fontsize=16)
ax2.set_xlabel(r'$P_{90}$' + ' Fire Danger', fontsize=16)
ax.set_ylabel(r'$POD_{SS}$')

ax1.get_yaxis().set_visible(False)
ax2.get_yaxis().set_visible(False)

plt.subplots_adjust(top=0.9)
fig.suptitle(r'$POD_{SS}$ for 90th Percentile Fires, All Zones')

plt.show()





