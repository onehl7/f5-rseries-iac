terraform {
  required_version = ">= 1.6.0"
  required_providers {
    bigip = {
      source  = "f5networks/bigip"
      version = "~> 1.22.0"
    }
  }
}

# Declarative AS3 Application Security (WAF) Policy Binding
resource "bigip_as3" "waf_service" {
  as3_json = jsonencode({
    "$schema" : "https://raw.githubusercontent.com/F5Networks/f5-appsvcs-extension/master/schema/latest/as3-schema.json",
    "class" : "AS3",
    "action" : "deploy",
    "persist" : true,
    "declaration" : {
      "class" : "ADC",
      "schemaVersion" : "3.50.0",
      "id" : "urn:f5:rseries:${var.tenant_name}:waf:${var.app_name}",
      (var.tenant_name) : {
        "class" : "Tenant",
        (var.app_name) : {
          "class" : "Application",
          "template" : "generic",
          "serviceMain" : {
            "class" : "Service_HTTPS",
            "virtualAddresses" : [var.virtual_ip],
            "virtualPort" : 443,
            "policyWAF" : {
              "use" : "waf_policy"
            },
            "serverTLS" : "webtls",
            "pool" : "app_pool"
          },
          "waf_policy" : {
            "class" : "WAF_Policy",
            "url" : var.waf_policy_url,
            "ignoreChanges" : false
          },
          "app_pool" : {
            "class" : "Pool",
            "members" : [
              for m in var.pool_members : {
                "servicePort" : m.port,
                "serverAddresses" : m.servers
              }
            ]
          },
          "webtls" : {
            "class" : "TLS_Server",
            "certificates" : [{ "certificate" : "app_cert" }]
          },
          "app_cert" : {
            "class" : "Certificate",
            "certificate" : { "bigip" : var.cert_path }
          }
        }
      }
    }
  })
}
