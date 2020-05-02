from flask import render_template, Flask, request
from waitress import serve
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import date
import pandas
from guts import sentimenter
import os

app = Flask(__name__)

#generated using os.urandom(12).hex()
app.config['SECRET_KEY'] = '0e6354d75ada225d2d9c99ce'

class StockForm(FlaskForm):
    stock = StringField('Stock ticker', [DataRequired()])
    submit = SubmitField('Submit')

@app.route('/' , methods=['GET','POST'])
def main():
    form = StockForm()
    if form.validate_on_submit():
        htmlcode = sentimenter(form.stock.data)
        return render_template('main.html', form=form, htmlcode=htmlcode)
    
    return render_template('main.html', form=form)
                
if __name__ == '__main__':
   serve(app, host='127.0.0.1', port=5000)