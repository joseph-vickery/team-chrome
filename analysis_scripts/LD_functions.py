#importing all the packages
import requests
import sys
import pandas as pd 
import io
import numpy as np
import itertools 
import time
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sb


############################################################################

#function for retrieving LD values from LDlink API, making a dictionary of LD values 
# to be used for downloadable file and graph production. 

#function takes list of rsids as strings and population of interest also as a string
def ld_dict_maker(rsid_list, population): 
    LD_dict= {}
    #create object of all unique combinations of rsids, iterate through each pair
    # and retrieve the LD value table from ldlink website
    for pair in itertools.combinations(rsid_list, r=2): 
        rsid1 = pair[0]
        rsid2 = pair[1]
        server = "https://ldlink.nci.nih.gov/LDlinkRest/ldpop?"
        #inputs rsid and population into url for retrieval
        ext = 'var1={rsid1}&var2={rsid2}&pop=ALL&r2_d=r2&genome_build=grch38&token=b56c4bea4225'.format(rsid1=rsid1, rsid2=rsid2)
        
        #Uses server to get specified LD values, try and except used to not overload server 
        #if this bit doesn't work - try a different IP address. 
        response = ''
        while response == '':
            try:
                response = requests.get(server+ext, headers={"Content-Type" : "application/json"})
                break
            except:
                print("Connection refused by the server..")
                print("Let me sleep for 5 seconds")
                print("ZZzzzz...")
                time.sleep(5)
                print("Was a nice sleep, now let me continue...")
                continue

        if not response.ok:
            response.raise_for_status()
            sys.exit()
        #decoding response into readable format
        decoded = (response._content).decode("utf-8") 

        if decoded == []: 
            print('Sorry there is no linkage disequilibrium data available for that combination of SNPs!')
    
        #transforming data into a pandas dataframe
        ld_string_data = io.StringIO(decoded)
        ld_df = pd.read_csv(ld_string_data, sep='\t')

        #isolating r^2 value of specified population
        ld_line = ld_df.loc[ld_df['Abbrev'] == population]
        r2 = float(ld_line['R2'])

        #inputting said data into dictionary 
        LD_dict[rsid1, rsid2] = r2

    return LD_dict


############################################################################

def ld_graph_maker(ld_dict): 
    rsid1 = []
    rsid2 = []
    values = []
    #seperating out rsid pairs and corresponding values:
    ld_sort = sorted(ld_dict.items(), key=lambda x:x[1], reverse=False)
    ld_dict_sort = dict(ld_sort)
    for pair in list(ld_dict_sort.keys()): 
        rsid1.append(pair[0])
        rsid2.append(pair[1])
        values.append(ld_dict_sort[pair])
    
    #outputting data into df 
    df = pd.DataFrame({'rsid1':rsid1, 'rsid2':rsid2, 'values':values})

    #transforming df into a symmetrical matrix, filling missing values with 0
    dfld = df.pivot(*df)
    ret = dfld.add(dfld.T, fill_value=0).fillna(0)

    #creating the mask for the triangular heatmap
    mask = np.triu(np.ones_like(ret))
    
    return ret, mask

##########csv maker for LD values ################

def ld_csv_maker(df):
    filename = 'LD_matrix.csv'
    df.to_csv(sep=',', path_or_buf = "LD_files/{filename}".format(filename=filename))
    return filename