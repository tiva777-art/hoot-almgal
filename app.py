from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1 style='color:red;text-align:center'>
    🔥 حوت المجال 🔥
    </h1>
    """

@app.route("/charge", methods=["POST"])
def charge():

    data = request.json

    number = data.get("number")
    product = data.get("product")

    return jsonify({
        "status":"success",
        "number":number,
        "product":product
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)