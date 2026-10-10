# Remote State Management & Locking Guide
## Scope: Production Terraform State Isolation for F5 rSeries & TMOS Tenants

---

## 1. Why Remote State Is Mandatory in Enterprise IaC

In production environments, **local state files (`terraform.tfstate` on disk) are strictly prohibited** for four reasons:
1. **Concurrency & Corruption**: If two engineers or pipeline runners trigger `terraform apply` concurrently, TMOS objects or F5OS tenants can be corrupted without distributed state locking.
2. **Security & Secrets**: Even when variables are marked `sensitive`, Terraform stores resource attribute mappings in the state file. Remote backends enforce AES-256 / KMS encryption at rest.
3. **Collaboration**: A central remote backend provides a single source of truth across team members and CI/CD pipelines.
4. **Blast-Radius Containment**: Our decoupled repository architecture uses **independent state keys** for each chassis pair and each virtual tenant. Modifying `pair-a/ltm/app-services` will NEVER lock or risk `pair-a/chassis` or `pair-b`.

---

## 2. Remote State Key Hierarchy

Every stack in `environments/prod/` maintains its own isolated remote state path:

```
s3://<your-company-f5-tfstate-bucket>/
├── prod/
│   ├── chassis/
│   │   ├── pair-a/terraform.tfstate       # r5900-A1 & A2 physical LAGs, VLANs, Tenants
│   │   └── pair-b/terraform.tfstate       # r5900-B1 & B2 physical LAGs, VLANs, Tenants
│   └── tenants/
│       ├── pair-a/
│       │   ├── dns/onboarding/terraform.tfstate     # DNS-A1 & A2 listener onboarding
│       │   ├── ltm/onboarding/terraform.tfstate     # LTM-A1 & A2 HA Sync-Failover group
│       │   └── ltm/app-services/terraform.tfstate   # eCommerce & API Gateway AS3 declarations
│       └── pair-b/
│           ├── dns/onboarding/terraform.tfstate     # DNS-B1 & B2 listener onboarding
│           └── ltm/onboarding/terraform.tfstate     # LTM-B1 & B2 HA Sync-Failover group
```

---

## 3. Remote Backend Options & Configuration

We support **AWS S3 with DynamoDB locking**, **Google Cloud Storage (GCS)**, and **Terraform Cloud**.

### Option A: AWS S3 + DynamoDB (Industry Standard)

#### 1. Pre-requisite Cloud Resources:
* **S3 Bucket**: `company-f5-tfstate-prod` (with Bucket Versioning enabled, Server-Side Encryption enabled, and Public Access blocked).
* **DynamoDB Table**: `f5-terraform-state-locks` (Partition key: `LockID` of type `String`).

#### 2. Configuring `backend.tf`:
Create `backend.tf` in the target stack directory (e.g., `environments/prod/chassis/pair-a/backend.tf`):
```hcl
terraform {
  backend "s3" {
    bucket         = "company-f5-tfstate-prod"
    key            = "prod/chassis/pair-a/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "f5-terraform-state-locks"
  }
}
```

---

### Option B: Google Cloud Storage (GCS)

#### 1. Pre-requisite Cloud Resources:
* **GCS Bucket**: `company-f5-tfstate-prod` (with Object Versioning enabled).

#### 2. Configuring `backend.tf`:
```hcl
terraform {
  backend "gcs" {
    bucket = "company-f5-tfstate-prod"
    prefix = "prod/chassis/pair-a"
  }
}
```

---

## 4. Partial Backend Configuration (Zero Hardcoding)

To keep backend configurations 100% agnostic and reusable across environments, use **Partial Configuration**:

In `main.tf`, declare an empty backend block:
```hcl
terraform {
  required_version = ">= 1.6.0"
  backend "s3" {}
}
```

At initialization time, pass backend parameters dynamically via CLI or CI/CD:
```bash
terraform init \
  -backend-config="bucket=company-f5-tfstate-prod" \
  -backend-config="key=prod/chassis/pair-a/terraform.tfstate" \
  -backend-config="region=us-east-1" \
  -backend-config="dynamodb_table=f5-terraform-state-locks"
```

---

## 5. Security Checklist Before Committing to GitHub

- [x] All `.tfvars` files scrubbed of plaintext passwords.
- [x] Sensitive variables marked `sensitive = true` in all `variables.tf`.
- [x] Local `.tfstate` and `.tfstate.backup` excluded in `.gitignore`.
- [x] Remote backend encryption (SSE-KMS) enabled on state bucket.
- [x] State locking (DynamoDB / GCS) enabled to prevent race conditions.
