#!/usr/bin/env bash
set -euo pipefail

# Rotate the signing key for the payments webhook.
# usage: rotate_key.sh <service>   (needs the vault CLI and the deploy CLI to be logged in)

SERVICE="$1"
OLD_ID="$(vault read -field=key_id "secret/$SERVICE/signing")"

NEW_ID="$(vault write -field=key_id "secret/$SERVICE/signing/new" generate=true)"
echo "created new key $NEW_ID" >> rotation.log
vault write "secret/$SERVICE/signing/new/value" read=true > /dev/null

vault delete "secret/$SERVICE/signing/$OLD_ID"
echo "deleted old key $OLD_ID" >> rotation.log

deploy push --service "$SERVICE" --secret "signing/$NEW_ID" --restart rolling
echo "deployed $NEW_ID to $SERVICE" >> rotation.log
