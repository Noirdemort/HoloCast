from flask import Flask, render_template, redirect, request, url_for
import pymongo

app = Flask(__name__)



client = pymongo.MongoClient("mongodb+srv://dexterLab:dyntyp-sejha6-sopcEc@holobase-upu74.gcp.mongodb.net/holocast?retryWrites=true")
# db = client.test
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


if __name__ == '__main__':
    app.run()
