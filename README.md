# Team Google Chrome - Type I Diabetes Web App
> This web application contains information about SNPs related to Type I diabetes 

## Description 

This web application was designed to make it easy to obtain information related to Type I Diabetes single nucleotide polymorphisms (SNPs). Genome-wide association studies (GWAS) are useful to identify large numbers of genetic variants associated with diseases. However, this information can be overwhelming to parse through, and related information is difficult to source. This software was developed in order to make SNP information related to Type 1 Diabetes Mellitus easier to access, especially for clinicians. Thus when a clinician has a research question, various genomic, functional, population, and clinical information can be accessed from one database. 

This application returns a table containing the rsID, mapped gene(s), p-value, chromosome number and position, the reference allele, the alternative allele, the minor allele, and the allele frequency for 5 significant geographic populations. It also returns raw and Phred CADD scores for each SNP. For each mapped gene associated with the rsID, a table will populate below the first containing the relevant GO term information. Finally, the software also provides analysis related to linkage disequilibrium between SNPs and, for queries related to chromosome region, produces a manhattan plot describing the p-values related to the SNPs.

## Instructions

The user interface has been designed to be simple and easy to use. Here is how to run the web app.

### Downloading the app: 

- Download this repository to your local computer. 
- Download the libraires and packages needed for the application to run by using the requirements.txt file 
- Run the file webapp.py with python, this should create a temporary server on which the application runs 
- For a more detailed explaination of the github repository - see the repository layout section

### Navigating the app: 

- Upon opening the application, you will be taken to the homepage where you can query SNPs based on rsID, chromosome, genomic position or mapped gene. For more information on making queries, see the making queries section. 
- Upon hitting submit, you will either be taken to a results page or an error page. 
  - If there is an error, make sure your query has been entered correctly and try again. If the error persists, then there is likely no information related to that query 
- To perform linkage disequilibirum analysis, scroll the down to the bottom of the page, select the SNPs of interest and the population and press submit. 
- If you make a region-related query, you will also see the manhattan plot containing the p-values at the bottom of the results page. 

### Making Queries:

**rsID**: If you would like information pertaining to a specific SNP, type it's rsID into the search bar. The structure of this table is the base information returned for each query. 

**Chromosome number:** If you want to query the database for all information relevant to a particular chromosome, you should enter “chr_” with no space between 'chr' and the number. A space will cause the programe to error. The current build of the application only contains information related to chromosome 6. This will be expanded to every chromosome with further development.

**Chromosome position:** If you want to query the database for a specific range of coordinates on the chromosome, type in “starting position,ending position” and this would return results located between the two coordinates entered. As the database only has data from chromosome 6, this information is assumed and so you can omit the 6 identifier at the start of their query. For example, if you want to query between 6:32421478 and 6:170063801, type in “32421478,170063801”. 

**Mapped gene:** If you want to query the database for all the information pertaining to a mapped gene, type in the gene name. This query is not case-sensitive.  

## Repository Layout ##
```
.

├── LD_files            #contains LD matrix text file which is downloaded in LD analysis page
│   └── LD_matrix.csv
├── analysis_scripts    #contains LD functions used for LD analysis
│   └── LD_functions.py
├── data                #contains the data used to create database and code to build database (SNP_code.txt)
│   ├── SNP_code.txt
│   ├── CADD.csv
│   ├── T1D_association.csv
│   ├── chr6_df_cleaned.csv
│   ├── gwas.csv
│   └── pop_freq.txt
├── templates           #contains html templates for web page rendering
│   ├── Chromosome.html
│   ├── LD.html
│   ├── Map.html
│   ├── Region.html
│   ├── base.html
│   ├── index.html
│   └── search.html
├── GC.db             #database used for web application
├── README.md         #Read Me file -  see for app instructions
├── requirements.txt  #use to download libraries and packages needed for app
└── webapp.py         #code whihc runs application via Flask
```

## Credits ##
Alex Vasquez <br>
Maddy May Creach <br>
Kelis Rossi <br>
Joseph Vickery <br>
