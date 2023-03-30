from flask import Flask, redirect, url_for,request, render_template,flash

app = Flask(__name__)
app.config['SECRET_KEY'] = ''


@app.route("/", methods = ['GET',"POST"])
@app.route("/index", methods = ['GET',"POST"])
def home():  
    return render_template('/index.html')


if __name__ == "__main__":
    app.run(debug=True)