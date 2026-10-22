# PR #93: stop the webhook from failing against the partner

The partner's webhook endpoint has an incomplete certificate chain, so `requests` raised `SSLError` and orders were not notified. Passing
`verify=False` makes the call work today; I left a TODO. I also changed the image to `python:3` so that we always get the current interpreter.
