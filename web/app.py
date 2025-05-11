from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import requests


app = Flask(__name__)
app.secret_key = 'super-secret-key'

def init_db():
    if not os.path.exists('bhoomi.db'):
        conn = sqlite3.connect('bhoomi.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    # Create crops table if not exists
    conn = sqlite3.connect('bhoomi.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            crop_name TEXT,
            area REAL,
            fertilizer TEXT,
            status TEXT DEFAULT 'Planted',
            growth INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('bhoomi.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "⚠️ Email already registered!"
        finally:
            conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('bhoomi.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['name'] = user[1]
            return redirect('/dashboard')
        else:
            return "❌ Invalid credentials!"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    # Simulated soil data
    data = {
        "Nitrogen (N)": "82 mg/kg",
        "Phosphorus (P)": "47 mg/kg",
        "Potassium (K)": "62 mg/kg",
        "pH": "6.5",
        "Moisture": "34 %",
        "Temperature": "27.5 °C",
        "EC": "420 µS/cm"
    }

    tooltips = {
        "Nitrogen (N)": "Helps leafy growth and photosynthesis.",
        "Phosphorus (P)": "Essential for root development.",
        "Potassium (K)": "Improves drought resistance and crop quality.",
        "pH": "Affects nutrient absorption, ideal 6-7.5.",
        "Moisture": "Reflects water retention of the soil.",
        "Temperature": "Ideal for microbial activity in soil.",
        "EC": "Indicates soil salinity affecting root health."
    }

    return render_template('dashboard.html', name=session['name'], data=data, tooltips=tooltips)


@app.route('/marketplace')
def marketplace():
    products = [
        {
            "name": "NPK 10-26-26",
            "price": "₹1600",
            "image": "NPK1.png",
            "composition": "46% Nitrogen",
            "weight": "50kg",
            "usage": "Recommended to use 75kg/acre",
            "brand": "IFFCO",
            "rating": 4.5
        },
        {
            "name": "DAP 18-46-0r",
            "price": "₹1350",
            "image": "DAP1.png",
            "composition": "N:18%, P:46%",
            "weight": "50kg",
            "usage": "Use 60kg/acre as basal dose",
            "brand": "Mahadhan",
            "rating": 4.8
        },
        {
            "name": "Vermicompost Organic Fertilizer",
            "price": "₹249",
            "image": "compost.png",
            "composition": "100% Organic",
            "weight": "5kg",
            "usage": "Use 100kg/acre in topsoil",
            "brand": "Native India Organics",
            "rating": 4.2
        },
        {
            "name": "Bone Meal Powder",
            "price": "₹119",
            "image": "Bone.jpg",
            "composition": "100% Organic",
            "weight": "400g",
            "usage": "Apply at the basin of the plant depending on the size and age",
            "brand": "Indian Gardens",
            "rating": 3.2
        },
        {
            "name": "Epsom Salt Fertilizer",
            "price": "₹119",
            "image": "epsom.jpg",
            "composition": "Magnesium Sulphate salt",
            "weight": "400g",
            "usage": "simply dissolve a tablespoon of Epsom salt in a gallon of water",
            "brand": "India Gardens",
            "rating": 4.2
        },
        {
            "name": "Neem Cake Powder",
            "price": "₹699",
            "image": "neem.jpg",
            "composition": "100% Organic",
            "weight": "10kg",
            "usage": "30g for a regular pot(6 inch diameter)",
            "brand": "Ugaoo",
            "rating": 4.2
        },

            {
            "name": "Humic Power Humic acid",
            "price": "₹270",
            "image": "humic.png",
            "composition": "12% Humic acid, 3% Fulvic acid",
            "weight": "500ml",
            "usage": "Apply 800ml-1L Humic acid in 200L barrel with water through drip irrigation per acre",
            "brand": "Native India Organics",
            "rating": 5.0
        },
        {
            "name": "Sea Special Seaweed Extract",
            "price": "₹190",
            "image": "sea.png",
            "composition": "100% Organic",
            "weight": "500ml",
            "usage": "Mix 7 ml of Sea Special Seaweed Extract per litre of clean water",
            "brand": "Native India Organics",
            "rating": 3.0
        },
        {
            "name": "Bio Insecticide to control Mealybugs",
            "price": "₹299",
            "image": "vert.jpg",
            "composition": "Verticillium Lecanii",
            "weight": "1KG",
            "usage": "Mix with water and apply as a spray",
            "brand": "Native India Organics",
            "rating": 4.2
        }
    ]
    return render_template('marketplace.html', products=products)

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    weather_data = None
    error = None
    if request.method == 'POST':
        city = request.form['city']
        api_key = '499bc583fdf043f890e73222252504'

        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
        response = requests.get(url)

        if response.status_code == 200:
            weather_data = response.json()
        else:
            error = "⚠️ Could not fetch weather data. Please check the location or try again."

    return render_template('weather.html', weather=weather_data, error=error)
@app.route('/subscriptions')
def subscription():
    plans = [
        {
            "name": "Basic",
            "price": "₹399/month",
            "features": [
                "Crop Recommendations",
                "Basic Fertilizer Suggestions",
                "Soil Data Dashboard"
            ],
            "bg": "bg-light",
            "btn": "btn-outline-success"
        },
        {
            "name": "Pro",
            "price": "₹899/month",
            "features": [
                "All Basic Features",
                "Access to QGIS Mapping",
                "Weather + Soil Insights",
                "Crop History Management"
            ],
            "bg": "bg-white border border-success",
            "btn": "btn-success"
        },
        {
            "name": "Premium",
            "price": "₹1299/month",
            "features": [
                "All Pro Features",
                "AI-based Fertilizer Optimization",
                "1:1 Agronomist Chat",
                "Yield Forecasting + Disease Alerts"
            ],
            "bg": "bg-light",
            "btn": "btn-outline-success"
        }
    ]
    current_plan = "Pro" 
    return render_template("subscription.html", plans=plans, current_plan=current_plan)

@app.route('/qgismap')
def qgismap():
    return render_template('qgismap.html')


@app.route('/mycrop', methods=['GET', 'POST'])
def mycrop():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    if request.method == 'POST':
        crop_name = request.form['crop_name']
        area = request.form['area']
        fertilizer = request.form['fertilizer']

        conn = sqlite3.connect('bhoomi.db')
        c = conn.cursor()
        c.execute('INSERT INTO crops (user_id, crop_name, area, fertilizer) VALUES (?, ?, ?, ?)',
                  (user_id, crop_name, area, fertilizer))
        conn.commit()
        conn.close()

    # Fetch crops for the user
    conn = sqlite3.connect('bhoomi.db')
    c = conn.cursor()
    c.execute('SELECT crop_name, area, fertilizer, stage, progress FROM crops WHERE user_id = ?', (user_id,))
    user_crops = c.fetchall()
    conn.close()

    return render_template('mycrop.html', crops=user_crops, name=session['name'])



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
