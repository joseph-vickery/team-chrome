#webapp packages
from flask import Flask, render_template, url_for, redirect, request

#database package
import sqlite3 as db
#data manipulation package
import pandas as pd

#import libraries needed to create and process forms
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField
from wtforms.validators import InputRequired, DataRequired

#importing LD functions 
from ld.LD_functions import ld_dict_maker, ld_file_maker

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
        elif snp_name[:3] == "chr":
            print('Going to chromosome page')
            return redirect(url_for('Chromosome',snp_name=snp_name))

#TEST ELSE STATEMENT##
        #else:
            redirect(url_for('MAPPED GENE', snp_name=snp_name))
        #elif snp_name 
        #elif type(snp_name) is int:
        #need to make region url
        # this else stamenet can be used for mapped gene function
        #else:
            #print("yay it works here")
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


        cursor = con.cursor()
        cursor.execute ("""SELECT * 
        FROM GO 
        WHERE Gene_name="%s" """ % gene_name)
                        
        search_GO = cursor.fetchall()

        for row in search_GO:
            if row[3] == None:
                continue
            else:
                search_gene = row[1]
                accession = row[2]
                print(accession)
                go_term_name = row[3]
                print(go_term_name)
                go_term_def = row[4]
                print(go_term_def)
                go_term_evidence = row[5]
                print(go_term_evidence)
                go_domain = row[6]
                print(go_domain)
            
#Finish the search hmtl and see if it connects.
        return render_template("search.html", name=snp_name, search_snp=search_snp, search_GO=search_GO)
    except:
        return "No information availabe for rs#: %s." % snp_name

@app.route('/Chromosome/<snp_name>', methods = ['GET', 'POST'])
def Chromosome(snp_name):
    try:
    #connecting to database
        con = db.connect("GC.db", check_same_thread=False)
        cursor = con.cursor() #this allows us to query our database  

        snp_name = snp_name.lower()
        #Cursor.execute function allows use to choose what tables and columns we can include within our search.
        #i put the query in a seperate variable just so easier to see/manipulate 
        query = ("""SELECT  gwas.snp, gwas.Gene_name,gwas.p_value,
        population.Chromosome, population.Position, population.REF_Allele, 
        population.ALT_Allele, population.Minor_Allele, population.AFR_Frequency, 
        population.AMR_Frequency, population.EAS_Frequency, population.EUR_Frequency, population.SAS_Frequency

        FROM gwas
        INNER JOIN population
        on gwas.snp = population.snp
        WHERE population.Chromosome= '%s' """ % snp_name)
        cursor.execute(query)
        
        search_snp = cursor.fetchall()
        ####code for rsid list starts here:
        #takes the first point (the rsid) from the query result so becomes list of rsids
        rsIDs = [] 
        result = search_snp
        rsIDs = [i[0] for i in result]

        #defining class for form inside the function so the choices for the selectable list are specific to the query:
        #rsid is the multiplefield list, submit is submit button
        class AnalysisForm(FlaskForm):
            rsid = SelectMultipleField('rsID list', validators=[DataRequired()], choices=rsIDs)
            submit = SubmitField("Submit") 
        
        form = AnalysisForm(request.form)
        ##this doesnt work :( )
        if request.method == 'POST' and form.validate():
            print("POST request and form is valid")
            rsid = form.rsid.data
            return redirect(url_for('analysis', rsid=rsid))
        
        return render_template("Chromosome.html", name=snp_name,search_snp=search_snp, rsIDs=rsIDs,form=form)
    except:
        return "No information availabe for rs#: %s." % snp_name

@app.route('/analysis/<rsid>')
def Linkage_analysis(rsIDs): 
    print(rsIDs)

#@app.route('/MAPPED GENE/<snp_name>')
#def MAPPED_GENE(snp_name):

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

        return render_template("Map.html", name=snp_name, search_snp=search_snp)
    except:
        return "No information availabe for %s." % snp_name

if __name__ == "__main__":
    app.run(debug=True)

