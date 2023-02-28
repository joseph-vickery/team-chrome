from LD_functions import ld_file_maker, ld_dict_maker, ld_graph_maker, ld_csv_maker
import seaborn as sns
import matplotlib.pyplot as plt

ld_dict = (ld_dict_maker(['rs1770', 'rs9273367', 'rs212408'], population='ALL'))

ld_file_maker(ld_dict, 'ALL')

ret, mask = ld_graph_maker(ld_dict)
file = ld_csv_maker(ret, ld_dict, 'ALL' )


sns.heatmap(ret, cmap="RdYlGn_r", annot=True, mask=mask)
plt.show()