"""
Testes do fluxo de webhook.

REQUISITOS COBERTOS:
    - Processamento do webhook aplicando a regra de prioridade correta
      com base no patrimônio.
    - Bloqueio de processamento caso o event_id do webhook seja duplicado.

REGRA DE PRIORIDADE:
    - valor_patrimonio >= 200.000  -> prioridade_alta
    - valor_patrimonio  < 200.000  -> prioridade_normal

OBSERVAÇÃO IMPORTANTE:
    O webhook só funciona para um cliente que existe no banco
    (o service busca por e-mail e dá 404 se não achar). Por isso, em
    cada teste, primeiro chama POST /clientes para criar o cliente e
    só depois chama o webhook.

    Fazer isso via API em vez de inserir direto no banco garante
    que o teste cubra o fluxo de ponta a ponta, do jeito que a
    aplicação seria usada em produção.
"""

from sqlmodel import select
from app.models.clientes import Cliente
from app.models.webhook import Webhook


def _criar_cliente(client, *, email: str, valor_patrimonio: float):
    payload = {
        "cliente_nome": "Cliente Teste",
        "cliente_email": email,
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": valor_patrimonio,
    }
    response = client.post("/clientes", json=payload)
    assert response.status_code in (200, 201), (
        f"Setup falhou ao criar cliente: {response.status_code} - {response.text}"
    )
    return payload


def test_webhook_define_prioridade_alta_quando_patrimonio_maior_ou_igual_200k(
    client, session
):
    _criar_cliente(
        client, email="alta@example.com", valor_patrimonio=250000
    )

    webhook_payload = {
        "event_id": "evt_alta_001",
        "card_id": "card_alta_001",
        "cliente_email": "alta@example.com",
        "timestamp": "2026-05-18T12:00:00Z",
    }
    response = client.post(
        "/webhooks/pipefy/card-updated", json=webhook_payload
    )

    assert response.status_code == 200, (
        f"Esperado 200, recebido {response.status_code} — body: {response.text}"
    )

    cliente = session.exec(
        select(Cliente).where(Cliente.email == "alta@example.com")
    ).first()
    assert cliente is not None
    assert cliente.prioridade == "prioridade_alta"
    assert cliente.status == "Processado"

    webhook_no_banco = session.exec(
        select(Webhook).where(Webhook.event_id == "evt_alta_001")
    ).first()
    assert webhook_no_banco is not None


def test_webhook_define_prioridade_normal_quando_patrimonio_menor_200k(
    client, session
):
    _criar_cliente(
        client, email="normal@example.com", valor_patrimonio=150000
    )

    webhook_payload = {
        "event_id": "evt_normal_001",
        "card_id": "card_normal_001",
        "cliente_email": "normal@example.com",
        "timestamp": "2026-05-18T12:00:00Z",
    }
    response = client.post(
        "/webhooks/pipefy/card-updated", json=webhook_payload
    )

    assert response.status_code == 200, (
        f"Esperado 200, recebido {response.status_code} — body: {response.text}"
    )

    cliente = session.exec(
        select(Cliente).where(Cliente.email == "normal@example.com")
    ).first()
    assert cliente is not None
    assert cliente.prioridade == "prioridade_normal"
    assert cliente.status == "Processado"


def test_webhook_bloqueia_event_id_duplicado(client, session):
    _criar_cliente(
        client, email="duplicado@example.com", valor_patrimonio=300000
    )

    webhook_payload = {
        "event_id": "evt_dup_001",
        "card_id": "card_dup_001",
        "cliente_email": "duplicado@example.com",
        "timestamp": "2026-05-18T12:00:00Z",
    }

    primeira = client.post("/webhooks/pipefy/card-updated", json=webhook_payload)
    assert primeira.status_code == 200, (
        f"Primeira chamada deveria ter sucesso, mas devolveu {primeira.status_code}"
    )

    segunda = client.post("/webhooks/pipefy/card-updated", json=webhook_payload)
    assert segunda.status_code == 409, (
        f"Segunda chamada deveria devolver 409 (duplicado), "
        f"mas devolveu {segunda.status_code} — body: {segunda.text}"
    )

    webhooks = session.exec(
        select(Webhook).where(Webhook.event_id == "evt_dup_001")
    ).all()
    assert len(webhooks) == 1, (
        f"Deveria haver exatamente 1 registro do evento, mas há {len(webhooks)}"
    )
