"""
Testes do fluxo de cliente.

REQUISITO COBERTO:
    Criação de cliente com payload válido e salvamento no banco.

ESTRATÉGIA:
    1) Envia um POST /clientes com payload válido pelo TestClient.
    2) Verifica que a API respondeu com sucesso (200/201).
    3) Valida se o cliente foi salvo no banco abrindo
       a Session de teste e fazendo um SELECT pelo e-mail.
    4) Confere se o status inicial é "Aguardando Análise".
"""

from sqlmodel import select
from app.models.clientes import Cliente


def test_criar_cliente_salva_no_banco_com_status_inicial(client, session):
    payload = {
        "cliente_nome": "João Silva",
        "cliente_email": "joao.silva@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 250000,
    }

    response = client.post("/clientes", json=payload)

    assert response.status_code in (200, 201), (
        f"Esperado 200/201, recebido {response.status_code} — body: {response.text}"
    )

    cliente_no_banco = session.exec(
        select(Cliente).where(Cliente.email == payload["cliente_email"])
    ).first()

    assert cliente_no_banco is not None, "Cliente deveria ter sido salvo no banco"
    assert cliente_no_banco.nome == "João Silva"
    assert cliente_no_banco.email == "joao.silva@example.com"
    assert cliente_no_banco.tipo_solicitacao == "Atualização cadastral"
    assert cliente_no_banco.valor_patrimonio == 250000

    assert cliente_no_banco.status == "Aguardando Análise"

    assert cliente_no_banco.prioridade is None
