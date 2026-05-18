from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """

    <html>
    <head>
    <title>حوت المجال</title>

    <style>

    body{
        background:#050505;
        color:white;
        font-family:Arial;
        text-align:center;
        padding-top:50px;
    }

    .box{
        width:90%;
        max-width:400px;
        margin:auto;
        background:#111;
        padding:20px;
        border-radius:20px;
        box-shadow:0 0 20px red;
    }

    h1{
        color:red;
        font-size:40px;
    }

    input,select{
        width:90%;
        padding:15px;
        margin:10px;
        border:none;
        border-radius:10px;
        background:#222;
        color:white;
    }

    button{
        width:95%;
        padding:15px;
        background:red;
        border:none;
        border-radius:10px;
        color:white;
        font-size:20px;
    }

    </style>
    </head>

    <body>

    <div class="box">

    <h1>🔥 حوت المجال 🔥</h1>

    <p>شحن كروت وباقات</p>

    <select>
    <option>Vodafone</option>
    <option>Etisalat</option>
    <option>Orange</option>
    <option>WE</option>
    </select>

    <input type="text" placeholder="رقم الهاتف">

    <select>
    <option>كارت 10</option>
    <option>كارت 15</option>
    <option>كارت 25</option>
    <option>كارت 50</option>
    </select>

    <button>شحن الآن</button>

    </div>

    </body>
    </html>

    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)