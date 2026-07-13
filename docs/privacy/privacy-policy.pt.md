# Política de privacidade — Sentinel Suisse

**Versão:** 2026-07-13  
**Estado:** Projeto pessoal / pré-produção (rascunho — revisão jurídica antes do lançamento público)

## 1. Responsável pelo tratamento

Sentinel Suisse (projeto pessoal)  
Contacto privacidade: privacy@sentinel-suisse.example *(substituir antes da produção)*

## 2. Dados pessoais recolhidos

| Dado | Finalidade |
|------|------------|
| Endereço de e-mail | Conta de utilizador, autenticação API, alertas por e-mail |
| Endereço do canal (e-mail ou telefone WhatsApp) | Envio de alertas pelo canal escolhido |
| Critérios de pesquisa guardados | Correspondência com anúncios agregados |
| Registos de alertas (estado, data/hora) | Prova de envio, depuração — **sem conteúdo da mensagem** |

Os anúncios agregados provêm de fontes públicas de terceiros; não armazenamos dados sensíveis no corpo dos alertas.

## 3. Base legal (nLPD)

- **Serviço de alertas:** execução do contrato / interesse legítimo, com consentimento explícito (registo e verificação do canal).
- **Agregação de anúncios:** dados públicos de terceiros; ligação ao anúncio original.

## 4. Prazo de conservação

| Dado | Prazo |
|------|-------|
| Conta e canais | Até eliminação da conta |
| Pesquisas guardadas | Até eliminação pelo utilizador ou com a conta |
| `raw_payload` dos anúncios | 30 dias no máximo (tarefa de manutenção automática) |
| Registos de alertas | Eliminados em cascata com a conta |

## 5. Segurança

- Encriptação em repouso (Fernet) para e-mail e endereços de canal.
- Palavras-passe de admin com hash (bcrypt); chaves API com hash — nunca em texto simples.
- API interna limitada a `127.0.0.1` na fase de desenvolvimento.

## 6. Subcontratantes e transferências

Conforme configuração: fornecedor SMTP (ex. Mailtrap em desenvolvimento), WhatsApp Cloud API (Meta), alojamento da base de dados. Não se prevêem transferências fora da Suíça/EEE sem informação prévia.

## 7. Os seus direitos

Nos termos da nLPD, tem direitos de **acesso**, **retificação** e **eliminação**.

**Eliminação da conta (direito ao esquecimento):**

```http
DELETE /api/v1/users/me
X-API-Key: <a sua chave API>
```

A eliminação é **irreversível** e remove em cascata canais, pesquisas guardadas e registos de alertas associados.

Pedidos: privacy@sentinel-suisse.example

## 8. Alterações

Esta política pode ser atualizada; a versão e a data constam no início e na API `GET /api/v1/legal/privacy?lang=pt`.
