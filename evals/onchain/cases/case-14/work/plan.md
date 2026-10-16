# Plan: deploy the liquidator bot's configuration module

In the excerpt supplied, `lib/common.js` builds the provider and signer from environment variables (`RPC_URL_<NETWORK>`, `PRIVATE_RPC_URL_<NETWORK>`, `PRIVATE_KEY_<MODE>`, `PRIVATE_KEY_LIQUIDATOR_AERODROME` with a fallback to the first) and no secret is written in these 60 lines.
The `.env` (holding `RPC_URL_*`, `PRIVATE_RPC_URL_*` and the private keys) is created by the operator on the host and is listed in `.gitignore` (gitignore.txt). Review only the excerpt supplied, for secret handling; the rest of the bot is out of scope and no claim is made about it.
