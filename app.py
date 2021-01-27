# Create anaconda env and
# pip install -r requirements.txt

from flask import Flask, render_template, request, redirect, jsonify
import pandas as pd
import query_processor as qp

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    global results
    queries_df = pd.read_csv("foo.csv")
    if request.method == 'POST':
        # Fetch form data
        qDetails = request.form
        query = qDetails['query']
        if (query != ''):
            single_query = {'Query': query}
            queries_df = queries_df.append(single_query, ignore_index=True)
            queries_df.to_csv(r'foo.csv')
            results = qp.query_search(query)
        return redirect('/queries')
    return render_template('index.html')

# @app.route('/queries')
# def queries():
#    queries_df = results.head()#pd.read_csv("foo.csv")
#    if queries_df.size > 2:
#        qDetailsTitle = queries_df["Title"].tolist()
#        qDetailsUrl = queries_df["Url"].tolist()
#        return render_template('queries.html', queryDetails=zip(qDetailsTitle,qDetailsUrl))
#    else :
#        return "Empty Database"

@app.route('/queries', methods=['GET', 'POST'])
def queries():
    queries_df = results.head()
    qDetailsTitle = queries_df["Title"].tolist()
    qDetailsUrl = queries_df["Url"].tolist()
    if request.method == 'POST':
        better = request.form.getlist('better')
        for i in better:
            print(qDetailsTitle[int(i)])
    return render_template('queries.html', queryDetails=zip(qDetailsTitle,qDetailsUrl))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)