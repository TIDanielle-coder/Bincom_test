import os
import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

# This part ensures Render finds your database file
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, "bincom_test.db")

def get_db():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return "Bincom Test is Running! Go to /polling-unit/8 to see results."

@app.route('/polling-unit/<int:id>')
def unit_result(id):
    db = get_db()
    results = db.execute("SELECT * FROM announced_pu_results WHERE polling_unit_uniqueid = ?", (id,)).fetchall()
    db.close()
    return render_template('unit.html', results=results, unit_id=id)

@app.route('/lga', methods=['GET', 'POST'])
def lga_total():
    db = get_db()
    lgas = db.execute("SELECT lga_id, lga_name FROM lga").fetchall()
    selected_results = []
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
