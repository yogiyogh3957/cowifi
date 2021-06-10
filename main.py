from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, URL
import csv
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Cafes(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    coffeeshop  = db.Column(db.String(250), unique=True, nullable=False)
    open        = db.Column(db.Integer, nullable=True)
    close       = db.Column(db.Integer, nullable=True)
    coffee      = db.Column(db.String(250), nullable=True)
    wifi        = db.Column(db.String(250), nullable=True)
    power       = db.Column(db.String(250), nullable=True)
    location    = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<Cafe {self.coffeeshop}>'
# db.create_all()

def coffe_dropdown(choice):
    if choice == 1 :
        return ["☕️️", "☕️️☕️️", "☕️️☕️️☕️️", "☕️️☕️️☕️️☕️️", "☕️️☕️️☕️️☕️️☕️️"]
    if choice == 2 :
        return ["✘", "💪", "💪💪", "💪💪💪", "💪💪💪💪", "💪💪💪💪"]
    if choice == 3 :
        return ["✘", "🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌"]

def submit():
    print("button have been pressed")

class CafeForm(FlaskForm):
    valid_length = Length(min=4, message="min 4 characters")
    valid_url_  = URL(message= "please input valid url")

    cafe    = StringField('Cafe name', validators=[DataRequired(), valid_length])
    loc     = StringField('Location', validators=[DataRequired(), valid_url_])
    open    = StringField('Open Hour', validators=[DataRequired()])
    close   = StringField('Close Hour', validators=[DataRequired()])
    coffee  = SelectField('Coffee', validators=[DataRequired()], choices=coffe_dropdown(1))
    wifi    = SelectField('Wifi', validators=[DataRequired()], choices=coffe_dropdown(2))
    power   = SelectField('Power', validators=[DataRequired()], choices=coffe_dropdown(3))
    submit  = SubmitField('Submit')

# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=['POST', 'GET'])
def add_cafe():
    form = CafeForm()
    print(form.data) #semua data dalam dict (.data)
    print(form.loc.data) #data lokasi saja, var= loc

    # isi form.data = {'cafe': 'aaaaaa', 'loc': 'https://g.page/Starbucks-JCM?share', 'open': '11', 'close': '21', 'coffee': '☕️️', 'wifi': '✘', 'power': '✘', 'submit': True, 'csrf_token': 'IjQxYTcwYjBmNGQ3YWQwNzZhNzZiOTc0NDlmYmY1YTM3MjU1MzU5YzQi.YJOj_Q.OtAQyGUfYQ4VSpv6Z_r3Exi1ZI4'}
    if form.validate_on_submit():

        # #Cara lain membaca data (memakai req.form)
        # all_data = request.form
        # print(f"req.form.loc = {all_data}")
        #
        # loc = request.form['loc']
        # print(f"req.form.loc = {loc}")

        #add data to csv
        with open("cafe-data.csv", mode="a") as csv_file:
            csv_file.write(f"\n{form.cafe.data},"
                           f"{form.loc.data},"
                           f"{form.open.data},"
                           f"{form.close.data},"
                           f"{form.coffee.data},"
                           f"{form.wifi.data},"
                           f"{form.power.data}")

        #add data into database
        cafe_data = Cafes(
            coffeeshop=form.cafe.data,
            open=form.open.data,
            close=form.close.data,
            coffee=form.coffee.data,
            wifi=form.wifi.data,
            power=form.power.data,
            location=form.loc.data
        )
        db.session.add(cafe_data)
        db.session.commit()
        all_cafe_data = db.session.query(Cafes).all()
        print(all_cafe_data)

        return redirect(url_for('cafes'))

    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    #SHOWING CAFE DATA FROM CSV
    with open('cafe-data.csv', newline='') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        indexs = len(list_of_rows)
        http = "http"
        for row in csv_data:
            list_of_rows.append(row)

    all_cafe_data = db.session.query(Cafes).all()


    return render_template('cafes.html', cafes=list_of_rows, len=indexs, http_string=http, all_cafe_data=all_cafe_data)


if __name__=="__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', 8934)), debug=True)

