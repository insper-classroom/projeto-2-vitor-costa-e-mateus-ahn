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


@app.route('/imoveis/<int:id>', methods=['PUT'])
def atualizar_imovel(id):
    data = request.get_json()
    required_fields = ['logradouro', 'tipo_logradouro', 'bairro', 'cidade', 'cep', 'tipo', 'valor', 'data_aquisicao']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao'}), 400

    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute(
        'UPDATE imoveis SET logradouro = ?, tipo_logradouro = ?, bairro = ?, cidade = ?, cep = ?, tipo = ?, valor = ?, data_aquisicao = ? WHERE id = ?',
        (data["logradouro"], data["tipo_logradouro"], data["bairro"], data["cidade"], data["cep"], data["tipo"], data["valor"], data["data_aquisicao"], id)
    )
    conn.commit()
    rows = cursor.rowcount

    cursor.close()
    conn.close()

    if rows == 0:
        return jsonify({'error': 'Imóvel não encontrado'}), 404

    response = {
        'message': 'Imóvel atualizado com sucesso',
        '_links': criar_links_imovel(id)
    }
    return jsonify(response), 200

@app.route('/imoveis/<int:id>', methods=['DELETE'])
def deletar_imovel(id):

    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute(
        'DELETE FROM imoveis WHERE id = ?',
        (int(id),)
    )
    conn.commit()

    cursor.close()
    conn.close()

    if cursor.rowcount == 0:
        return {'erro' : 'Imovel não encontrado'}, 404

    return {'mensagem' : 'Imovel excluído com sucesso'}, 200

@app.route('/imoveis/tipo/<string:tipo>', methods=['GET'])
def listar_imoveis_tipo(tipo):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute('SELECT tipo, id, logradouro, tipo_logradouro, bairro, cidade, cep, valor, data_aquisicao FROM imoveis WHERE tipo = ?', (tipo,))
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()

    data = [criar_linha_imovel(row) for row in rows]
    
    response = {
        '_embedded': {'imoveis': data},
        '_links': {
            'self': {'href': '/imoveis/tipo/{tipo}', 'method': 'GET'},
            'create': {'href': '/imoveis/tipo/{tipo}', 'method': 'POST'}
        }
    }

    return jsonify(response), 200

@app.route('/imoveis/cidade/<string:cidade>', methods=['GET'])
def listar_imoveis_cidade(cidade):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute('SELECT tipo, id, logradouro, tipo_logradouro, bairro, cidade, cep, valor, data_aquisicao FROM imoveis WHERE cidade = ?', (cidade,))
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()

    data = [criar_linha_imovel(row) for row in rows]
    
    response = {
        '_embedded': {'imoveis': data},
        '_links': {
            'self': {'href': '/imoveis/cidade/{cidade}', 'method': 'GET'},
            'create': {'href': '/imoveis/cidade/{cidade}', 'method': 'POST'}
        }
    }

    return jsonify(response), 200