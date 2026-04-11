import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
uri = os.environ.get("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///local_test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- ROUTES ---

@app.route('/')
def home():
    # Fixed: This is now inside a function and properly indented
    return "Bincom Test is Running! Go to /polling-unit/8 to see results."

@app.route('/polling-unit/<int:id>')
def unit_result(id):
    query = text("SELECT * FROM announced_pu_results WHERE polling_unit_uniqueid = :id")
    results = db.session.execute(query, {'id': id}).fetchall()
    return render_template('unit.html', results=results)

@app.route('/lga', methods=['GET', 'POST'])
def lga_total():
    # Fixed: Corrected the string literal syntax error on line 27
    lgas = db.session.execute(text("SELECT lga_id, lga_name FROM lga")).fetchall()
    selected_results = []
    
    if request.method == 'POST':
        lga_id = request.form.get('lga_id')
        query = text("""
            SELECT party_abbreviation, SUM(party_score) as total_score
            FROM announced_pu_results
            JOIN polling_unit ON announced_pu_results.polling_unit_uniqueid = polling_unit.uniqueid
            WHERE polling_unit.lga_id = :lga_id
            GROUP BY party_abbreviation
        """)
        selected_results = db.session.execute(query, {'lga_id': lga_id}).fetchall()
        
    return render_template('lga.html', lgas=lgas, results=selected_results)

@app.route('/add-result', methods=['GET', 'POST'])
def add_result():
    if request.method == 'POST':
        pu_id = request.form.get('unit_id')
        party = request.form.get('party')
        score = request.form.get('score')
        
        query = text("""
            INSERT INTO announced_pu_results (polling_unit_uniqueid, party_abbreviation, party_score)
            VALUES (:pu_id, :party, :score)
        """)
        db.session.execute(query, {'pu_id': pu_id, 'party': party, 'score': score})
        db.session.commit()
        return "Result Submitted Successfully!"
        
    return render_template('add.html')
    
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
