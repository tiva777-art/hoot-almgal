from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """

<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>حوت المجال</title>

<style>

body{
    margin:0;
    background:#050816;
    font-family:Arial;
    color:white;
}

.top{
    padding:20px;
}

.title{
    text-align:center;
    font-size:35px;
    font-weight:bold;
}

.sub{
    text-align:center;
    color:#999;
    margin-top:5px;
}

.balance{
    width:90%;
    margin:auto;
    margin-top:20px;
    background:linear-gradient(to left,#c40000,#ff1a1a);
    border-radius:25px;
    padding:25px;
    box-sizing:border-box;
    box-shadow:0 0 25px rgba(255,0,0,0.5);
}

.balance h2{
    margin:0;
    font-size:20px;
}

.money{
    font-size:45px;
    font-weight:bold;
    margin-top:10px;
}

.services{
    width:90%;
    margin:auto;
    margin-top:25px;
}

.services h2{
    margin-bottom:20px;
}

.grid{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:15px;
}

.card{
    background:#10192d;
    padding:25px;
    border-radius:20px;
    text-align:center;
    transition:0.3s;
    box-shadow:0 0 10px rgba(0,0,0,0.3);
}

.card:hover{
    transform:scale(1.03);
    box-shadow:0 0 15px red;
}

.icon{
    font-size:40px;
    margin-bottom:15px;
}

.name{
    font-size:20px;
    font-weight:bold;
}

.banner{
    width:90%;
    margin:auto;
    margin-top:25px;
    background:black;
    border:2px solid red;
    border-radius:20px;
    padding:20px;
    text-align:center;
    color:red;
    font-size:25px;
    font-weight:bold;
    box-shadow:0 0 20px rgba(255,0,0,0.5);
}

.bottom{
    position:fixed;
    bottom:0;
    width:100%;
    background:#09101f;
    display:flex;
    justify-content:space-around;
    padding:15px 0;
    border-top:1px solid #222;
}

.bottom div{
    text-align:center;
    color:white;
    font-size:14px;
}

.active{
    color:red;
}

a{
    text-decoration:none;
    color:white;
}

</style>

</head>

<body>

<div class="top">

<div class="title">
🔥 حوت المجال 🔥
</div>

<div class="sub">
أسرع شحن .. أفضل خدمة
</div>

</div>

<div class="balance">

<h2>الرصيد الحالي</h2>

<div class="money">
125.50 ج
</div>

</div>

<div class="services">

<h2>الخدمات</h2>

<div class="grid">

<a href="#">
<div class="card">
<div class="icon">📶</div>
<div class="name">شحن الباقات</div>
</div>
</a>

<a href="#">
<div class="card">
<div class="icon">💳</div>
<div class="name">كروت الفكة</div>
</div>
</a>

<a href="#">
<div class="card">
<div class="icon">📅</div>
<div class="name">الباقات الشهرية</div>
</div>
</a>

<a href="#">
<div class="card">
<div class="icon">🎮</div>
<div class="name">شحن الألعاب</div>
</div>
</a>

<a href="#">
<div class="card">
<div class="icon">⚙️</div>
<div class="name">خدمات أخرى</div>
</div>
</a>

</div>

</div>

<div class="banner">
TIVA - HOT ALMGAL
</div>

<div style="height:120px"></div>

<div class="bottom">

<div class="active">
🏠<br>
الرئيسية
</div>

<div>
📋<br>
العمليات
</div>

<div>
➕<br>
إضافة رصيد
</div>

<div>
👤<br>
الحساب
</div>

</div>

</body>
</html>

"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)