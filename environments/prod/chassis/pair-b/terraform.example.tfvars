f5os_chassis_endpoint = "https://10.2.0.10"
f5os_username         = "admin"
# Note: Sensitive credentials must NOT be stored in plain text.
# Inject at runtime via environment variable (TF_VAR_f5os_password) or HashiCorp Vault.
lag_name              = "bundle-1"
lag_member_interfaces = ["1.0", "2.0"]
tmos_image            = "BIGIP-17.1.1.3-0.0.5.ALL-F5OS.qcow2.zip"
