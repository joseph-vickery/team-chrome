from LD_functions import ld_file_maker, ld_dict_maker, ld_graph_maker, csv_maker


ld_dict = (ld_dict_maker(['rs1770', 'rs9273367', 'rs212408'], population='ALL'))

#ld_file_maker(ld_dict, 'ALL')

graph, df = ld_graph_maker(ld_dict, rsid_list=['rs1770', 'rs9273367', 'rs212408'])

file = csv_maker(df, ld_dict, 'ALL' )

