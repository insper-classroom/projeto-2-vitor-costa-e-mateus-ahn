import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_NAME = 'banco.db'


def conectar_banco():
    return sqlite3.connect(DB_NAME)


def criar_links_imovel(imovel_id):
    return {
        'self': {'href': f'/imoveis/{imovel_id}', 'method': 'GET'},
        'update': {'href': f'/imoveis/{imovel_id}', 'method': 'PUT'},
        'delete': {'href': f'/imoveis/{imovel_id}', 'method': 'DELETE'}
    }


def criar_linha_imovel(row):
    return {
        'id': row[0],
        'logradouro': row[1],
        'tipo_logradouro': row[2],
        'bairro': row[3],
        'cidade': row[4],
        'cep': row[5],
        'tipo': row[6],
        'valor': row[7],
        'data_aquisicao': row[8],
        '_links': criar_links_imovel(row[0])
    }


@app.route('/imoveis', methods=['GET'])
def listar_imoveis():
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute('SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis')
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()

    data = [criar_linha_imovel(row) for row in rows]
    
    response = {
        '_embedded': {'imoveis': data},
        '_links': {
            'self': {'href': '/imoveis', 'method': 'GET'},
            'create': {'href': '/imoveis', 'method': 'POST'}
        }
    }

    return jsonify(response), 200


@app.route('/imoveis/<int:id>', methods=['GET'])
def obter_imovel(id):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute('SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE id = ?', (id,))
    row = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if row:
        imovel = criar_linha_imovel(row)
        return jsonify(imovel), 200
    else:
        return jsonify({'error': 'Imóvel não encontrado'}), 404
    
    
@app.route('/imoveis', methods=['POST'])
def criar_imovel():
    data = request.get_json()
    required_fields = ['logradouro', 'tipo_logradouro', 'bairro', 'cidade', 'cep', 'tipo', 'valor', 'data_aquisicao']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao'}), 400

    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute(
        'INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (data['logradouro'], data['tipo_logradouro'], data['bairro'], data['cidade'], data['cep'], data['tipo'], data['valor'], data['data_aquisicao'])
    )
    conn.commit()
    new_id = cursor.lastrowid
    
    cursor.close()
    conn.close()

    response = {
        'id': new_id,
        '_links': criar_links_imovel(new_id)
    }
    return jsonify(response), 201