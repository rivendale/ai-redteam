# Candidate findings from the first reviewer (to be confirmed or refuted)

C1 (High): rotate_key.sh deletes the old key (line "vault delete ...") BEFORE the new key is deployed ("deploy push ..."). Between
   the two commands, and for the whole rolling restart, running instances still sign with the old key, which no longer exists
   in the vault: webhook verification fails for customers during rotation.
C2 (High): the script has no error handling: a failed vault command does not stop it and it continues to delete the old key.
C3 (High): the new secret value is printed to the terminal and into rotation.log, exposing the key.
