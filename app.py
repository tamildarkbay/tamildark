from flask import Flask, render_template, request, redirect, url_for, session
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import gspread

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure key

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDS_FILE = 'credentials.json'  # Your Google Service Account credentials
creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=creds)
client = gspread.authorize(creds)

# Google Sheets IDs
USER_SHEET_ID = '1fLF0iL9SNcG98JD76p-nQ8K4KYzM45SmQ6R9CEz_iyE'
MOVIE_SHEET_ID = '1ttpLnqQD-0JrFa7XJJV17yXxZOXRORxKansUlzjBzzY'
SLIDESHOW_SHEET_ID = '19D4sKTjwHDQ6ihWk4dUjewJLsmluey97MfvAP7-cFtc'

def get_users():
    sheet = client.open_by_key(USER_SHEET_ID).sheet1
    return sheet.get_all_records()

def add_user(name, email, password):
    sheet = client.open_by_key(USER_SHEET_ID).sheet1
    user_id = str(uuid.uuid4())
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    sheet.append_row([user_id, name, email, hashed_password])

def get_slideshow_movies():
    sheet = client.open_by_key(SLIDESHOW_SHEET_ID).sheet1
    return sheet.get_all_records()

def get_movies():
    sheet = client.open_by_key(MOVIE_SHEET_ID).sheet1
    return sheet.get_all_records()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = get_users()
        for user in users:
            if user['email'] == email and check_password_hash(user['password'], password):
                session['user_id'] = user['user_id']
                session['name'] = user['name']
                session['email'] = user['email']
                return redirect(url_for('home'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        users = get_users()
        if any(user['email'] == email for user in users):
            return render_template('signup.html', error='Email already exists')
        add_user(name, email, password)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    slideshow_movies = get_slideshow_movies()
    return render_template('home.html', slideshow_movies=slideshow_movies)

@app.route('/movies')
def movies():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    movies = get_movies()
    return render_template('movies.html', movies=movies)

@app.route('/about')
def about():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('about.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', name=session['name'], email=session['email'])

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('name', None)
    session.pop('email', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
