import os
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text 
from flask import Flask, render_template, request

app = Flask(__name__)

# This gets the URL from Render's Environment Variables
uri = os.environ.get("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
@app.route('/')
def home():
    return "Bincom Test is Running! Go to /polling-unit/8 to see results."

@app.route('/polling-unit/<int:id>')
def unit_result(id):
    query = text("SELECT * FROM announced_pu_results WHERE polling_unit_uniqueid = :id")
    results = db.session.execute(query, {'id': id}).fetchall()
    return render_template('unit.html', results=
        lgas = 
    db.session.execute(text("SELECT lga_id, 
    lga_name FROM lga")).fetchall()
    if request.method == 'POST':
        lga_id = request.form.get('lga_id')
        query = """
            SELECT party_abbreviation, SUM(party_score) as total_score 
            FROM announced_pu_results 
            JOIN polling_unit ON announced_pu_results.polling_unit_uniqueid = polling_unit.uniqueid 
            WHERE polling_unit.lga_id = ? 
            GROUP BY party_abbreviation
        """
        selected_results = db.execute(query, (lga_id,)).fetchall()
    db.close()
    return render_template('lga.html', lgas=lgas, results=selected_results)

@app.route('/add-result', methods=['GET', 'POST'])
def add_result():
    if request.method == 'POST':
        db = get_db()
        query = "INSERT INTO announced_pu_results (polling_unit_uniqueid, party_abbreviation, party_score, entered_by_user, date_entered) VALUES (?, ?, ?, ?, datetime('now'))"
        db.execute(query, (request.form['unit_id'], request.form['party'], request.form['score'], 'Daniel Tayo'))
        db.commit()
        db.close()
        return "Result Submitted Successfully!"
    return render_template('add.html')

if __name__ == "__main__":
    app.run(debug=True)
