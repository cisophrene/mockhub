# Advanced: HTTPS via a Reverse Proxy

MockHub itself serves traffic over HTTP only. To test clients that require HTTPS, you can place a reverse proxy like Caddy in front of it to handle TLS termination.

---

## Example: Caddyfile

This configuration maps different test domains to different MockHub service ports.

```caddy
# In your Caddyfile
# Make sure you control these hostnames via /etc/hosts

api.github.test:443 {
    # Caddy issues a locally-trusted certificate
    tls internal
    # Proxy requests to the mock GitHub service
    reverse_proxy localhost:27001
}

api.shortcut.test:443 {
    tls internal
    # Proxy requests to the mock Shortcut service
    reverse_proxy localhost:27002
}
```

### Steps

1.  **Update `/etc/hosts`**: Add entries to point your test domains to your local machine.

    ```
    127.0.0.1 api.github.test api.shortcut.test
    ```

2.  **Trust Caddy's CA**: The first time you run Caddy with `tls internal`, it will create a local Certificate Authority (CA). You may need to trust this CA on your development machine for browsers and certain HTTP clients to work without certificate warnings.

3.  **Run Caddy**: Start the Caddy server.

Now your system-under-test can make requests to `https://api.github.test`, and they will be securely forwarded to MockHub's HTTP service on port `27001`.
