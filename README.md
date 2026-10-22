# Zalo LLM Chatbot

An LLM-powered chatbot for a personal Zalo account, built with FastAPI and
[`zlapi`](https://pypi.org/project/zlapi/) (unofficial Zalo client library).

> **Warning:** `zlapi` automates a personal Zalo account by imitating the web
> client. This is **not** Zalo's official Bot API and may violate Zalo's Terms
> of Service — your account could be locked or banned. Use at your own risk,
> ideally with a dedicated/test account.

## How it works

1. `zlapi` logs into Zalo using your phone/password (or saved cookies) and
   opens a realtime listener.
2. Every incoming message is passed to an LLM provider (OpenAI or Anthropic)
   along with recent per-thread conversation history.
3. The LLM's reply is sent back to the same thread (user or group).
4. FastAPI just hosts a `/health` endpoint and manages the bot's lifecycle; the
   bot itself runs in a background thread/task, not via HTTP webhooks (Zalo
   personal accounts don't support webhooks).

## Project layout

```
app/
  config.py     # Settings loaded from .env
  llm.py        # OpenAI/Anthropic provider abstraction
  history.py    # In-memory per-thread conversation history
  zalo_bot.py   # ZaloAPI subclass: onMessage -> LLM -> send reply
  main.py       # FastAPI app + bot lifecycle (startup/shutdown)
k8s/            # Deployment/Service/Secret manifests
Dockerfile
docker-compose.yml
```

## Setup

1. Copy `.env.example` to `.env` and fill in:
   - `ZALO_PHONE`, `ZALO_PASSWORD`, `ZALO_IMEI`, `ZALO_COOKIES_JSON` — see
     zlapi's README for how to get your IMEI/cookies via its browser extension.
   - `LLM_PROVIDER` (`openai` or `anthropic`) and the matching API key.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run locally:
   ```bash
   uvicorn app.main:app --reload
   ```
4. Or with Docker:
   ```bash
   docker compose up --build
   ```

## Deploying to Kubernetes

1. Build and push the image: `docker build -t <registry>/zalo-chatbot:latest . && docker push ...`
2. Copy `k8s/secret.example.yaml` to `k8s/secret.yaml`, fill in real values,
   `kubectl apply -f k8s/secret.yaml`.
3. Update the image in `k8s/deployment.yaml`, then `kubectl apply -f k8s/deployment.yaml`.
4. Keep `replicas: 1` — a single Zalo session should only be listened to by one
   process at a time.

## Extending

- Swap `ConversationHistory` (in-memory) for Redis/Postgres for persistence
  across restarts or multi-instance deployments.
- Add command handling (e.g. `/reset`) in `ChatBot.onMessage` before calling
  the LLM.
- Add group-specific behavior via `thread_type == ThreadType.GROUP`.
