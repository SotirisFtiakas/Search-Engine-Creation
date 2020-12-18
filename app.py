# Create anaconda env and
# pip install -r requirements.txt

from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)

# Configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Fetch form data
        qDetails = request.form
        query = qDetails['query']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO searches(query) VALUES(%s)", (query, ))
        mysql.connection.commit()
        cur.close()
        #return 'Success'
        return redirect('/queries')
    return render_template('index.html')

@app.route('/queries')
def queries():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM searches")
    if resultValue > 0:
        qDetails = cur.fetchall()
        return render_template('queries.html', qDetails=qDetails)
    else :
        return "Empty Database"

if __name__ == '__main__':
    app.run(debug=True)