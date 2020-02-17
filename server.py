import re
from flask import Flask, render_template, redirect, session, flash, request
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
from datetime import datetime

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
INVALID_PASSWORD_REGEX = re.compile(r'^([^0-9]*|[^A-Z]*)$')

app = Flask(__name__)
app.secret_key = "Ninetails"
bcrypt = Bcrypt(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/registration", methods=['POST'])
def registration_post():
    is_valid = True
    if len(request.form['first_name']) < 2:
        flash("First name must be at least two characters.")
        is_valid = False

    if len(request.form['last_name']) < 2:
        flash("Last name must be at least two characters.")
        is_valid = False

    if not EMAIL_REGEX.match(request.form['email']):
        flash("Email must be valid")
        is_valid = False

    if len(request.form['password']) < 8:
        flash("Password must be at least eight characters.")
        is_valid = False

    if INVALID_PASSWORD_REGEX.match(request.form['password']):
        flash(
            "Password must have at least one uppercase character and at least one number.")
        is_valid = False

    if request.form['password'] != request.form['confirm']:
        flash("Passwords must match.")
        is_valid = False

    if not is_valid:
        return redirect("/")

    mysql = connectToMySQL('med_tracker')
    query = "INSERT into users (first_name, last_name, password, email, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(password)s, %(email)s, NOW(), NOW())"

    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'password': bcrypt.generate_password_hash(request.form['password']),
        'email': request.form['email']
    }

    user_id = mysql.query_db(query, data)
    if not user_id:
        flash("Failed to create user.")
        return redirect("/")

    session['user_id'] = user_id

    return redirect("/profile")


@app.route('/login', methods=['POST'])
def login():
    is_valid = True

    if len(request.form['email']) < 1:
        is_valid = False
        flash("Please enter email.")

    if len(request.form['password']) < 1:
        is_valid = False
        flash("Please enter password.")

    if not is_valid:
        return redirect("/")

    mysql = connectToMySQL("med_tracker")
    query = "SELECT * FROM users WHERE users.email = %(email)s"
    data = {
        'email': request.form['email']
    }
    user = mysql.query_db(query, data)

    if not user:
        flash("Must use valid email.")
        return redirect("/")

    hashed_pass = user[0]['password']

    if not bcrypt.check_password_hash(hashed_pass, request.form['password']):
        flash("Password invalid.")
        return redirect("/")

    session['user_id'] = user[0]['id']
    return redirect("/profile")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/profile')
def profile():
    user = get_current_user()

    if user is None:
        return redirect("/")

    mysql = connectToMySQL('med_tracker')
    query = "SELECT * FROM medications WHERE user_id = %(user_id)s"
    data = {
        'user_id': user['id']
    }
    medications = mysql.query_db(query, data)

    mysql = connectToMySQL('med_tracker')
    query = "SELECT medication_events.id AS id, medications.name AS medication_name, dose, dose_units, administered_at FROM medication_events JOIN medications WHERE medications.id = medication_events.medication_id AND medication_events.user_id = %(user_id)s"
    data = {
        'user_id': user['id']
    }
    medication_events = mysql.query_db(query, data)

    return render_template("profile.html", user=user, medications=medications, medication_events=medication_events)


@app.route('/medications/create', methods=['GET'])
def medications_create_get():
    user = get_current_user()

    if user is None:
        return redirect("/")

    return render_template("create_medication.html", user=user)


@app.route('/medications/create', methods=['POST'])
def medications_create_post():
    user = get_current_user()

    if user is None:
        return redirect("/")

    mysql = connectToMySQL('med_tracker')
    query = "INSERT INTO medications (user_id, name) VALUES (%(id)s, %(name)s)"
    data = {'id': session['user_id'],
            'name': request.form['medication_name']}
    mysql.query_db(query, data)

    return redirect("/profile")


@app.route('/medication_events/create', methods=['POST'])
def create_medication_event_post():
    user = get_current_user()

    if user is None:
        return redirect("/")

    is_valid = True

    if len(request.form['medication_id']) == 0:
        flash("Please select a medication")
        is_valid = False

    if len(request.form['dose']) == 0:
        flash("Please input dosage.")
        is_valid = False

    if request.form['dose'].isnumeric() == False:
        flash("Dosage must be numeric.")
        is_valid = False
    else:
        dose = int(request.form['dose'])

        if dose < 0:
            flash("Dosage must be greater than 0.")
            is_valid = False

        if dose > 2147483647:
            flash("Dosage must be less than 2,147,483,647.")
            is_valid = False

    if len(request.form['dose_units']) == 0:
        flash("Please provide dosage units.")
        is_valid = False

    # matches the enum in the database
    valid_dose_units = [
        'Milligrams (mg)',
        'Micrograms (mcg)',
        'Grams (g)',
        'Milliliters (ml)',
        'Teaspoon (tsp)',
        'Tablespoon (Tbsp)',
        'International Units (IU)',
        'Other'
    ]

    if request.form['dose_units'] not in valid_dose_units:
        flash(
            f"Please choose one of {', '.join(valid_dose_units)} for dose units.")
        is_valid = False

    if len(request.form['administered_at']) == 0:
        flash("Please fill date and time administered field.")
        is_valid = False

    if not is_valid:
        return redirect("/medication_events/create")

    mysql = connectToMySQL('med_tracker')
    query = "INSERT INTO medication_events (medication_id, user_id, dose, dose_units, administered_at) VALUES (%(medication_id)s, %(user_id)s, %(dose)s, %(dose_units)s, %(administered_at)s)"
    data = {
        'medication_id': request.form['medication_id'],
        'user_id': user['id'],
        'dose': request.form['dose'],
        'dose_units': request.form['dose_units'],
        'administered_at': request.form['administered_at']
    }

    mysql.query_db(query, data)

    return redirect("/profile")


@app.route('/medication_events/create', methods=["GET"])
def create_medication_event_get():
    user = get_current_user()

    if user is None:
        return redirect("/")

    query = "SELECT id, name FROM medications WHERE user_id = %(user_id)s"
    data = {
        'user_id': user['id']
    }
    mysql = connectToMySQL('med_tracker')
    medications = mysql.query_db(query, data)

    return render_template("create_medication_event.html", user=user, medications=medications)


@app.route('/medication_events/<medication_event_id>/delete')
def delete_med_event(medication_event_id):
    user = get_current_user()

    if user is None:
        return redirect("/")

    query = "DELETE FROM medication_events WHERE id = %(medication_event_id)s AND user_id = %(user_id)s"
    data = {
        'user_id': user['id'],
        'medication_event_id': medication_event_id
    }
    mysql = connectToMySQL('med_tracker')
    mysql.query_db(query, data)

    return redirect("/profile")

@app.route('/medication_events/<medication_event_id>/edit', methods=['GET'])
def medication_events_edit_get(medication_event_id):
    user = get_current_user()

    if user is None:
        return redirect("/")

    query = "SELECT * FROM medication_events WHERE id = %(medication_event_id)s AND user_id = %(user_id)s"
    data = {
        'user_id': user['id'],
        'medication_event_id': medication_event_id
    }
    mysql = connectToMySQL('med_tracker')
    medication_events = mysql.query_db(query, data)

    query = "SELECT id, name FROM medications WHERE user_id = %(user_id)s"
    data = {
        'user_id': user['id']
    }
    mysql = connectToMySQL('med_tracker')
    medications = mysql.query_db(query, data)

    return render_template("edit_medication_event.html", user=user, medications=medications, medication_event=medication_events[0])

@app.route('/medication_events/<medication_event_id>/edit', methods=['POST'])
def medication_events_edit_post(medication_event_id):
    user = get_current_user()

    if user is None:
        return redirect("/")

    query = "UPDATE medication_events SET medication_id = %(medication_id)s, dose = %(dose)s, dose_units = %(dose_units)s, administered_at = %(administered_at)s WHERE id = %(medication_event_id)s AND user_id = %(user_id)s"
    data = {
        'medication_event_id': medication_event_id,
        'user_id': user['id'],
        'medication_id': request.form['medication_id'],
        'dose': request.form['dose'],
        'dose_units': request.form['dose_units'],
        'administered_at': request.form['administered_at']
    }
    mysql = connectToMySQL('med_tracker')
    mysql.query_db(query, data)

    return redirect("/profile")


@app.route('/medications/<medication_id>/edit', methods=['POST'])
def medications_edit_post(medication_id):
    user = get_current_user()

    if user is None:
        return redirect("/")

    query = "UPDATE medications SET name = %(name)s WHERE id = %(medication_id)s AND user_id = %(user_id)s"
    data = {
        'name': request.form["medication_name"],
        'user_id': user['id'],
        'medication_id': medication_id
    }
    mysql = connectToMySQL('med_tracker')
    mysql.query_db(query, data)

    return redirect("/profile")


@app.route('/medications/<medication_id>/edit', methods=['GET'])
def medication_edit_get(medication_id):
    user = get_current_user()

    if user is None:
        return redirect("/")

    query = "SELECT id, name FROM medications WHERE id = %(medication_id)s AND user_id = %(user_id)s"
    data = {
        'medication_id': medication_id,
        'user_id': user['id']
    }
    mysql = connectToMySQL('med_tracker')
    medications = mysql.query_db(query, data)

    return render_template("edit_medication.html", user=user, medication=medications[0])


@app.route('/medications/<medication_id>/delete')
def delete_med(medication_id):
    user = get_current_user()

    if user is None:
        return redirect("/")

    query = "DELETE FROM medication_events WHERE medication_id = %(medication_id)s AND user_id = %(user_id)s"
    data = {
        'user_id': user['id'],
        'medication_id': medication_id
    }
    mysql = connectToMySQL('med_tracker')
    mysql.query_db(query, data)

    query = "DELETE FROM medications WHERE id = %(medication_id)s AND user_id = %(user_id)s"
    mysql = connectToMySQL('med_tracker')
    mysql.query_db(query, data)

    return redirect("/profile")


def get_current_user():
    if 'user_id' not in session:
        return None

    query = "SELECT * FROM users WHERE users.id = %(user_id)s LIMIT 1"
    data = {'user_id': session['user_id']}

    mysql = connectToMySQL('med_tracker')

    user = mysql.query_db(query, data)

    if user is None:
        return None

    return user[0]


if __name__ == "__main__":
    app.run(debug=True)
