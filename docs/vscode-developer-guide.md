# VS Code Developer Guide: F5 iSeries to rSeries Migration

This guide explains how to use and maintain this repository inside **Visual Studio Code (VS Code)**, whether working manually with the terminal, using VS Code tasks, or using AI assistants (GitHub Copilot, Cursor, Continue.dev).

---

## 1. Opening the Project in VS Code

1. Open the repository root directory in VS Code:
   ```bash
   code "/path/to/IaC F5"
   ```
2. When prompted with **"Do you want to install the recommended extensions for this repository?"**, click **Install All**.

### Recommended Extensions (configured in `.vscode/extensions.json`):
* **F5 Extension for VS Code (`f5devcentral.vscode-f5`)**: Official F5 DevCentral extension. Allows you to connect directly to F5OS chassis and TMOS tenants, post AS3/DO declarations, and view real-time system logs.
* **HashiCorp Terraform (`hashicorp.terraform`)**: Provides HCL syntax highlighting, auto-completion, and formatting.
* **Python & Pylance (`ms-python.python`)**: Autocomplete and linting for the `tools/assessment/` engine.
* **Red Hat YAML (`redhat.vscode-yaml`)**: Schema validation for CI/CD workflows and declarations.
* **Markdown Mermaid (`bierner.markdown-mermaid`)**: Live preview for the architecture and sequence diagrams in `docs/`.

---

## 2. Using Built-in VS Code Tasks (One-Click Operations)

You don't need to memorize long CLI commands. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux) -> Select **Tasks: Run Task**:

| Task Name | Keyboard Shortcut / Action | What It Does |
| :--- | :--- | :--- |
| **`F5: Run Migration Assessment`** | Default Build (`Cmd+Shift+B`) | Runs `run_assessment.py` against the legacy test fixture and updates AS3/JSON reports. |
| **`F5: Run Assessment Unit Tests`** | Run Test Task | Executes `python3 -m unittest discover -s tests/unit`. |
| **`Terraform: Format All Files`** | Run Task | Automatically formats all `.tf` and `.tfvars` files using `terraform fmt`. |
| **`Terraform: Plan Pair-A Chassis`** | Run Task | Runs `terraform plan` for `environments/prod/chassis/pair-a/`. |
| **`Terraform: Plan Pair-A LTM Onboarding`** | Run Task | Runs `terraform plan` for Pair-A DO onboarding. |
| **`Terraform: Plan Pair-A LTM App Services`** | Run Task | Runs `terraform plan` for Pair-A AS3 applications. |

---

## 3. Working with F5 AS3 & DO JSON Schemas in VS Code

The `.vscode/settings.json` file automatically links all `*as3*.json` and `*do*.json` files to their official F5 GitHub JSON schemas:
- **Instant IntelliSense**: As you type JSON in `as3_declaration_output.json`, VS Code provides autocomplete for valid AS3 classes (`Service_HTTPS`, `Pool`, `Monitor`, `TLS_Server`).
- **Real-Time Linting**: If a required field (such as `virtualPort` or `virtualAddresses`) is missing, VS Code highlights it in red with the schema error explanation.

---

## 4. Using AI Assistants in VS Code (GitHub Copilot, Cursor, etc.)

We have pre-configured [`.github/copilot-instructions.md`](file:///Users/hl/Documents/antigravity/IaC%20F5/.github/copilot-instructions.md) and [`.cursorrules`](file:///Users/hl/Documents/antigravity/IaC%20F5/.cursorrules/). 

When you use GitHub Copilot Chat or Cursor in VS Code, the AI assistant automatically adopts the repository's 4 personas and guardrails:

### Example Prompts in VS Code Copilot / Cursor:
* **To assess a new legacy file**:
  > *"As `migration-analyst`, write a test that runs `tools/assessment/run_assessment.py` on my new file `dc2_legacy.conf`."*
* **To create a new AS3 service**:
  > *"As `bigip-tenant-engineer`, add an AS3 declaration for a new payment API on port 8443 with TLS offloading into `environments/prod/tenants/pair-a/ltm/app-services/`."*
* **To verify r5900 hardware bounds**:
  > *"As `f5os-platform-architect`, verify if our tenant configurations in `environments/prod/chassis/pair-a/` stay within the 28 vCPU limit."*

---

## 5. Universal Terminal / Makefile Support

If you prefer using the integrated VS Code terminal (`Ctrl+\`` or `Cmd+\``), the root [Makefile](file:///Users/hl/Documents/antigravity/IaC%20F5/Makefile) works identically across all systems:
```bash
make assess       # Runs assessment tool
make test         # Runs Python unit tests
make lint         # Checks Terraform formatting
make fmt          # Formats all Terraform code
make clean        # Cleans temporary test outputs
```
