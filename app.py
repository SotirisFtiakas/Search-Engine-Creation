# Create anaconda env and
# pip install -r requirements.txt

from flask import Flask, render_template, request, redirect
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    queries_df = pd.read_csv("foo.csv")
    if request.method == 'POST':
        # Fetch form data
        qDetails = request.form
        query = qDetails['query']
        if (query != ''):
            single_query = {'Query': query}
            queries_df = queries_df.append(single_query, ignore_index=True)
            queries_df.to_csv(r'foo.csv')
        return redirect('/queries')
    return render_template('index.html')

@app.route('/queries')
def queries():
    queries_df = pd.read_csv("foo.csv")
    if queries_df.size > 2:
        qDetails = queries_df['Query'].tolist()
        return render_template('queries.html', qDetails=qDetails)
    else :
        return "Empty Database"

if __name__ == '__main__':
    app.run(debug=True)