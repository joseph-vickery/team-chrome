#webapp packages
from flask import Flask, render_template, url_for, redirect, request, send_from_directory, render_template_string

#database package
import sqlite3 as db
#data manipulation package
import pandas as pd

#import libraries needed to create and process forms
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, SelectField
from wtforms.validators import InputRequired

#for LD functions 
from analysis_scripts.LD_functions import ld_dict_maker, ld_graph_maker, ld_csv_maker
import matplotlib 
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
import numpy as np
from io import BytesIO
import base64

#libraries for manhattan plots
import pandas as pd
import matplotlib
matplotlib.use('SVG')
import numpy as np

#Creates the flask application object
app = Flask(__name__)
#Just a key for production. dont worry about it
app.config['SECRET_KEY'] = 'PURPLE HAZE 123'

#Created a class to establish what the user searches for in the web app
class QueryForm(FlaskForm):
    snp_name = StringField('Enter valid input: ', validators=[InputRequired()])
    submit = SubmitField('Submit')

###creating class for analysis query forms: SNP select, population and the submit button
class OwnForm(FlaskForm):
    ##making choices empty so can be adjusted to match query searches within app routes
    rsid_select = SelectMultipleField(u'rsid_list',coerce=str, choices =[])
    population_select = SelectField(u'pop_list', coerce=str, choices = [('ALL', 'ALL'), ('AFR', 'AFR'), ('AMR','AMR'), ('EAS','EAS'),('EUR','EUR'), ('SAS','SAS')])
    submit = SubmitField(u"Submit")

### this is to make the plots the right size when rendered in html 
rcParams.update({'figure.autolayout': True})

#This is the home page 
@app.route('/', methods = ['GET', 'POST'])
def index():
    form = QueryForm()
    snp_name = None
    if form.validate_on_submit():
        snp_name = form.snp_name.data
        #Redirect user to snp page if rs is typed
        if snp_name[:2]== "rs":
            return redirect(url_for('SNP', snp_name= snp_name))
        #Redirect user to chromosome page if chr is typed
        if snp_name[:3] == "chr":
            return redirect(url_for('Chromosome',snp_name=snp_name))
        
        #Redirect user to region page if they enter two locations separated by a comma
        elif "," in snp_name:
            return redirect(url_for('Region', snp_name=snp_name))
        
        #redirect to mapped gene page if the beginning != rs or chr or ,
        elif snp_name != 'rs' or snp_name != 'chr' or "," not in snp_name:
            return redirect(url_for('MAPPED_GENE', snp_name=snp_name))

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
        population.SAS_Frequency, CADD.Raw_Score, CADD.PHRED

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
            cursor.execute("""SELECT *
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
        return render_template("search.html", name=snp_name, search_snp=search_snp, search_GO=search_GO, search_GO1=search_GO1, search_GO2=search_GO2)
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
        cursor.execute ("""SELECT  gwas.snp, gwas.Gene_name,gwas.p_value,
        population.Chromosome, population.Position, population.REF_Allele, 
        population.ALT_Allele, population.Minor_Allele, population.AFR_Frequency, 
        population.AMR_Frequency, population.EAS_Frequency, population.EUR_Frequency, population.SAS_Frequency, CADD.Raw_Score, CADD.PHRED

        FROM gwas
        INNER JOIN CADD ON gwas.snp = CADD.snp 
        INNER JOIN population on CADD.snp = population.snp 
        WHERE population.Chromosome= '%s' """ % snp_name)
        search_snp = cursor.fetchall()

        ####code for LD analysis:###
        ##rsIDs are taken from query and made into tuple for form list. 
        rsIDs = [] 
        result = search_snp
        rsIDs = [i[0] for i in result]
        rsid_tuples = [(a,b) for a,b in zip(rsIDs, rsIDs)]
        
        ##calling wtf form class for analysis
        form = OwnForm()
        #making choices specific to query
        form.rsid_select.choices = rsid_tuples

        ##checking if the form is working and the submit button has been pressed:
        if request.method == 'POST' and form.validate_on_submit():
            try:
                #retrieving data from the forms 
                rsid_list = request.form.getlist('rsid_select')
                population = form.population_select.data
            
                #getting dictionary of LD values for each rsID pair - this function contains the API access
                ld_dict = ld_dict_maker(rsid_list=rsid_list, population=population)
                
                ####creating HEATMAP####
                
                #getting heatmap components from LD values 
                ret, mask = ld_graph_maker(ld_dict)

                ##initialising figure
                plt.figure()

                #if the graph is too big, the annotations are removed due to it crowding up the graph and looking messy
                if len(ret) > 15: 
                    sns.heatmap(ret, cmap="RdYlGn_r", annot=False, mask=mask, vmin=0,vmax=1)
                else: 
                    sns.heatmap(ret, cmap="RdYlGn_r", annot=True, mask=mask, vmin=0,vmax=1)
                #setting plot title 
                plt.title('LD Heatmap for population: {pop}'.format(pop=population))

                #setting the x axis labels to be vertical so they don't overlap
                plt.xticks(rotation=90)
                plt.yticks(rotation=360)
                
                #making bytes object to save to heatmap - makes into binary object
                buf = BytesIO()

                #saving the figure as a png
                plt.savefig(buf, format="png")
                buf.seek(0) 

                #encoding the data which is then decoded when sent to html 
                figdata_png = base64.b64encode(buf.getvalue())
                
                ###making downloadable file - file name is passed to html which is used to access file from file download function 
                filename = ld_csv_maker(df=ret)
                #rendering the html template with the figure being decoded when sent to html page
                return render_template('LD.html', ld_dict=ld_dict, result=figdata_png.decode('utf8'), filename=filename)
            #error message if form fails for some reason. 
            except: 
                return render_template_string("""The search has errored. <br> Firstly, please ensure more than one SNP was selected. <br> 
                Furthermore, There may not be any available information for this combination of SNPs and population. <br> Please try again with different parameters. <br>
                If this is a persistant problem, it is likely you have made too many requests in a short amount of time and this link has thus been blocked from accessing the API server. <br> 
                Please wait for 15 mins and try again or contact LDlink at NCILDlinkWebAdmin@mail.nih.gov who may be able to remedy this issue. """)
        return render_template("Chromosome.html", form=form, search_snp=search_snp)
    except:
        return "No information availabe for rs#: %s." % snp_name

@app.route('/MAPPED_GENE/<snp_name>', methods = ['GET', 'POST'])
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
        population.SAS_Frequency, CADD.Raw_Score, CADD.PHRED

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

        ####code for LD analysis:###
        ##rsIDs are taken from query and made into tuple for form list. 
        rsIDs = [] 
        result = search_snp
        rsIDs = [i[0] for i in result]
        rsid_tuples = [(a,b) for a,b in zip(rsIDs, rsIDs)]
        
        ##calling wtf form class for analysis
        form = OwnForm()
        #making choices specific to query
        form.rsid_select.choices = rsid_tuples

        ##checking if the form is working and the submit button has been pressed:
        if request.method == 'POST' and form.validate_on_submit():
            try:
                #retrieving data from the forms 
                rsid_list = request.form.getlist('rsid_select')
                population = form.population_select.data
            
                #getting dictionary of LD values for each rsID pair - this function contains the API access
                ld_dict = ld_dict_maker(rsid_list=rsid_list, population=population)
                
                ####creating HEATMAP####
                
                #getting heatmap components from LD values 
                ret, mask = ld_graph_maker(ld_dict)

                ##initialising figure
                plt.figure()

                #if the graph is too big, the annotations are removed due to it crowding up the graph and looking messy
                if len(ret) > 15: 
                    sns.heatmap(ret, cmap="RdYlGn_r", annot=False, mask=mask, vmin=0,vmax=1)
                else: 
                    sns.heatmap(ret, cmap="RdYlGn_r", annot=True, mask=mask, vmin=0,vmax=1)
                #setting plot title 
                plt.title('LD Heatmap for population: {pop}'.format(pop=population))

                #setting the x axis labels to be vertical so they don't overlap
                plt.xticks(rotation=90)
                plt.yticks(rotation=360)
                
                #making bytes object to save to heatmap - makes into binary object
                buf = BytesIO()

                #saving the figure as a png
                plt.savefig(buf, format="png")
                buf.seek(0) 

                #encoding the data which is then decoded when sent to html 
                figdata_png = base64.b64encode(buf.getvalue())
                
                ###making downloadable file - file name is passed to html which is used to access file from file download function 
                filename = ld_csv_maker(df=ret)

                #rendering the html template with the figure being decoded when sent to html page
                return render_template('LD.html', ld_dict=ld_dict, result=figdata_png.decode('utf8'), filename=filename)
            #error message if form fails for some reason. 
            except: 
                return render_template_string("""The search has errored. <br> Firstly, please ensure more than one SNP was selected. <br> 
                Furthermore, There may not be any available information for this combination of SNPs and population. <br> Please try again with different parameters. <br>
                If this is a persistant problem, it is likely you have made too many requests in a short amount of time and this link has thus been blocked from accessing the API server. <br> 
                Please wait for 15 mins and try again or contact LDlink at NCILDlinkWebAdmin@mail.nih.gov who may be able to remedy this issue. """)
        return render_template("Map.html", name=snp_name, search_snp=search_snp, GO_search=GO_search, form=form)
    except:
        return "No information availabe for %s." % snp_name

@app.route('/Region/<snp_name>', methods = ['GET', 'POST'])
def Region(snp_name):
    try:
        con = db.connect("GC.db", check_same_thread=False)
        cursor = con.cursor()

    
        #separate the two locations from the user input by a comma
        sep_genes = snp_name.split(',')
        #sorted takes the list and arranges from lowest to greatest.
        sorted_genes = sorted(sep_genes)
        gene1, gene2 = [sorted_genes[i] for i in (0, 1)]
        gene2 = gene2.strip()

        ########snp search######

        #queried data is executed below to get all info from tables
        cursor.execute ("""SELECT  gwas.snp, gwas.Gene_name,gwas.p_value, gwas.location, population.Chromosome,
        population.Position, population.REF_Allele, 
        population.ALT_Allele, population.Minor_Allele, population.AFR_Frequency,
        population.AMR_Frequency, population.EAS_Frequency, population.EUR_Frequency, 
        population.SAS_Frequency, CADD.Raw_Score, CADD.PHRED
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

        ###Code for creating Manhattan Plot ###        
        man_info=[]
        for row in search_snp:
            rs_ID = row[0]
            p_value = row[2]
            location = row[3]
            new_row=[rs_ID, p_value, location]        
            man_info.append(new_row)
       
            #creating dictionary for man plot 
        data_dict = {'snp': [row[0] for row in man_info],
                    'p_value':[row[1] for row in man_info],
                    'location': [row[2] for row in man_info]}
            #convert into a pandas
        df=pd.DataFrame.from_dict(data_dict)
        

        #change structure of the loop-- try iterows as seem to be overwriting everything 
        i=0
        #have a counter that starts with 0
        for p_value_f in df['p_value']:  # produces this for all values 4.000000e-08
            #df['p_value_f']=float(p_value_f.replace(' x 10', 'e')) #the replace is approved
            df.at[i,'p_value'] = p_value_f.replace(' x 10', 'e')
            i+=1  
            #issue-so basically its changing evry value in column to last value that we loop through

        df['p_value']=df['p_value'].astype(float) #make the p_value column a float

            #create a df coloumn for the chromosome number
        df['chr']=np.vectorize(lambda x: x.split(':')[0])(np.array(df['location'],dtype=str)) #for new column called chromosome, take where there is a : in 'location', split and take the values before it and transalte to new column.
        #adjust position coloumn to only show the bits after :
        df['location']=np.vectorize(lambda x:x.split(':')[1])(np.array(df['location'],dtype=str)) #split and keep the values after the dleimiter by [1], overwrote the locarion column
        df['location']=df['location'].astype(int)
        #-log_10 pvalue
        df['-log_pv']=-np.log10(df.p_value) #convert to -log10 pvalue and store in new column of dataframe

        #generating plot works

        #group each snp by chromosome
        df=df.sort_values(['chr','location'])  #inorder of location 
        df.reset_index(inplace=True, drop=True); df['i']=df.index

        #generate plot
        plot=sns.relplot(data=df, x='i', y='-log_pv', aspect=4,
                        hue='chr', palette='bright', legend=None, linewidth=0)
        chrom_df=df.groupby('chr')['i'].median()
        plot.ax.set_xlabel('chr'); plot.ax.set_xticks(chrom_df)
        plot.ax.set_xticklabels(chrom_df.index)
        plot.fig.suptitle('Manhattan plot showing association between SNPs and Diabetes Mellitus 1 ')

        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        figdata_png = base64.b64encode(buf.getvalue())

        ####code for LD analysis:###
        ##rsIDs are taken from query and made into tuple for form list. 
        rsIDs = [] 
        result = search_snp
        rsIDs = [i[0] for i in result]
        rsid_tuples = [(a,b) for a,b in zip(rsIDs, rsIDs)]
        
        ##calling wtf form class for analysis
        form = OwnForm()
        #making choices specific to query
        form.rsid_select.choices = rsid_tuples

        ##checking if the form is working and the submit button has been pressed:
        if request.method == 'POST' and form.validate_on_submit():
            try:
                #retrieving data from the forms 
                rsid_list = request.form.getlist('rsid_select')
                population = form.population_select.data
            
                #getting dictionary of LD values for each rsID pair - this function contains the API access
                ld_dict = ld_dict_maker(rsid_list=rsid_list, population=population)
                
                ####creating HEATMAP####
                
                #getting heatmap components from LD values 
                ret, mask = ld_graph_maker(ld_dict)

                ##initialising figure
                plt.figure()

                #if the graph is too big, the annotations are removed due to it crowding up the graph and looking messy
                if len(ret) > 15: 
                    sns.heatmap(ret, cmap="RdYlGn_r", annot=False, mask=mask, vmin=0,vmax=1)
                else: 
                    sns.heatmap(ret, cmap="RdYlGn_r", annot=True, mask=mask, vmin=0,vmax=1)
                #setting plot title 
                plt.title('LD Heatmap for population: {pop}'.format(pop=population))

                #setting the x axis labels to be vertical so they don't overlap
                plt.xticks(rotation=90)
                plt.yticks(rotation=360)
                
                #making bytes object to save to heatmap - makes into binary object
                buf = BytesIO()

                #saving the figure as a png
                plt.savefig(buf, format="png")
                buf.seek(0) 

                #encoding the data which is then decoded when sent to html 
                figdata_png = base64.b64encode(buf.getvalue())
                
                ###making downloadable file - file name is passed to html which is used to access file from file download function 
                filename = ld_csv_maker(df=ret)

                #rendering the html template with the figure being decoded when sent to html page
                return render_template('LD.html', ld_dict=ld_dict, result=figdata_png.decode('utf8'), filename=filename)
            #error message if form fails for some reason. 
            except: 
                return render_template_string("""The search has errored. <br> Firstly, please ensure more than one SNP was selected. <br> 
                Furthermore, There may not be any available information for this combination of SNPs and population. <br> Please try again with different parameters. <br>
                If this is a persistant problem, it is likely you have made too many requests in a short amount of time and this link has thus been blocked from accessing the API server. <br> 
                Please wait for 15 mins and try again or contact LDlink at NCILDlinkWebAdmin@mail.nih.gov who may be able to remedy this issue. """)
            
        return render_template("Region.html", name=snp_name, search_snp=search_snp, all_region_GO_queries=all_region_GO_queries,
                                man_plot = figdata_png.decode('utf8'), form=form)
    except:
        return "No information availabe for %s." % snp_name

##route for csv file download
@app.route('/table/<filename>')
def file_download(filename):
    return send_from_directory('LD_files', filename)

if __name__ == "__main__":
    app.run(debug=True, port=8001)
