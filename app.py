# Create anaconda env and
# pip install -r requirements.txt

# Import needed libraries

from flask import Flask, render_template, request, redirect, jsonify
import pandas as pd
import query_processor as qp

app = Flask(__name__)

# Landing page
@app.route('/', methods=['GET', 'POST'])
def index():
    global results, full_query_vector
    queries_df = pd.read_csv("history.csv")
    # Fetch form data
    if request.method == 'POST':
        qDetails = request.form
        query = qDetails['query']
        if (query != ''):
            single_query = {'Query': query}
            queries_df = queries_df.append(single_query, ignore_index=True)
            #queries_df.to_csv(r'history.csv')
            results, full_query_vector = qp.query_search(query)
        return redirect('/queries')
    return render_template('index.html')

# Result page
@app.route('/queries', methods=['GET', 'POST'])
def queries():
    global full_query_vector
    queries_df = results.head(7)
    qDetailsTitle = queries_df["Title"].tolist()
    qDetailsUrl = queries_df["Url"].tolist()
    qDetailsScore = queries_df["Score"].tolist()
    #print(queries_df)
    rankings=["0","1","2","3","4","5","6"]
    # Fetch form data
    if request.method == 'POST':
        better = request.form.getlist('better')
        newResults, full_query_vector = qp.optimized_query(better, queries_df.reset_index(drop=True), full_query_vector, results)
        queries_df = newResults.head(7)
        qDetailsTitle = queries_df["Title"].tolist()
        qDetailsUrl = queries_df["Url"].tolist()
        qDetailsScore = queries_df["Score"].tolist()
    return render_template('queries.html', queryDetails=zip(qDetailsTitle,qDetailsUrl,qDetailsScore,rankings))

# 404 error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)