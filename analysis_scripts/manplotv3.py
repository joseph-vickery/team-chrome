
import sqlite3
import pandas as pd
pd.options.display.max_colwidth = 1000
import matplotlib.pyplot as plt
import numpy as np
from bioinfokit import visuz
from scipy.stats import uniform
from scipy.stats import randint 
from qmplot import manhattanplot
import seaborn as sns

def create_connection(db_file):
    con=None
    try:
        con=sqlite3.connect(db_file)

    except OSError as e:
        print(e)
    
    return con

def data_pandas(con):
    
    #con=sqlite3.connect("GC.db")
    cur=con.cursor()
    db_query= "SELECT snp, p_value, location FROM gwas" # WHERE location =' "


     # execute the query and retrieve the data as a list of tuples  
    data=con.execute(db_query).fetchall()
    
    #dictionary
    data_dict = {'snp': [row[0] for row in data],
                 'p_value':[row[1] for row in data],
                 'location': [row[2] for row in data]}
    #data_dict['p_value']=list(map(float,data_dict['p_value'])) #tying to convert p value to float from dictionary      #convert into a pandas
    df=pd.DataFrame.from_dict(data_dict)
    

    #change structure of the loop-- try iterows as seem to be overwriting everything 
    i=0
    #have a counter that starts with 0
    for p_value_f in df['p_value']:  # produces this for all values 4.000000e-08
        #df['p_value_f']=float(p_value_f.replace(' x 10', 'e')) #the replace is approved
        #print(float(p_value_f.replace(' x 10', 'e')))
        df.at[i,'p_value'] = p_value_f.replace(' x 10', 'e')
        i+=1
            
        #issue-so basically its changing evry value in column to last value that we loop through

    df['p_value']=df['p_value'].astype(float) #make the p_value column a float

        #create a df coloumn for the chromosome number
    df['chr']=np.vectorize(lambda x: x.split(':')[0])(np.array(df['location'],dtype=str)) #for new column called chromosome, take where there is a : in 'location', split and take the values before it and transalte to new column.
    print(df)
    #adjust position coloumn to only show the bits after :
    df['location']=np.vectorize(lambda x:x.split(':')[1])(np.array(df['location'],dtype=str)) #split and keep the values after the dleimiter by [1], overwrote the locarion column
    df['location']=df['location'].astype(int)
    #-log_10 pvalue
    df['-log_pv']=-np.log10(df.p_value) #convert to -log10 pvalue and store in new column of dataframe

    #generating plot works

    #group each snp by chromosome
    df=df.sort_values(['chr','location'])  #inorder of location 
    df.reset_index(inplace=True, drop=True); df['i']=df.index
    print(df)

    #generate plot
    plot=sns.relplot(data=df, x='i', y='-log_pv', aspect=4,
                    hue='chr', palette='bright', legend=None, linewidth=0)
    chrom_df=df.groupby('chr')['i'].median()
    plot.ax.set_xlabel('chr'); plot.ax.set_xticks(chrom_df);
    plot.ax.set_xticklabels(chrom_df.index)
    plot.fig.suptitle('Manhattan plot showing association between SNPs and Diabetes Mellitus 1 ')
    plt.show()

def main():
    
    con=create_connection("GC.db")

    with con:
        
        print("3.Query by column")
        data_pandas(con)

if __name__=='__main__':
    main()
        
