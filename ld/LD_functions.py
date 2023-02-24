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
#function for making a text file of LD r^2 values for each rsid combination.
def ld_file_maker(ld_dict, population):
    rsids = [] 
    #seperating out the rsid values in each pair:
    for k in ld_dict.keys():
        if k[0] not in rsids:
            rsids.append(k[0])
        else:
            rsids.append(k[1])
   
   #creating file with rsids and population as the name of the file
    ld_file = open('LD_{rsids}_{population}.txt'.format(rsids='_'.join(rsids), population=population), 'w')

    #creating header: iterate through dict keys, writing file name and tab to file 
    ld_file.write('Population: {population}'.format(population=population) + '\n')
    for pair in ld_dict.keys():
        ld_file.write(pair[0]+ ', ' +pair[1] + '\t')
    ld_file.write('\n')

    #iterate through values of dict, retrieving filename for corresponding dict value using list comprehnsion, writing to file.
    for x in ld_dict.values():
        ld_file.write(str(x) + '\t')
    ld_file.close()
    return ld_file

############################################################################

def ld_graph_maker(ld_dict, rsid_list): 
    rsid1 = []
    rsid2 = []
    values = []
    #seperating out rsid pairs and corresponding values:
    for pair in list(ld_dict.keys()): 
        rsid1.append(pair[0])
        rsid2.append(pair[1])
        values.append(ld_dict[pair])
    
    #outputting data into df 
    df = pd.DataFrame({'rsid1':rsid1, 'rsid2':rsid2, 'values':values})

    #transforming df into a symmetrical matrix, filling missing values with 0
    dfld = df.pivot(*df)
    ret = dfld.add(dfld.T, fill_value=0).fillna(0)

    #creating the mask for the triangular heatmap
    mask = np.triu(np.ones_like(ret))

    #creating the heat map using seaborn packages 
    dataplot = sb.heatmap(ret, cmap="RdYlGn_r", annot=True, mask=mask)
    plt.show()
    
    return dataplot, ret

def ld_csv_maker(df, ld_dict, population):
    rsids = [] 
    #seperating out the rsid values in each pair:
    for k in ld_dict.keys():
        if k[0] not in rsids:
            rsids.append(k[0])
        else:
            rsids.append(k[1])
    
    file = df.to_csv('LD_{rsids}_{population}.csv'.format(rsids='_'.join(rsids), population=population), sep=',')
    print(file)
    return file