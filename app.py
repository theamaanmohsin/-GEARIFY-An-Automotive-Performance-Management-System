from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'gearify_super_secret_key'

# --- SAFE DATA HANDLING ---
def get_data_path(filename):
    """Creates the data folder if it doesn't exist."""
    if not os.path.exists('data'):
        os.makedirs('data')
    return os.path.join('data', filename)

def load_data(filename):
    """Reads JSON files. Returns empty list or dict if file is missing."""
    path = get_data_path(filename)
    
    # Default structures
    if filename == 'prices.json': default = {}
    elif filename == 'settings.json': default = {"admin_key": "gearify2025"}
    else: default = []

    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return default
    
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default

def save_data(filename, data):
    """Writes data to JSON files."""
    path = get_data_path(filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

# --- INITIAL SETUP ---
prices_data = load_data('prices.json')
if not prices_data: 
    save_data('prices.json', {
        "oil": {"Shell Helix HX7 (10W-40)": 4500, "ZIC X7 (5W-30)": 5200, "Caltex Havoline (20W-50)": 3800},
        "air_filter": {"Leppon Premium Air Filter": 1800, "Wix High-Flow Filter": 2500, "Guard Autozone Filter": 1200},
        "oil_filter": {"Vic C-110 (Japan)": 1500, "Leppon Performance": 1100, "Guard Standard": 850}
    })

settings_data = load_data('settings.json')
if not settings_data:
    save_data('settings.json', {"admin_key": "gearify2025"})

# --- GLOBAL SECURITY GUARD ---
@app.before_request
def require_login():
    """Prevents access to private pages if not logged in."""
    allowed_routes = ['login', 'register', 'about', 'team', 'project', 'home', 'static']
    if 'user' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))

# --- ROUTES ---

@app.route('/')
def home():
    return redirect(url_for('about'))

@app.route('/about')
def about(): return render_template('about.html')
@app.route('/team')
def team(): return render_template('team.html')
@app.route('/project')
def project(): return render_template('project.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        users = load_data('users.json')
        
        for user in users:
            if user.get('username') == username and user.get('password') == password:
                if user.get('role') == role:
                    session['user'] = username
                    session['role'] = role
                    return redirect(url_for('dashboard'))
                else:
                    flash(f'Incorrect Role! You are registered as {user.get("role")}.')
                    return redirect(url_for('login'))
        flash('Invalid Username or Password!')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        secret_key = request.form.get('secret_key', '').strip()
        
        settings = load_data('settings.json')
        current_admin_key = settings.get('admin_key', 'gearify2025')

        if role == 'admin' and secret_key != current_admin_key:
            flash(f'Wrong Admin Secret Key! Access Denied.')
            return redirect(url_for('register'))

        users = load_data('users.json')
        for user in users:
            if user.get('username') == username:
                flash('Username exists.')
                return redirect(url_for('login'))
        
        users.append({'username': username, 'password': password, 'role': role})
        save_data('users.json', users)
        flash('Registered! Please Login.')
        return redirect(url_for('login'))
    return render_template('register.html')

# --- DASHBOARD & HUB ---

@app.route('/dashboard')
def dashboard():
    history = load_data('history.json')
    prices = load_data('prices.json')
    all_users = []
    current_key = ""

    if session.get('role') == 'admin':
        all_users = load_data('users.json')
        # Load the key to show it to the admin
        current_key = load_data('settings.json').get('admin_key', 'gearify2025')
    else:
        history = [h for h in history if h.get('username') == session['user']]
    
    # Search Logic
    query = request.args.get('search')
    if query:
        query = query.lower()
        history = [h for h in history if query in h['car'].lower() or query in h.get('reg_no', '').lower() or query in h['date']]

    # Section Logic (Default: 'menu')
    # Options: menu, services, records, prices, users, security
    section = request.args.get('section', 'menu')
    
    if query:
        section = 'records' # Force records view if searching

    return render_template('dashboard.html', 
                           history=history, 
                           role=session.get('role'), 
                           prices=prices, 
                           all_users=all_users, 
                           admin_key=current_key,
                           section=section)

# --- ACTIONS ---

@app.route('/maintenance', methods=['GET', 'POST'])
def maintenance():
    prices = load_data('prices.json')
    cars = load_data('cars.json')

    if request.method == 'POST':
        reg_no = request.form['reg_no'].upper().strip()
        company, model, year = request.form['company'], request.form['model'], request.form['year']
        current_km = int(request.form['km'])
        
        # Safe Data Retrieval
        oil_choice = request.form.get('oil')
        air_choice = request.form.get('air_filter')
        oil_filter_choice = request.form.get('oil_filter')

        if reg_no not in cars:
            cars[reg_no] = {"company": company, "model": model, "year": year}
            save_data('cars.json', cars)

        total = 0
        parts_list = []

        # Logic to handle "None" (Skip)
        if oil_choice and oil_choice != "None":
            cost = prices['oil'].get(oil_choice, 0)
            total += cost
            parts_list.append({"name": f"Oil: {oil_choice}", "price": cost})

        if air_choice and air_choice != "None":
            cost = prices['air_filter'].get(air_choice, 0)
            total += cost
            parts_list.append({"name": f"Air: {air_choice}", "price": cost})

        if oil_filter_choice and oil_filter_choice != "None":
            cost = prices['oil_filter'].get(oil_filter_choice, 0)
            total += cost
            parts_list.append({"name": f"Oil Filter: {oil_filter_choice}", "price": cost})

        receipt = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "username": session['user'],
            "reg_no": reg_no,
            "car": f"{company} {model} ({year})",
            "parts": parts_list,
            "total": total,
            "next_km": current_km + 15000
        }
        
        history = load_data('history.json')
        history.append(receipt)
        save_data('history.json', history)
        return render_template('receipt.html', receipt=receipt)
        
    return render_template('maintenance.html', prices=prices)

@app.route('/update_prices', methods=['POST'])
def update_prices():
    if session.get('role') != 'admin': return redirect(url_for('dashboard'))
    
    new_prices = {
        "oil": {
            "Shell Helix HX7 (10W-40)": int(request.form['oil_1']),
            "ZIC X7 (5W-30)": int(request.form['oil_2']),
            "Caltex Havoline (20W-50)": int(request.form['oil_3'])
        },
        "air_filter": {
            "Leppon Premium Air Filter": int(request.form['air_1']),
            "Wix High-Flow Filter": int(request.form['air_2']),
            "Guard Autozone Filter": int(request.form['air_3'])
        },
        "oil_filter": {
            "Vic C-110 (Japan)": int(request.form['oilf_1']),
            "Leppon Performance": int(request.form['oilf_2']),
            "Guard Standard": int(request.form['oilf_3'])
        }
    }
    save_data('prices.json', new_prices)
    flash('Prices Updated Successfully!')
    return redirect(url_for('dashboard', section='prices'))

@app.route('/update_key', methods=['POST'])
def update_key():
    if session.get('role') != 'admin': return redirect(url_for('dashboard'))
    
    new_key = request.form['new_key'].strip()
    if new_key:
        save_data('settings.json', {"admin_key": new_key})
        flash('Security Key Updated Successfully!')
    else:
        flash('Key cannot be empty!')
        
    # Redirects back to the SECURITY section
    return redirect(url_for('dashboard', section='security'))

@app.route('/delete/<id>')
def delete(id):
    if session.get('role') == 'admin':
        history = [h for h in load_data('history.json') if h.get('id') != id]
        save_data('history.json', history)
        flash('Record Deleted.')
    return redirect(url_for('dashboard', section='records'))

@app.route('/delete_user/<username>')
def delete_user(username):
    if session.get('role') == 'admin':
        if username == session['user']:
            flash("You cannot delete your own account!")
            return redirect(url_for('dashboard', section='users'))
        users = [u for u in load_data('users.json') if u.get('username') != username]
        save_data('users.json', users)
        flash(f'User {username} deleted successfully.')
    return redirect(url_for('dashboard', section='users'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True) 