from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error

load_dotenv('.cred')
config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT')),
    'ssl_ca': os.getenv('SSL_CA_PATH')
}

app = Flask(__name__)


def conectar_banco():
    print(config)
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            return conn
    except Error as err:
        print(f'Erro: {err}')
        return None


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

    cursor.execute('SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE id = %s', (id,))
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
        'INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
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
        'UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, bairro = %s, cidade = %s, cep = %s, tipo = %s, valor = %s, data_aquisicao = %s WHERE id = %s',
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

    cursor.execute("DELETE FROM imoveis WHERE id = %s", (id,))

    conn.commit()
    rows = cursor.rowcount

    cursor.close()
    conn.close()

    if rows == 0:
        return jsonify({'error': 'Imóvel não encontrado'}), 404

    response = {
        'message': 'Imóvel excluído com sucesso',
        '_links': {
            'create': {'href': '/imoveis', 'method': 'POST'},
            'list': {'href': '/imoveis', 'method': 'GET'}
        }
    }
    return jsonify(response), 200


@app.route('/imoveis/tipo/<string:tipo>', methods=['GET'])
def listar_imoveis_por_tipo(tipo):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute('SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE tipo = %s', (tipo,))
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()

    data = [criar_linha_imovel(row) for row in rows]
    
    response = {
        '_embedded': {'imoveis': data},
        '_links': {
            'self': {'href': f'/imoveis/tipo/{tipo}', 'method': 'GET'},
            'list': {'href': '/imoveis', 'method': 'GET'},
            'create': {'href': '/imoveis', 'method': 'POST'}
        }
    }

    return jsonify(response), 200


@app.route('/imoveis/cidade/<string:cidade>', methods=['GET'])
def listar_imoveis_por_cidade(cidade):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute('SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE cidade = %s', (cidade,))
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()

    data = [criar_linha_imovel(row) for row in rows]

    response = {
        '_embedded': {'imoveis': data},
        '_links': {
            'self': {'href': f'/imoveis/cidade/{cidade}', 'method': 'GET'},
            'list': {'href': '/imoveis', 'method': 'GET'},
            'create': {'href': '/imoveis', 'method': 'POST'}
        }
    }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True)