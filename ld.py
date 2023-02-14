def LD(rsid1,rsid2): 
    import requests, sys

    rsid1 = rsid1.lower()
    rsid2 = rsid2.lower()

    server = "https://rest.ensembl.org"
    #ext = "/ld/human/pairwise/{rsid1}/{rsid2}".format(rsid1=rsid1, rsid2=rsid2)
    ext = '/ld/human/pairwise/rs73043122/rs1015166' 
    print(ext)

    r = requests.get(server+ext, headers={"Content-Type" : "application/json"})
    
    if not r.ok:
        r.raise_for_status()
        sys.exit()
    
    decoded = r.json()
    print(repr(decoded))

    if decoded == []: 
        print('Sorry there is no linkage disequilibrium data available for that combination of SNPs!')
    

print(LD('rs73043122', 'rs78824139'))




