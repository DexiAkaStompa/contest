from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'la_tua_chiave_segreta'

# Connessione al database
def get_db_connection():
    conn = sqlite3.connect('contest.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    partecipanti = conn.execute('SELECT * FROM participants').fetchall()
    conn.close()
    return render_template('index.html', partecipanti=partecipanti)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Implementa qui la logica di autenticazione
        if username == 'LemonContest' and password == 'Madebydexi':  # Modifica con un metodo di autenticazione sicuro
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Accesso fallito. Controlla il tuo nome utente e/o password.')
    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    partecipanti = conn.execute('SELECT * FROM participants').fetchall()
    conn.close()
    return render_template('admin.html', partecipanti=partecipanti)

@app.route('/add_participant', methods=['POST'])
def add_participant():
    nome = request.form['name']
    cognome = request.form['surname']
    biglietti = int(request.form['tickets'])

    # Aggiungi il nuovo partecipante
    conn = get_db_connection()
    conn.execute('INSERT INTO participants (name, surname, tickets) VALUES (?, ?, ?)', (nome, cognome, biglietti))
    conn.commit()

    # Rimuovi i duplicati
    remove_duplicates(conn)

    conn.close()
    return redirect(url_for('admin_dashboard'))

def remove_duplicates(conn):
    # Trova tutti i partecipanti
    partecipanti = conn.execute('SELECT id, name, surname, SUM(tickets) as total_tickets FROM participants GROUP BY name, surname').fetchall()
    
    for partecipante in partecipanti:
        if partecipante['total_tickets'] > 1:
            # Rimuovi i duplicati lasciando solo una entry
            conn.execute('DELETE FROM participants WHERE name = ? AND surname = ? AND id != ?', (partecipante['name'], partecipante['surname'], partecipante['id']))
    
    conn.commit()

@app.route('/remove_participant/<int:id>', methods=['POST'])
def remove_participant(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM participants WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Partecipante rimosso con successo!')
    return redirect(url_for('admin_dashboard'))

@app.route('/add_tickets/<int:id>', methods=['POST'])
def add_tickets(id):
    additional_tickets = int(request.form['additional_tickets'])

    conn = get_db_connection()
    conn.execute('UPDATE participants SET tickets = tickets + ? WHERE id = ?', (additional_tickets, id))
    conn.commit()
    conn.close()
    flash('Biglietti aggiunti con successo!')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
