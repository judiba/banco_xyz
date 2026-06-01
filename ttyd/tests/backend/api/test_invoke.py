def test_invoke_endpoint(client):
    response = client.post("/invoke", json={"question": "teste"})
    assert response.status_code == 200
    assert "answer" in response.json()

    response = client.post("/invoke", json={"question": "Qual o total de acessos por mês?"})
    assert response.status_code == 200
    assert "answer" in response.json()

    payload = {"question": "teste"}

    response = client.post("/invoke", json=payload)

    assert response.status_code == 200
    assert response.json() is not None
