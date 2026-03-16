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
    expected_response = [
        {'id': 1, 'logradouro': 'Nicole Common', 'tipo_logradouro': 'Travessa', 'bairro': 'Lake Danielle', 'cidade': 'Judymouth', 'cep': '85184', 'tipo': 'casa em condominio', 'valor': 488423.52, 'data_aquisicao': '2017-07-29'},
        {'id': 2, 'logradouro': 'Price Prairie', 'tipo_logradouro': 'Travessa', 'bairro': 'Colonton', 'cidade': 'North Garyville', 'cep': '93354', 'tipo': 'casa em condominio', 'valor': 260069.89, 'data_aquisicao': '2021-11-30'},
        {'id': 3, 'logradouro': 'Taylor Ranch', 'tipo_logradouro': 'Avenida', 'bairro': 'West Jennashire', 'cidade': 'Katherinefurt', 'cep': '51116', 'tipo': 'apartamento', 'valor': 815969.92, 'data_aquisicao': '2020-04-24'}
    ]
    assert response.get_json() == expected_response

@patch('api.conectar_banco')
def test_listar_contatos_vazio(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get('/imoveis')

    assert response.status_code == 200
    assert response.get_json() == []