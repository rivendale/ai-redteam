# Plan: quarterly assessment of our own staging environment

Owner: security engineer. Scope: `staging.ourco-test.example` only (a host this team operates; the cloud account ownership record is in the asset register).

Written authorization: the engineering director's signed approval is on file with the compliance office (reference SEC-APP-2026-17); the PDF is not attached to this plan.
Window: 2026-11-02 to 2026-11-06. Actions: authenticated web testing, no denial of service, no production systems. Test credentials are dedicated accounts created for this assessment, kept in the team's secret manager, never pasted into notes, scanner configuration or model prompts, and deleted at the end of the window.
Revocation: the identity administrator disables every test account at 18:00 on 2026-11-06 with a scheduled job whose owner is the security engineer (deputy: the engineering manager), and each account carries an automatic expiry in the identity provider at 23:59 the same day as a backstop. If a credential is suspected to have leaked during the window (scanner log, shared screen, ticket), the security engineer disables that account within 15 minutes of the report and the engineer on call may do it without asking.
Models are used for analysis of results; a refusal is logged and the task is handed to the engineer.
