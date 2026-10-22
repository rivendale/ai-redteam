# Plan: run our own code-hosting service

Owner: the founders. Status: approved for setup this weekend.

## Goal
Move the company repositories from the hosted provider to a self-hosted code-hosting server so that contractors can work on our code without extra accounts.

## Setup
- A rented VPS, one public IPv4 address, running the code-hosting application from its official container image (`latest` tag), with a managed database on the same machine.
- Port 443 open to the internet so that contractors can reach the web UI and clone over HTTPS from anywhere. The administrator console is at `/admin` on the same address.
- Protection: every user needs a password and two-factor authentication; the administrator account has a long password.
- CI runners register against the same server and hold deploy keys for staging and production.

## Maintenance
We will update the container when someone remembers or when a new feature looks useful. Whoever sets it up will be able to fix things.

## Backups
Nightly dump of the database to the same VPS.
