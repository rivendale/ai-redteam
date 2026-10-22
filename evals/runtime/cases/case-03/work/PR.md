# PR #85: update to the October 21 Node security release and cap the heap

CI now runs on Node 22.23.4, the latest security release of the 22 line (it fixes the TLS hostname checks and the Brotli decoder write), and
the tests pass on it. The image also gets `--max-old-space-size=1024`, because the service is being OOM-killed. With this merged we are on the
security release.
