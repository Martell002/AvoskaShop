from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)
cart = []

def init_sqlite_db():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            items TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_sqlite_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        conn = sqlite3.connect('db.sqlite')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (fullname, username, email, phone, password)
            VALUES (?, ?, ?, ?, ?)
        ''', (fullname, username, email, phone, password))
        conn.commit()
        conn.close()
        
        return redirect(url_for('catalog'))
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return redirect(url_for('catalog'))
    else:
        return "Invalid username or password!"

@app.route('/catalog')
def catalog():
    return render_template('catalog.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item = request.json.get('name')
    img = request.json.get('img')
    product = {"name": item, "img": img}
    cart.append(product)
    return jsonify({"status": "success", "item": product})

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    item_name = request.json.get('item')
    global cart
    cart = [item for item in cart if item['name'] != item_name]
    return jsonify({"status": "success", "items": cart})

@app.route('/get_cart')
def get_cart():
    return jsonify({"items": cart})

@app.route('/orders')
def orders():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM addresses')
    addresses = cursor.fetchall()
    conn.close()
    return render_template('orders.html', addresses=addresses)

@app.route('/submit_order', methods=['POST'])
def submit_order():
    address = request.form.get('address')
    payment_method = request.form.get('payment-method')
    items = ', '.join([item['name'] for item in cart])
    
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (address, payment_method, items)
        VALUES (?, ?, ?)
    ''', (address, payment_method, items))
    conn.commit()
    conn.close()
    
    cart.clear()  # Очищаем корзину после оформления заказа
    return redirect(url_for('orders'))

@app.route('/addresses', methods=['GET'])
def addresses():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM addresses')
    addresses = cursor.fetchall()
    conn.close()
    return render_template('addresses.html', addresses=addresses)

@app.route('/add_address', methods=['POST'])
def add_address():
    address = request.form.get('address')
    
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO addresses (address)
        VALUES (?)
    ''', (address,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('addresses'))

@app.route('/delete_address', methods=['POST'])
def delete_address():
    id = request.json.get('id')
    
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM addresses WHERE id=?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
