import pytest
from unittest.mock import patch, MagicMock
from api import app, conectar_banco


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch('api.conectar_banco')
def test_listar_imoveis(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.fetchall.return_value = [
        (1, 'Nicole Common', 'Travessa', 'Lake Danielle', 'Judymouth', '85184', 'casa em condominio', 488423.52, '2017-07-29'),
        (2, 'Price Prairie', 'Travessa', 'Colonton', 'North Garyville', '93354', 'casa em condominio', 260069.89, '2021-11-30'),
        (3, 'Taylor Ranch', 'Avenida', 'West Jennashire', 'Katherinefurt', '51116', 'apartamento', 815969.92, '2020-04-24')
    ]

    response = client.get('/imoveis')

    assert response.status_code == 200
    response_data = response.get_json()
    
    # Verifica estrutura HATEOAS
    assert '_embedded' in response_data
    assert '_links' in response_data
    assert 'imoveis' in response_data['_embedded']
    
    imoveis = response_data['_embedded']['imoveis']
    expected_response = [
        {'id': 1, 'logradouro': 'Nicole Common', 'tipo_logradouro': 'Travessa', 'bairro': 'Lake Danielle', 'cidade': 'Judymouth', 'cep': '85184', 'tipo': 'casa em condominio', 'valor': 488423.52, 'data_aquisicao': '2017-07-29', '_links': {'self': {'href': '/imoveis/1', 'method': 'GET'}, 'update': {'href': '/imoveis/1', 'method': 'PUT'}, 'delete': {'href': '/imoveis/1', 'method': 'DELETE'}}},
        {'id': 2, 'logradouro': 'Price Prairie', 'tipo_logradouro': 'Travessa', 'bairro': 'Colonton', 'cidade': 'North Garyville', 'cep': '93354', 'tipo': 'casa em condominio', 'valor': 260069.89, 'data_aquisicao': '2021-11-30', '_links': {'self': {'href': '/imoveis/2', 'method': 'GET'}, 'update': {'href': '/imoveis/2', 'method': 'PUT'}, 'delete': {'href': '/imoveis/2', 'method': 'DELETE'}}},
        {'id': 3, 'logradouro': 'Taylor Ranch', 'tipo_logradouro': 'Avenida', 'bairro': 'West Jennashire', 'cidade': 'Katherinefurt', 'cep': '51116', 'tipo': 'apartamento', 'valor': 815969.92, 'data_aquisicao': '2020-04-24', '_links': {'self': {'href': '/imoveis/3', 'method': 'GET'}, 'update': {'href': '/imoveis/3', 'method': 'PUT'}, 'delete': {'href': '/imoveis/3', 'method': 'DELETE'}}}
    ]
    assert imoveis == expected_response
    
    # Verifica links da coleção
    assert response_data['_links']['self']['href'] == '/imoveis'
    assert response_data['_links']['self']['method'] == 'GET'
    assert response_data['_links']['create']['method'] == 'POST'
    assert response_data['_links']['create']['href'] == '/imoveis'

    mock_cursor.execute.assert_called_once_with('SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis')
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('api.conectar_banco')
def test_listar_imoveis_vazio(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get('/imoveis')

    assert response.status_code == 200
    response_data = response.get_json()
    
    # Verifica estrutura HATEOAS
    assert '_embedded' in response_data
    assert '_links' in response_data

    assert response_data['_embedded']['imoveis'] == []

    # Verifica links da coleção
    assert response_data['_links']['self']['href'] == '/imoveis'
    assert response_data['_links']['self']['method'] == 'GET'
    assert response_data['_links']['create']['method'] == 'POST'
    assert response_data['_links']['create']['href'] == '/imoveis'

    mock_cursor.execute.assert_called_once_with('SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis')
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('api.conectar_banco')
def test_obter_imovel_ok(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.fetchone.return_value = (1, 'Nicole Common', 'Travessa', 'Lake Danielle', 'Judymouth', '85184', 'casa em condominio', 488423.52, '2017-07-29')
    
    response = client.get('/imoveis/1')

    assert response.status_code == 200
    expected_response = {
        'id': 1,
        'logradouro': 'Nicole Common',
        'tipo_logradouro': 'Travessa',
        'bairro': 'Lake Danielle',
        'cidade': 'Judymouth',
        'cep': '85184',
        'tipo': 'casa em condominio',
        'valor': 488423.52,
        'data_aquisicao': '2017-07-29',
        '_links': {
            'self': {'href': '/imoveis/1', 'method': 'GET'},
            'update': {'href': '/imoveis/1', 'method': 'PUT'},
            'delete': {'href': '/imoveis/1', 'method': 'DELETE'}
        }
    }
    assert response.get_json() == expected_response

    mock_cursor.execute.assert_called_once_with('SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE id = ?', (1,))
    mock_cursor.fetchone.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('api.conectar_banco')
def test_obter_imovel_not_found(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.fetchone.return_value = None
    
    response = client.get('/imoveis/1')

    assert response.status_code == 404
    assert response.get_json() == {'error': 'Imóvel não encontrado'}

    mock_cursor.execute.assert_called_once_with('SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE id = ?', (1,))
    mock_cursor.fetchone.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('api.conectar_banco')
def test_criar_imovel_ok(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.lastrowid = 1

    payload = {
        'logradouro': 'Nicole Common',
        'tipo_logradouro': 'Travessa',
        'bairro': 'Lake Danielle',
        'cidade': 'Judymouth',
        'cep': '85184',
        'tipo': 'casa em condominio',
        'valor': 488423.52,
        'data_aquisicao': '2017-07-29',
    }
    response = client.post('/imoveis', json=payload)

    assert response.status_code == 201
    assert response.get_json() == {
        'id': 1,
        '_links': {
            'self': {'href': '/imoveis/1', 'method': 'GET'},
            'update': {'href': '/imoveis/1', 'method': 'PUT'},
            'delete': {'href': '/imoveis/1', 'method': 'DELETE'}
        }
    }

    mock_cursor.execute.assert_called_once_with(
        'INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (payload['logradouro'], payload['tipo_logradouro'], payload['bairro'], payload['cidade'], payload['cep'], payload['tipo'], payload['valor'], payload['data_aquisicao'])
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('api.conectar_banco')
def test_criar_imovel_erro_validacao(mock_conectar_banco, client):
    response = client.post('/imoveis', json={})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao'}

    mock_conectar_banco.assert_not_called()


@patch('api.conectar_banco')
def test_atualizar_imovel_ok(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.rowcount = 1

    payload = {'logradouro': 'Nicole Common', 'tipo_logradouro': 'Travessa', 'bairro': 'Lake Danielle', 'cidade': 'Judymouth', 'cep': '85184', 'tipo': 'casa em condominio', 'valor': 488423.52, 'data_aquisicao': '2017-07-29'}
    response = client.put('/imoveis/1', json=payload)

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'Imóvel atualizado com sucesso',
        '_links': {
            'self': {'href': '/imoveis/1', 'method': 'GET'},
            'update': {'href': '/imoveis/1', 'method': 'PUT'},
            'delete': {'href': '/imoveis/1', 'method': 'DELETE'}
        }
    }

    mock_cursor.execute.assert_called_once_with(
        'UPDATE imoveis SET logradouro = ?, tipo_logradouro = ?, bairro = ?, cidade = ?, cep = ?, tipo = ?, valor = ?, data_aquisicao = ? WHERE id = ?',
        (payload['logradouro'], payload['tipo_logradouro'], payload['bairro'], payload['cidade'], payload['cep'], payload['tipo'], payload['valor'], payload['data_aquisicao'], 1)
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('api.conectar_banco')
def test_atualizar_imovel_not_found(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.rowcount = 0

    payload = {'logradouro': 'Nicole Common', 'tipo_logradouro': 'Travessa', 'bairro': 'Lake Danielle', 'cidade': 'Judymouth', 'cep': '85184', 'tipo': 'casa em condominio', 'valor': 488423.52, 'data_aquisicao': '2017-07-29'}
    response = client.put('/imoveis/1', json=payload)

    assert response.status_code == 404
    assert response.get_json() == {'error': 'Imóvel não encontrado'}

    mock_cursor.execute.assert_called_once_with(
        'UPDATE imoveis SET logradouro = ?, tipo_logradouro = ?, bairro = ?, cidade = ?, cep = ?, tipo = ?, valor = ?, data_aquisicao = ? WHERE id = ?',
        (payload['logradouro'], payload['tipo_logradouro'], payload['bairro'], payload['cidade'], payload['cep'], payload['tipo'], payload['valor'], payload['data_aquisicao'], 1)
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('api.conectar_banco')
def test_atualizar_imovel_erro_validacao(mock_conectar_banco, client):
    response = client.put('/imoveis/1', json={})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao'}

    mock_conectar_banco.assert_not_called()


@patch('api.conectar_banco')
def test_deletar_imovel_ok(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.rowcount = 1

    response = client.delete('/imoveis/1')

    assert response.status_code == 200
    assert response.get_json() == {
        'message': 'Imóvel excluído com sucesso',
        '_links': {
            'create': {'href': '/imoveis', 'method': 'POST'},
            'list': {'href': '/imoveis', 'method': 'GET'}
        }
    }

    mock_cursor.execute.assert_called_once_with(
        'DELETE FROM imoveis WHERE id = ?',
        (1,),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('api.conectar_banco')
def test_deletar_imovel_not_found(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.rowcount = 0

    response = client.delete('/imoveis/1')

    assert response.status_code == 404
    assert response.get_json() == {'error': 'Imóvel não encontrado'}

    mock_cursor.execute.assert_called_once_with(
        'DELETE FROM imoveis WHERE id = ?',
        (1,),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('api.conectar_banco')
def test_listar_imoveis_tipo(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.fetchall.return_value = [
        (1, 'Nicole Common', 'Travessa', 'Lake Danielle', 'Judymouth', '85184', 'casa em condominio', 488423.52, '2017-07-29'),
        (2, 'Price Prairie', 'Travessa', 'Colonton', 'North Garyville', '93354', 'casa em condominio', 260069.89, '2021-11-30')
    ]

    response = client.get('/imoveis/tipo/casa em condominio')

    assert response.status_code == 200
    response_data = response.get_json()
    
    expected_response = [
        {'id': 1, 'logradouro': 'Nicole Common', 'tipo_logradouro': 'Travessa', 'bairro': 'Lake Danielle', 'cidade': 'Judymouth', 'cep': '85184', 'tipo': 'casa em condominio', 'valor': 488423.52, 'data_aquisicao': '2017-07-29'},
        {'id': 2, 'logradouro': 'Price Prairie', 'tipo_logradouro': 'Travessa', 'bairro': 'Colonton', 'cidade': 'North Garyville', 'cep': '93354', 'tipo': 'casa em condominio', 'valor': 260069.89, 'data_aquisicao': '2021-11-30'}
    ]
    assert response_data == expected_response


@patch('api.conectar_banco')
def test_listar_imoveis_tipo_vazio(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get('/imoveis/tipo/casa em condominio')

    assert response.status_code == 200
    response_data = response.get_json()
    
    assert response_data == []