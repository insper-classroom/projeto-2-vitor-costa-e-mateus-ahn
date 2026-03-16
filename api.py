import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_NAME = 'banco.db'

def conectar_banco():
    return sqlite3.connect(DB_NAME)

@app.route('/imoveis', methods=['GET'])
def listar_imoveis():
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM imoveis')
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()

    data = []
    for row in rows:
        data.append({
            'id': row[0],
            'logradouro': row[1],
            'tipo_logradouro': row[2],
            'bairro': row[3],
            'cidade': row[4],
            'cep': row[5],
            'tipo': row[6],
            'valor': row[7],
            'data_aquisicao': row[8]
        })

    return jsonify(data)