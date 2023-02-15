#webapp packages
from flask import Flask, render_template, url_for, redirect

#database package
import sqlite3 as db
#data manipulation package
import pandas as pd

#import libraries needed to create and process forms
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired

#connecting to database
con = db.connect("dummy_sql.db", check_same_thread=False)
c = con.cursor() #this allows us to query our database



#Creates the flask application object
app = Flask(__name__)
#Just a key for production. dont worry about it
app.config['SECRET_KEY'] = 'PURPLE HAZE 123'

class QueryForm(FlaskForm):
    snp_name = StringField('Enter a valid rsID: ', validators=[InputRequired()])
    submit = SubmitField('Submit')


@app.route('/', methods = ['GET', 'POST'])
def index():
    form = QueryForm()
    snp_name = None
    if form.validate_on_submit():
        snp_name = form.snp_name.data
        print('\n\n\n'+snp_name+'\n\n\n')
        return redirect(url_for('SNP', snp_name= snp_name))
    return render_template("index.html", form = form, snp_name=snp_name)


@app.route('/SNP/<snp_name>')
def SNP(snp_name):

    df_gwas = pd.read_sql_query('select * from gwas', con, index_col="rsID")

    snp_name = snp_name.lower()
    try:
        row = df_gwas.loc[snp_name]
#Finish the search hmtl and see if it connects.
        return render_template("search.html", name=snp_name, gene =row.Mappedgene, location = row.Location)
    except:
        return "No information availabe for rs#: %s." % snp_name


if __name__ == "__main__":
    app.run(debug=True)
