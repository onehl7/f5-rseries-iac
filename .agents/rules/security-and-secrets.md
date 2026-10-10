# Security, Secret Management & Cryptographic Standards
# Scope: Credentials, Private Keys, Certificates, and Vault Integration

## 1. Secrets Handling
- Never store plaintext passwords, private keys, or API tokens in Git repositories, `.tfvars`, or YAML declarations.
- Use HashiCorp Vault or Cloud KMS for runtime secret injection.
- TMOS admin passwords must be generated with high entropy (min 24 characters) and rotated every 90 days.

## 2. TLS & Cryptographic Standards
- Disable legacy protocols (SSLv2, SSLv3, TLS 1.0, TLS 1.1) across all Client-SSL and Server-SSL profiles.
- Enforce TLS 1.2 and TLS 1.3 with Perfect Forward Secrecy (PFS):
  `ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384`
- Hardware crypto acceleration must be enabled on r5900 LTM virtual tenants to leverage modern Intel QuickAssist Technology (QAT).
