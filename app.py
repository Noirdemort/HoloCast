from flask import Flask, render_template, redirect, request, url_for
import pymongo
import os

app = Flask(__name__)

url = "mongodb+srv://dexterLab:dyntyp-sejha6-sopcEc@holobase-upu74.gcp.mongodb.net/holocast?retryWrites=true"
client = pymongo.MongoClient(url)
db = client.holocast
building_data = db["building"]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/building/<name>", methods=["GET", "POST"])
def update_data(name):
    data = dict(request.form)
    building = building_data.find_one({"name": name})
    if building is None:
        building_data.insert_one({"name": name, "voltage": data["voltage"], "current": data["current"]})
        return redirect(url_for("home"))
    building_data.update_one(
        {"name": name}, {
            "$set": {
                    "name": name,
                    "voltage": data["voltage"],
                    "current": data["current"]
                }
        })
    return redirect(url_for("home"))


@app.route("/get_data")
def send_data():
    data = building_data.find()
    data_string = ""
    for i in data:
        data_string += i['name'] + '$' + i['voltage'] + '$' + i['current']
        data_string += "!#!"
    return data_string


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
