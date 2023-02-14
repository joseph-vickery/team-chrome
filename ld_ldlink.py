import requests
import sys
import pandas as pd 
import io

rsid1 = 'rs73043122'
rsid2 = 'rs1770'

server = "https://ldlink.nci.nih.gov/LDlinkRest/ldpop?"
ext = 'var1={rsid1}&var2={rsid2}&pop=ALL&r2_d=r2&genome_build=grch38&token=b56c4bea4225'.format(rsid1=rsid1, rsid2=rsid2)


r = requests.get(server+ext, headers={"Content-Type" : "application/json"})

if not r.ok:
    r.raise_for_status()
    sys.exit()

decoded = (r._content)
decoded = decoded.decode("utf-8") 


if decoded == []: 
    print('Sorry there is no linkage disequilibrium data available for that combination of SNPs!')
    
ld_string_data = io.StringIO(decoded)
ld_df = pd.read_csv(ld_string_data, sep='\t')

print(ld_df)

