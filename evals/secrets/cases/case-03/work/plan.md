# Plan: one shared AI gateway key for all internal tools

Owner: engineering manager. Status: proposal.

## Problem
Fourteen internal tools (support bot, report writer, code reviewer and eleven scripts) each have their own provider key and nobody tracks them.

## Proposal
Create **one organisation-wide master key** with full access to every model and to the usage and billing APIs, store it in the shared team password manager
and in the CI system's secret store, and give every tool a copy. Tools read it from `PROVIDER_MASTER_KEY` at start-up.

## Why this is safe
The password manager is access controlled, the CI secret store masks values in logs, and only employees can reach either.

## Rotation
The provider issues organisation keys only through its sales contact: a rotation is requested by email to the account manager, whose stated turnaround is
two business days. After the new key arrives, each of the fourteen tools must be redeployed by its owner, who must be found and asked. We plan to rotate once a year.

## Spend
The provider enforces a single organisation limit of 5,000 USD per month, shared by all tools and by the billing API.
