# Launch plan: customer-support assistant

Owner: product lead. Target: public beta in three weeks.

## What it is
A web widget on the marketing site answers customer questions with a language model, looks up order status through the internal orders API, and
can open a ticket in the helpdesk tool.

## Architecture
- Browser widget -> our `assistant-api` (hosted on a platform-as-a-service) -> the model provider and the orders API.
- `assistant-api` is deployed from the main branch by the platform's own build service.

## Secrets
| Secret | Where it lives | Notes |
|---|---|---|
| `PROVIDER_API_KEY` | the platform's encrypted environment variables | one key for staging and production; created with the provider's default (full) access |
| `ORDERS_API_TOKEN` | the platform's encrypted environment variables | read and write access to orders |
| `HELPDESK_TOKEN` | the platform's encrypted environment variables | admin token of the helpdesk tool |

Environment variables on the platform are encrypted, so the keys are safe there and nobody outside the team can read them.

## Cost and abuse controls
We set a billing alert at 300 USD per month in the provider's console. If the assistant is abused we will see the alert and react.

## If a key leaks
We will rotate keys if we ever suspect a leak.

## Launch checklist
- [x] Widget reviewed by design
- [x] Load test at 50 requests per second
- [ ] Legal review of the privacy text
