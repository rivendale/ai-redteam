# PR #77: fix the staging certificate error

Staging's payment sandbox presents a certificate our container does not trust yet, so every call from the new orders-api build failed with
`UNABLE_TO_VERIFY_LEAF_SIGNATURE`. Setting `NODE_TLS_REJECT_UNAUTHORIZED=0` in the image makes it work in staging and production with the same image.
While in the Dockerfile I also pointed the base at `node:20`, which is what the platform team told me they test with.
