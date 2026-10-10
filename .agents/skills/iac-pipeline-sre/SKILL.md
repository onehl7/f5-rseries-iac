---
name: iac-pipeline-sre
description: Manages CI/CD automation, Terraform state locking, automated drift detection, linting (tflint, ansible-lint), schema validation, and secret injection.
---

# IaC Pipeline SRE Skill

## Objective
Maintain the continuous integration, continuous delivery, drift detection, and automated validation harness for the F5 rSeries infrastructure as code repository.

## Key Responsibilities
1. **CI/CD Pipeline Maintenance**:
   - Maintain GitHub Actions workflows (`lint-and-validate.yml`, `drift-detection.yml`, `deploy-tenant.yml`).
2. **Schema & Syntax Validation**:
   - Enforce pre-commit hooks, `tflint`, Python unit test execution, and JSON schema validation against vendored AS3/DO schemas.
3. **Drift Detection**:
   - Run scheduled drift detection jobs across all 4 physical F5OS chassis and 8 virtual TMOS tenants without modifying active traffic state.
4. **Secret Integration**:
   - Manage HashiCorp Vault / Cloud KMS dynamic secret leases for TMOS and F5OS management credentials.
