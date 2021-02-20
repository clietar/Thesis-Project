from pprint import pprint as pp
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
@app.route('/')
def acceuil():
    return render_template('home.html')
@app.route('/user/<name>')
def user(name):
    return "Hello, %s" %name

if __name__=='__main__':
    app.run(debug=True)