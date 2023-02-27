#webapp packages
from flask import Flask, render_template, url_for, redirect

#database package
import sqlite3 as db
#data manipulation package
import pandas as pd

#import libraries needed to create and process forms
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired

#Creates the flask application object
app = Flask(__name__)
#Just a key for production. dont worry about it
app.config['SECRET_KEY'] = 'PURPLE HAZE 123'

#Created a class to establish what the user searches for in the web app
class QueryForm(FlaskForm):
    snp_name = StringField('Enter a valid rsID: ', validators=[InputRequired()])
    submit = SubmitField('Submit')

#This is the home page 
@app.route('/', methods = ['GET', 'POST'])
def index():
    form = QueryForm()
    snp_name = None
    if form.validate_on_submit():
        snp_name = form.snp_name.data
        #Redirect user to snp page if rs is typed
        if snp_name[:2]== "rs":
            print('YAY IT HAS AN rsID')
            return redirect(url_for('SNP', snp_name= snp_name))
        
        #Redirect user to chromosome page if chr is typed
        if snp_name[:3] == "chr":
            print('Going to chromosome page')
            return redirect(url_for('Chromosome',snp_name=snp_name))

        #Redirect user to region page if they enter two locations separated by a comma
        elif "," in snp_name:
            print('Going to Region page')
            return redirect(url_for('Region', snp_name=snp_name))

        #redirect to mapped gene page if the beginning != rs or chr or ,
        elif snp_name != 'rs' or snp_name != 'chr' or "," not in snp_name:
            print('REDIRECT TO MAPPED GENE')
            return redirect(url_for('MAPPED_GENE', snp_name=snp_name))
        
        print('\n\n\n'+snp_name+'\n\n\n')
        #redirects to the "SNP" url down below app route
        return redirect(url_for('SNP', snp_name= snp_name))

        
    return render_template("index.html", form = form, snp_name=snp_name)

#SNP page redirect to here where we queried all info based on that gene and rsID
@app.route('/SNP/<snp_name>')
def SNP(snp_name):
    try:
    #connecting to database every time we generate a new route
        con = db.connect("GC.db", check_same_thread=False)
        cursor = con.cursor() #this allows us to query our database  
        #this is selecting specific info on snp
        snp_name = snp_name.lower()
        #queried data is executed below to get all info from tables
        cursor.execute ("""SELECT  gwas.snp, gwas.Gene_name,gwas.p_value,population.Chromosome,
        population.Position, population.REF_Allele, 
        population.ALT_Allele, population.Minor_Allele, population.AFR_Frequency,
        population.AMR_Frequency, population.EAS_Frequency, population.EUR_Frequency, 
        population.SAS_Frequency

        FROM gwas 
        INNER JOIN CADD ON gwas.snp = CADD.snp 
        INNER JOIN population on CADD.snp = population.snp 
        WHERE gwas.snp= '%s' """ % snp_name) 
        #^^^^Very important to include '%s' because that is substituted with snp_name^

        search_snp = cursor.fetchall()

    ##########   GO TERM SEARCH   ##############
    #query for GO terms from gene_name for SNP input
        
        for row in search_snp:
            gene_name = row[1]

    #If there are multiple mapped genes per SNP then the string needs to be separated into gene 1 and gene 2
        if ',' in gene_name:
            sep_genes = gene_name.split(',')
            gene1, gene2 = [sep_genes[i] for i in (0, 1)]
            gene2 = gene2.strip()

#query for GO terms from gene_name for SNP input
#if there are two mapped genes run two separate queries for both of the genes
        if ',' in gene_name:
            
            cursor = con.cursor()
            cursor.execute ("""SELECT * 
                FROM GO 
                WHERE Gene_name="%s" """ % gene1)
            
            #set search_GO = "" for the html to output the correct query corresponding to the input
            search_GO = ""

            search_GO1 = cursor.fetchall()

            cursor = con.cursor()
            cursor.execute ("""SELECT * 
                FROM GO 
                WHERE Gene_name="%s" """ % gene2)
                    
            search_GO2 = cursor.fetchall()


#if there is only one mapped gene run the query once            

        else:
            cursor = con.cursor()
            cursor.execute ("""SELECT * 
                FROM GO 
                WHERE Gene_name="%s" """ % gene_name)
                        
            search_GO = cursor.fetchall()

            #set search_GO1 and search_GO2 = "" for the html to output the correct query corresponding to the input
            search_GO1 = ""
            search_GO2 = ""

            
#Finish the search hmtl and see if it connects.
        return render_template("search.html", name=snp_name, search_snp=search_snp, search_GO=search_GO, search_GO1=search_GO1, search_GO2=search_GO2, dumb = "stupid")
    except:
        return "No information availabe for rs#: %s." % snp_name

@app.route('/Chromosome/<snp_name>')
def Chromosome(snp_name):

    try:
    #connecting to database
        con = db.connect("GC.db", check_same_thread=False)
        cursor = con.cursor() #this allows us to query our database  
    
        snp_name = snp_name.lower()
        #Cursor.execute function allows use to choose what tables and columns we can include within our search.
        cursor.execute ("""SELECT  gwas.snp, gwas.Gene_name,gwas.p_value,
        population.Chromosome, population.Position, population.REF_Allele, 
        population.ALT_Allele, population.Minor_Allele, population.AFR_Frequency, 
        population.AMR_Frequency, population.EAS_Frequency, population.EUR_Frequency, population.SAS_Frequency

        FROM gwas
        INNER JOIN population
        on gwas.snp = population.snp
        WHERE population.Chromosome= '%s' """ % snp_name)
        search_snp = cursor.fetchall()


        return render_template("Chromosome.html", name=snp_name,search_snp=search_snp)
    except:
        return "No information availabe for rs#: %s." % snp_name




@app.route('/MAPPED_GENE/<snp_name>')
def MAPPED_GENE(snp_name):

    try:
    #connecting to database every time we generate a new route
        con = db.connect("GC.db", check_same_thread=False)
        cursor = con.cursor() #this allows us to query our database  
        #this is selecting specific info on snp
        snp_name = snp_name.upper()
        #queried data is executed below to get all info from tables
        cursor.execute ("""SELECT  gwas.snp, gwas.Gene_name,gwas.p_value,population.Chromosome,
        population.Position, population.REF_Allele, 
        population.ALT_Allele, population.Minor_Allele, population.AFR_Frequency,
        population.AMR_Frequency, population.EAS_Frequency, population.EUR_Frequency, 
        population.SAS_Frequency

        FROM gwas 
        INNER JOIN CADD ON gwas.snp = CADD.snp 
        INNER JOIN population on CADD.snp = population.snp 
        WHERE gwas.Gene_name= '%s' """ % snp_name) 
        #^^^^Very important to include '%s' because that is substituted with snp_name^

        search_snp = cursor.fetchall()
        for row in search_snp:
            gene_name = row[1]

        cursor = con.cursor()
        cursor.execute ("""SELECT * 
        FROM GO 
        WHERE Gene_name="%s" """ % gene_name)

        GO_search = cursor.fetchall()

        return render_template("Map.html", name=snp_name, search_snp=search_snp, GO_search=GO_search)
    except:
        return "No information availabe for %s." % snp_name


@app.route('/Region/<snp_name>')
def Region(snp_name):
    try:
        con = db.connect("GC.db", check_same_thread=False)
        cursor = con.cursor()

    
        #separate the two locations from the user input by a comma
        sep_genes = snp_name.split(',')
        print(sep_genes)
        #sorted takes the list and arranges from lowest to greatest.
        sorted_genes = sorted(sep_genes)
        gene1, gene2 = [sorted_genes[i] for i in (0, 1)]
        gene2 = gene2.strip()
        print(gene1)
        print(gene2)


            ########snp search######

        #queried data is executed below to get all info from tables
        cursor.execute ("""SELECT  gwas.snp, gwas.Gene_name,gwas.p_value,population.Chromosome,
        population.Position, population.REF_Allele, 
        population.ALT_Allele, population.Minor_Allele, population.AFR_Frequency,
        population.AMR_Frequency, population.EAS_Frequency, population.EUR_Frequency, 
        population.SAS_Frequency
        FROM gwas 
        INNER JOIN CADD ON gwas.snp = CADD.snp 
        INNER JOIN population on CADD.snp = population.snp 
        WHERE CAST(SUBSTR(gwas.location,3,15) AS UNSIGNED) BETWEEN '%s' and '%s' """ % (gene1,gene2) )
        #^^^^Very important to include '%s' because that is substituted with snp_name^

        search_snp = cursor.fetchall()
        

        ##########   GO TERM SEARCH   ##############
        #query for GO terms from gene_name for SNP input

        #Initialize a list of all of the mapped genes for every snp within the user's input region
        gene_name_list = []
        for row in search_snp:
           gene_name = row[1]
           gene_name_list.append(gene_name)
        

    #Initialize a list to hold all of the queries
        all_region_GO_queries=[]
        
        #iterate through the gene name list and limit the query to 1 per mapped gene
        for item in gene_name_list:
            
            cursor = con.cursor()
            cursor.execute ("""SELECT * 
                FROM GO 
                WHERE Gene_name="%s" 
                LIMIT 1""" % item)
            
            #for every query fetchall the information
            search_item = cursor.fetchall()

            #in order to create a list iterate through the fetchall and separate the information
            for row in search_item:
                gene_name=row[1]
                go_term_accession=row[2]
                go_name=row[3]
                go_definition=row[4]
                go_evidence=row[5]
                go_domain=row[6]

                #combine the query information into one list and append this list to list containing all the mapped gene queries
                new_query = [gene_name, go_term_accession, go_name, go_definition, go_evidence, go_domain]
                all_region_GO_queries.append(new_query)
        
          

    except:
        return "No information availabe for %s." % snp_name


    return render_template("Region.html", name=snp_name, search_snp=search_snp, all_region_GO_queries=all_region_GO_queries)



if __name__ == "__main__":
    app.run(debug=True, port=8001)


