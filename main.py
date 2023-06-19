from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    title = "Home"
    return render_template("home.html", title=title)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)