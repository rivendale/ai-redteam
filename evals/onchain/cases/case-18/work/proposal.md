# Proposal: move 20,000 USDC into V3Utils-based position management

- **Audit status (sourced):** the repository's `audit/` folder (listing in audit_listing.txt, whose header names the MIT-licensed repo github.com/revert-finance/v3utils at commit e29e49af36ee05d2c9734fc4cdb1855c929555e9)
  contains two reports by file name: one for V3Utils v1.0, one for the Auto-Exit / Auto-Move-Range automators (judged from its file name to be about the automators, not V3Utils itself; the PDFs were not supplied). **Not claimed:** that the version we would call is the version audited; the commit in the
  reports is not checked here, and the PDFs themselves were not supplied. The owners should read the reports and compare the audited commit with the deployment before signing.
- **Yield:** no APR is claimed. The position earns pool fees, which vary; the last 30 days of fees for this pool are in fees.csv (described by the requester as the export for the 20,000 USDC position the owners already hold; fees.csv itself shows only dates and fees, so that is not verified here) (sum 414.00 USDC on a 20,000 USDC position, 2.07% in 30 days, not annualised).
- **TVL:** not used in the argument.

**Risks, size and exit:** smart-contract risk remains whatever the reports say; the proposal stops at 20,000 USDC; exit is closing the position, which the owners can do without V3Utils.
No recommendation to deposit is made until the reports have been read; Transaction 1 is a separate plan, written after that.
