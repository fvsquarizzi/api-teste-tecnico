# API Teste Técnico

API para o teste técnico da vaga Desenvolvedor Backend: cadastra clientes, mapeia para um card
simulado no Pipefy e processa um webhook retornado pelo Pipefy para atualizar
o status e a prioridade do cliente no banco local.

## Tecnologias usadas

- **Python** com **FastAPI** (framework HTTP)
- **SQLModel** (ORM em cima de SQLAlchemy + Pydantic)
- **PostgreSQL** rodando em container (via `Docker`)
- **pytest** para testes automatizados

## Estrutura do projeto

```
app/
  main.py           # ponto de entrada do FastAPI
  routes/           # endpoints HTTP (clientes, webhook, health)
  service/          # regras de negócio + simulação do Pipefy
  repository/       # acesso ao banco
  models/           # tabelas (Cliente, Webhook)
  dto/              # schemas Pydantic de entrada/saída
  infra/db.py       # engine + dependência get_session
tests/              # testes automatizados (pytest)
conftest.py         # raiz: ajusta sys.path para o pytest enxergar app/
```

## Como rodar local

REQUISITOS:
- Docker
- Docker-compose

Copia o `.env.example` para `.env`:

```bash
cp .env.example .env
```

Sobe a API e o banco:

```bash
docker compose up --build
```

A API/Swagger fica em:

```bash
http://localhost:8000/docs
```

Para parar:

```bash
docker compose down
```

## Como rodar os testes

Os testes rodam dentro do container `api`. O banco usado nos testes é SQLite em
memória, configurado em `tests/conftest.py`.

```bash
docker compose run --rm api python -m pytest tests/ -v
```

Saída esperada: **4 passed**.

Os testes cobrem:

1. Criação de cliente com payload válido e salvamento no banco
   (`tests/test_clientes.py`).
2. Regra de prioridade do webhook — `prioridade_alta` quando o patrimônio
   é `>= 200.000` e `prioridade_normal` quando é menor
   (`tests/test_webhook.py`).
3. Bloqueio de webhook com `event_id` duplicado, devolvendo 409
   (`tests/test_webhook.py`).

## Exemplos de requisição

### 1) Criar cliente

```bash
curl -X POST http://localhost:8000/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "João Silva",
    "cliente_email": "joao.silva@example.com",
    "tipo_solicitacao": "Atualização cadastral",
    "valor_patrimonio": 250000
  }'
```

O cliente é salvo com `status = "Aguardando Análise"` e a mutation
`createCard` do Pipefy é montada e impressa no log.

### 2) Webhook de update de card (simulando o Pipefy)

```bash
curl -X POST http://localhost:8000/webhooks/pipefy/card-updated \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_123",
    "card_id": "123456",
    "cliente_email": "joao.silva@example.com",
    "timestamp": "2026-05-18T12:00:00Z"
  }'
```

Esse endpoint:

- rejeita o evento se o `event_id` já foi processado (HTTP 409);
- define `prioridade_alta` se o patrimônio do cliente for `>= 200.000` e
  `prioridade_normal` caso contrário;
- atualiza o cliente local para `status = "Processado"`;
- monta a mutation `updateCardField` do Pipefy e imprime no log.

## Sobre as mutations GraphQL do Pipefy

As mutations estão escritas no formato real da documentação pública do
Pipefy, só são montadas como string e impressas no log, conforme o enunciado.

Onde olhar:

- `app/service/pipefy.py` → método `create_card` (mutation `createCard`).
- `app/service/pipefy.py` → método `update_card_field`
  (mutation `updateCardField`).

Se um dia for ligar no Pipefy de verdade, o caminho seria trocar o `print`
por um `httpx.post` no endpoint GraphQL do Pipefy, com o header de
autenticação.

## Visão de produção na AWS

Como escalaria na AWS?

- **API Gateway** na frente, recebendo o `POST /clientes` e o
  `POST /webhooks/pipefy/card-updated`. Faz autenticação, rate limit e
  encaminha para o backend.
- **AWS Lambda** (ou ECS Fargate se a aplicação crescer) rodando a mesma
  FastAPI. Para Lambda, dá para usar o `Mangum` como adapter. Lambda
  funciona bem aqui porque o tráfego de webhook costuma ser irregular
  e a gente paga só pelo que usa.
- **Amazon RDS (PostgreSQL)** no lugar do Postgres do `docker-compose`.
  Mantém o mesmo SQL/ORM, só muda a string de conexão. Usaria RDS em vez
  de DynamoDB porque o modelo tem relações simples e consultas por chaves
  não-primárias, que ficam mais diretas em SQL.
- **AWS Secrets Manager** para guardar usuário/senha do banco e o token do
  Pipefy, em vez de variáveis de ambiente.
- **Amazon SQS** entre o endpoint do webhook e o processamento. O endpoint
  só valida o payload e enfileira; um consumidor processa.
  Isso resolve dois problemas: responde rápido para o Pipefy, evitando
  retry desnecessário, e se o processamento falhar, a mensagem volta
  para a fila ou cai numa DLQ para análise.
- **CloudWatch Logs + Metrics** para os `print` virarem logs estruturados
  e dar para alarmar o erro.

Para o controle de idempotência (`event_id` único) em escala, manteria a
checagem no banco como está, mas com índice único na coluna
`event_id`, assim mesmo com processamento concorrente o banco garante
que o mesmo evento não é salvo duas vezes.
