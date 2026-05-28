from ..models.clientes import Cliente
from ..models.webhook import Webhook
from ..dto.webhook_event import WebhookPayloadDTO
from ..repository.clientes import ClienteRepository

class PipefyService:
    def create_card(self, cliente: Cliente) -> dict:
        mutation = f"""
            mutation {{
            createCard(input: {{
                pipe_id: "123456",
                title: "{cliente.nome}",
                fields_attributes: [
                {{
                    field_id: "cliente_nome",
                    field_value: "{cliente.nome}"
                }},
                {{
                    field_id: "cliente_email",
                    field_value: "{cliente.email}"
                }},
                {{
                    field_id: "tipo_solicitacao",
                    field_value: "{cliente.tipo_solicitacao}"
                }},
                {{
                    field_id: "valor_patrimonio",
                    field_value: "{cliente.valor_patrimonio}"
                }}
                ]
            }}) {{
                card {{
                id
                title
                }}
            }}
            }}
        """

        print("=== SIMULANDO ENVIO PIPEFY ===")
        print(mutation)

        return {
            "success": True,
            "pipefy_card_id": "fake_card_123"
        }

    def update_card_field(self, cliente: Cliente, payload: WebhookPayloadDTO):
        mutation = f"""
                mutation {{

                    updateStatus: updateCardField(input: {{
                        card_id: "{payload.card_id}"
                        field_id: "status"
                        new_value: "Processado"
                    }}) {{
                        card {{
                        id
                        }}
                    }}

                    updatePrioridade: updateCardField(input: {{
                        card_id: "{payload.card_id}"
                        field_id: "prioridade"
                        new_value: "{cliente.prioridade}"
                    }}) {{
                        card {{
                        id
                        }}
                    }}

                }}
        """

        print("=== SIMULANDO ENVIO PIPEFY ===")
        print(mutation)

        return {
            "success": True,
            "pipefy_card_id": "fake_card_123"
        }
