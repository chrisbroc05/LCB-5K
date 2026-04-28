import os
from flask import Flask, render_template, request, redirect, url_for, g, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.secret_key = 'dev'  # Set a secret key for session management

# Database setup
DATABASE = 'event_database.db'

# Predefined lists for Cancer Types
CANCER_TYPES = [
    "Breast Cancer", "Lung Cancer", "Prostate Cancer", "Colorectal Cancer",
    "Skin Cancer", "Lymphoma", "Leukemia", "Pancreatic Cancer",
    "Ovarian Cancer"
]

# SQL schema as a string
SCHEMA = '''
DROP TABLE IF EXISTS participants;
DROP TABLE IF EXISTS teams;

CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    cancer_type TEXT NOT NULL,
    team TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    date TEXT NOT NULL  -- Added date column
);
'''


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.executescript(SCHEMA)
        db.commit()


# Function to connect to Google Sheets
def connect_to_google_sheets():
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Add your service account credentials
    creds = ServiceAccountCredentials.from_json_keyfile_name('k-event-9ce08cc64855.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet by name
    sheet = client.open("5K Sign Up").sheet1  # Change to your sheet name

    return sheet


# Routes
@app.route('/')
def home():
    db = get_db()
    participants = db.execute('SELECT name, team FROM participants ORDER BY id DESC LIMIT 10').fetchall()
    teams = db.execute('SELECT name FROM teams').fetchall()

    # Convert the list of teams into a dictionary for easier access in the template
    teams_dict = {team['name']: None for team in teams}

    return render_template('home.html', participants=participants, teams=teams_dict)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    db = get_db()  # Ensure the database connection is established here
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        date = request.form['date']
        cancer_type = request.form['cancer_type']
        other_cancer_type = request.form.get('other_cancer_type', '').strip()
        team = request.form['team']
        other_team_name = request.form.get('other_team_name', '').strip()

        # Check if email already exists in Google Sheets
        sheet = connect_to_google_sheets()
        existing_emails = [row['Email'] for row in sheet.get_all_records()]  # Use the header name
        if email in existing_emails:
            flash("Looks like you are already registered, please join an existing team below.", "info")
            return redirect(url_for('teams'))  # Redirect to the teams page

        # Use the other cancer type if specified
        if cancer_type == 'Other' and other_cancer_type:
            cancer_type = other_cancer_type

        # Use the other team name if specified
        if team == 'Other' and other_team_name:
            team = other_team_name

        # Hash the password before storing
        password_hash = generate_password_hash(password)

        # Insert the participant
        db.execute(
            'INSERT INTO participants (name, email, cancer_type, team, password_hash, date) VALUES (?, ?, ?, ?, ?, ?)',
            (name, email, cancer_type, team, password_hash, date))

        # Check if the new team needs to be added
        if team not in [row['name'] for row in db.execute('SELECT name FROM teams').fetchall()]:
            db.execute('INSERT INTO teams (name) VALUES (?)', (team,))

        # Commit the changes
        db.commit()

        # Connect to Google Sheets and append the data
        sheet.append_row([name, email, cancer_type, team, date])  # Exclude the password

        return redirect(url_for('team', team_name=team))  # Redirect to the team page after sign-up

    # Fetch teams from the database for the dropdown
    teams = db.execute('SELECT name FROM teams').fetchall()
    return render_template('signup.html', cancer_types=CANCER_TYPES, teams=[team['name'] for team in teams])


@app.route('/teams', methods=['GET', 'POST'])
def teams():
    db = get_db()
    teams = db.execute('SELECT name FROM teams').fetchall()
    team_members_count = {
        team['name']: db.execute('SELECT COUNT(*) FROM participants WHERE team = ?', (team['name'],)).fetchone()[0] for
        team in teams}
    return render_template('teams.html', teams=team_members_count)


@app.route('/team/<team_name>', methods=['GET'])
def team(team_name):
    db = get_db()
    team_members = db.execute('SELECT name, cancer_type FROM participants WHERE team = ?', (team_name,)).fetchall()
    return render_template('team.html', team_name=team_name, members=team_members)


@app.route('/join_team', methods=['POST'])
def join_team():
    email = request.form['email']  # Get the email from the form
    password = request.form['password']  # Get the password from the form
    cancer_type = request.form['cancer_type']  # Get the cancer type from the form
    date = request.form['date']  # Get the date from the form
    team_name = request.form['team']  # Get the selected team from the dropdown

    # Verify the password
    db = get_db()
    user = db.execute('SELECT * FROM participants WHERE email = ?', (email,)).fetchone()
    if user is None or not check_password_hash(user['password_hash'], password):
        flash("Invalid email or password.", "danger")
        return redirect(url_for('teams'))

    # Update the participant's team in the database
    db.execute('UPDATE participants SET team = ?, cancer_type = ?, date = ? WHERE email = ?',
               (team_name, cancer_type, date, email))
    db.commit()

    # Connect to Google Sheets and update the data
    sheet = connect_to_google_sheets()
    # Find the row for the participant and update the team (this is a simple approach)
    participants = sheet.get_all_records()
    for row in participants:
        if row['Email'] == email:  # Match by email
            sheet.update_cell(row['Row'], 4, team_name)  # Assuming team is in the 4th column
            sheet.update_cell(row['Row'], 3, cancer_type)  # Assuming cancer type is in the 3rd column
            sheet.update_cell(row['Row'], 5, date)  # Assuming date is in the 5th column

    flash("Successfully joined the team!", "success")
    return redirect(url_for('teams'))  # Redirect to the teams page


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Fetch the user by email
        user = db.execute('SELECT * FROM participants WHERE email = ?', (email,)).fetchone()
        if user is None:
            return "Email not found", 400

        # Verify the password
        if check_password_hash(user['password_hash'], password):
            # Password is correct, log the user in
            return redirect(url_for('dashboard'))  # Redirect to a dashboard or home page
        else:
            return "Incorrect password", 400

    return render_template('login.html')  # Render the login form


@app.route('/participants')
def participants():
    db = get_db()
    participants = db.execute('SELECT name, email, cancer_type, team FROM participants ORDER BY team, name').fetchall()
    return render_template('participants.html', participants=participants)


@app.route('/location')
def location():
    return render_template('location.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.cli.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    print('Initialized the database.')


if __name__ == '__main__':
    app.run(debug=True)