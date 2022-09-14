import os
import requests
import operator
import re
import nltk
import logging
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from collections import Counter
from bs4 import BeautifulSoup
nltk.download("stopwords")
from nltk.corpus import stopwords
import matplotlib.pyplot as plt

app = Flask(__name__)

stops = [
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
    'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
    'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
    'with', 'about', 'against', 'between', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
    'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
    'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
    'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's',
    't', 'can', 'will', 'just', 'don', 'should', 'now', 'id', 'var',
    'function', 'js', 'd', 'script', '\'script', 'fjs', 'document', 'r',
    'b', 'g', 'e', '\'s', 'c', 'f', 'h', 'l', 'k'
]


# Function to remove tags
def remove_tags(html):
  
    # parse html content
    soup = BeautifulSoup(html, "html.parser")
  
    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()
  
    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)
  
@app.route("/simple_chart")
def chart():
    legend = 'Monthly Data'
    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 9, 8, 7, 6, 4, 7, 8]
    return render_template('index.html', values=values, labels=labels, legend=legend)


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    labels = []
    sizes  =[];
    word_img='./View/word_pie_chart.png'
    if request.method == "POST":
        # get url that the person has entered
        try:
            url = request.form['url']
            r = requests.get(url,headers={"User-Agent": "Mozilla/5.0"})
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
            return render_template('index.html', errors=errors)
        if r:
            # text processing
            html_text = remove_tags(r.text)
            raw = BeautifulSoup(html_text, 'html.parser').get_text()
            nltk.data.path.append('./nltk_data/')  # set the path
            tokens = nltk.word_tokenize(raw)
            text = nltk.Text(tokens)
            # remove punctuation, count raw words
            nonPunct = re.compile('.*[A-Za-z].*')
            raw_words = [w for w in text if nonPunct.match(w)]
            raw_word_count = Counter(raw_words)
            # stop words
            no_stop_words = [w for w in raw_words if w.lower() not in stops]
            no_stop_words_count = Counter(no_stop_words)
            # save the results
            results = sorted(
                no_stop_words_count.items(),
                key=operator.itemgetter(1),
                reverse=True
            )[:10]
            
            explode = [0.1, 0, 0, 0,0,0,0,0,0,0]
            for n in results:
                labels.append(n[0])
                sizes.append(n[1])
                

            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                    shadow=True, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            fig1.savefig('View/word_pie_chart.png')
            try:
               result="deneme"
            except:
                errors.append("Unable to add item to database.")
    return render_template('index.html', errors=errors, results=results,labels=labels,sizes=sizes)


if __name__ == '__main__':
    app.run()


if __name__ == "__main__":
    app.debug = False
    app.run()