from flask import Flask, render_template, redirect, request, url_for
import pymongo
import os

app = Flask(__name__)

url = "mongodb+srv://dexterLab:dyntyp-sejha6-sopcEc@holobase-upu74.gcp.mongodb.net/holocast?retryWrites=true"
client = pymongo.MongoClient(url)
db = client.holocast
building_data = db["building"]
history = db["history"]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/building/<name>", methods=["GET", "POST"])
def update_data(name):
    data = dict(request.form)
    building = building_data.find_one({"name": name})
    if building is None:
        building_data.insert_one({"name": name, "voltage": data["voltage"], "current": data["current"], "frequency": data['frequency'], 'theta': data['theta']})
        return redirect(url_for("home"))

    hist = history.find_one({"name": name})
    if hist:
        hist['voltage'].append(building['voltage'])
        hist['current'].append(building['current'])
        hist['frequency'].append(building['frequency'])
        hist['theta'].append(building['theta'])

        history.update_one(
            {"name": name}, {
                "$set": {
                    "name": name,
                    "voltage": hist["voltage"],
                    "current": hist["current"],
                    "frequency": hist["frequency"],
                    "theta": hist["theta"]
                }
            })
    else:
        history.insert_one({"name": name, "voltage": [data["voltage"]], "current": [data["current"]], "frequency": [data['frequency']], 'theta': [data['theta']]})

    building_data.update_one(
        {"name": name}, {
            "$set": {
                    "name": name,
                    "voltage": data["voltage"],
                    "current": data["current"],
                    "frequency": data["frequency"],
                    "theta": data["theta"]
                }
        })

    return redirect(url_for("home"))


@app.route("/get_data")
def send_data():
    data = building_data.find()
    data_string = ""
    for i in data:
        data_string += i['name'] + '$' + i['voltage'] + '$' + i['current'] + '$' + i['frequency'] + '$' + i['theta']
        data_string += "!#!"
    return data_string


@app.route("/fetch/<trace>")
def send_sjt(trace):
    data = building_data.find_one({"name": trace})
    if data:
        data_string = f"Line Voltage: {data['voltage']}, Line Current: {data['current']}, Power: {round((3**0.5)*float(data['voltage'])*float(data['current'])*float(data['theta']), 2)}"
    else:
        data_string = "No data!"
    return data_string 


@app.route("/fetch_tmp/<trace>")
def send_tmp_sjt(trace):
    data = building_data.find_one({"name": trace})
    if data:
        data_string = f"Reactive Power: {float(data['voltage'])*float(data['current'])*((1- int(data['theta'])**2)**0.5)}, Apparent Power: {int(data['current'])*int(data['voltage'])}, Frequency: {data['frequency']}"
    else:
        data_string = "No data!"
    return data_string


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
