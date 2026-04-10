from flask import Flask, render_template, request, redirect
import os
import sqlite3

app = Flask(__name__)

# ----- paste the new code here-----
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'Bincom_test.db')
def get_db():
    conn= sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
def get_db():
    return mysql.connector.connect(**db_config)

# QUESTION 1: Individual Polling Unit Result
@app.route('/polling-unit/<int:id>')
def unit_result(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM announced_pu_results WHERE polling_unit_uniqueid = %s"
    cursor.execute(query, (id,))
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('unit.html', results=results, unit_id=id)

# QUESTION 2: Total LGA Results
@app.route('/lga', methods=['GET', 'POST'])
def lga_total():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get LGAs for the dropdown select box
    cursor.execute("SELECT lga_id, lga_name FROM lga")
    lgas = cursor.fetchall()
    
    selected_results = []
    if request.method == 'POST':
        lga_id = request.form.get('lga_id')
        # Summing results manually from all polling units in the selected LGA
        query = """
            SELECT party_abbreviation, SUM(party_score) as total_score 
            FROM announced_pu_results 
            JOIN polling_unit ON announced_pu_results.polling_unit_uniqueid = polling_unit.uniqueid 
            WHERE polling_unit.lga_id = %s 
            GROUP BY party_abbreviation
        """
        cursor.execute(query, (lga_id,))
        selected_results = cursor.fetchall()
        
    cursor.close()
    db.close()
    return render_template('lga.html', lgas=lgas, results=selected_results)

# QUESTION 3: Store Results for New Polling Unit
@app.route('/add-result', methods=['GET', 'POST'])
def add_result():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        # In a real app, you'd loop through all parties. Here is a simple example for one.
        query = "INSERT INTO announced_pu_results (polling_unit_uniqueid, party_abbreviation, party_score, entered_by_user, date_entered) VALUES (%s, %s, %s, %s, NOW())"
        data = (request.form['unit_id'], request.form['party'], request.form['score'], 'Daniel Tayo')
        cursor.execute(query, data)
        db.commit()
        cursor.close()
        db.close()
        return "Result Submitted Successfully!"
    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True)

















<h2>Results for Polling Unit #{{ unit_id }}</h2>
<table border="1">
    <tr><th>Party</th><th>Score</th></tr>
    {% for row in results %}
    <tr><td>{{ row.party_abbreviation }}</td><td>{{ row.party_score }}</td></tr>
    {% endfor %}
</table>














<form method="POST">
    <select name="lga_id">
        {% for lga in lgas %}
        <option value="{{ lga.lga_id }}">{{ lga.lga_name }}</option>
        {% endfor %}
    </select>
    <button type="submit">View Summed Results</button>
</form>

{% if results %}
<h3>Summed Results for Selected LGA</h3>
<table border="1">
    <tr><th>Party</th><th>Total Summed Score</th></tr>
    {% for row in results %}
    <tr><td>{{ row.party_abbreviation }}</td><td>{{ row.total_score }}</td></tr>
    {% endfor %}
</table>
{% endif %}















<h3>Add New Polling Unit Result</h3>
<form method="POST">
    <input type="text" name="unit_id" placeholder="Polling Unit ID" required><br>
    <input type="text" name="party" placeholder="Party (e.g. PDP)" required><br>
    <input type="number" name="score" placeholder="Score" required><br>
    <button type="submit">Submit Result</button>
</form>
