#webapp packages
from flask import Flask, render_template, url_for, redirect, request, session, render_template_string, Response, send_from_directory
from flask_debugtoolbar import DebugToolbarExtension
#database package
import sqlite3 as db
#data manipulation package
import pandas as pd

#import libraries needed to create and process forms
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, Form, SelectField
from wtforms.validators import InputRequired, DataRequired

#for LD functions 
from ld.LD_functions import ld_dict_maker, ld_graph_maker, ld_csv_maker
import matplotlib 
matplotlib.use('Agg') 
import matplotlib.pyplot as plt, mpld3
import seaborn as sns
import numpy as np
import io
from io import BytesIO
from matplotlib.figure import Figure
import base64


#Creates the flask application object
app = Flask(__name__)


#Just a key for production. dont worry about it
app.config['SECRET_KEY'] = 'PURPLE HAZE 123'
app.debug=True


#Created a class to establish what the user searches for in the web app
class QueryForm(FlaskForm):
    snp_name = StringField('Enter a valid rsID: ', validators=[InputRequired()])
    submit = SubmitField('Submit')

class OwnForm(FlaskForm):
    rsid_select = SelectMultipleField(u'rsid_list',coerce=str, choices =[])
    population_select = SelectField(u'pop_list', coerce=str)
    submit = SubmitField(u"Submit")
    #takes the first point (the rsid) from the query result so becomes list of rsids
    def __init__(self, *args, **kwargs):
        #rsIDs = 
        #['rs9501130', 'rs9405661','rs9388489','rs9356171','rs9354144','rs9275358','rs9273368','rs9273363','rs9272346','rs9268853','rs9268645','rs9268576',
        #'rs926592','rs9264758','rs9260151','rs924043','rs886424','rs80028505','rs78824139','rs7760731','rs73043122','rs72928038','rs6931865','rs4320356','rs4148870','rs3997848',
        #'rs3761980','rs3757247','rs35122968','rs34941730','rs3135365','rs3135002','rs3134938','rs3128930','rs3093664','rs2857595','rs2647044','rs2471863','rs241427',
        #'rs2251396','rs212408','rs1980493','rs17711850','rs1770','rs1578060','rs1538171','rs138748427','rs13217044','rs1270942','rs12665429','rs1265057','rs12203596','rs118124843',
        #'rs11755527','rs116763857','rs116020851','rs114631266','rs11154178','rs1050979','rs1015166']
        #rsid_tuples = [(a,b) for a,b in zip(rsIDs, rsIDs)]
        super(OwnForm, self).__init__(*args, **kwargs)
        #self.rsid_select.choices = rsid_tuples
        self.population_select.choices = [('ALL', 'ALL'), ('AFR', 'AFR'), ('AMR','AMR'), ('EAS','EAS'),('EUR','EUR'), ('SAS','SAS')]
                      
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
        
        ####code for LD analysis:###
        ##rsIDs are taken from query and made into tuple. 
        rsIDs = [] 
        result = search_snp
        rsIDs = [i[0] for i in result]
        rsid_tuples = [(a,b) for a,b in zip(rsIDs, rsIDs)]
        
        ##calling wtf form class
        form = OwnForm()
        #making choices specific to query
        form.rsid_select.choices = rsid_tuples

        if request.method == 'POST' and form.validate_on_submit():
            #retrieving data from forms 
            rsid_list = request.form.getlist('rsid_select')
            population = form.population_select.data
        
            #getting dictionary of LD values for each RSID pair
            ld_dict = ld_dict_maker(rsid_list=rsid_list, population=population)
            #getting heatmap components from LD values 
            ret, mask = ld_graph_maker(ld_dict)

            ####PLOTTING HEATMAP:
            plt.figure()
            sns.heatmap(ret, cmap="RdYlGn_r", annot=True, mask=mask)
            plt.title('LD Heatmap')
            #making bytes object to save to heatmap - makes into binary object
            buf = BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0) 
            #encoding the data which is then decoded when sent to html 
            figdata_png = base64.b64encode(buf.getvalue())
            
            ###making downloadbale file. 
            file, filename = ld_csv_maker(df=ret, ld_dict=ld_dict, population=population)
            return render_template('table.html', ld_dict=ld_dict, result=figdata_png.decode('utf8'), filename=filename)
        return render_template("Chromosome.html", form=form, search_snp=search_snp)
    except:
        return "No information availabe for rs#: %s." % snp_name

##route for csv file download
@app.route('/table/<filename>')
def file_download(filename):
    return send_from_directory('LD_files', filename)
    

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

