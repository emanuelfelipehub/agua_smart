from datetime import datetime
import sqlite3
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = 'emanuel'

def get_db_connection():
  conn = sqlite3.connect('database.db')
  conn.row_factory = sqlite3.Row 
  return conn

def init_db():
  conn = get_db_connection()
  conn.execute('''
        CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            consumo REAL NOT NULL,
            observacao TEXT
        )
    ''')
  conn.commit()
  conn.close()


@app.route('/')
def index():
  conn = get_db_connection()
  leituras = conn.execute(
      'SELECT * FROM leituras ORDER BY id DESC'
  ).fetchall()

  alerta = None
  if len(leituras) >= 2:
    ultimo_consumo = leituras[0]['consumo']
    penultimo_consumo = leituras[1]['consumo']


    if ultimo_consumo > penultimo_consumo * 1.4:
      alerta = (
          'Atenção: Detectamos um aumento superior a 40% no consumo de água!'
      )

  conn.close()
  return render_template('index.html', leituras=leituras, alerta=alerta)


@app.route('/registrar', methods=('GET', 'POST'))
def registrar():
  if request.method == 'POST':
    consumo = request.form['consumo']
    observacao = request.form['observacao']
    data = datetime.now().strftime('%Y-%m-%d %H:%M')

    if consumo:
      conn = get_db_connection()
      conn.execute(
          'INSERT INTO leituras (data, consumo, observacao) VALUES (?, ?, ?)',
          (data, float(consumo), observacao),
      )
      conn.commit()
      conn.close()
      return redirect(url_for('index'))

  return render_template('formulario.html')


if __name__ == '__main__':
  init_db()
  app.run(debug=True)