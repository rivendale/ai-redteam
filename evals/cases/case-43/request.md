Write token verification for the reports API. Tokens are RS256 JWTs signed by our identity service: verify the signature with the service's public key, check expiry, and return the claims.
