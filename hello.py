
from flask import Flask
from flask import render_template

app = Flask(__name__)
app.debug = False


@app.route("/")
def hello():
    return render_template ('hello.html', message="Hello Andrii", xxx="Goodby!!!")

@app.route("/test")
def testng():
    return "TEST TEST TEST!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)


