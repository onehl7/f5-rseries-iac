terraform {
  required_version = ">= 1.6.0"
  required_providers {
    bigip = {
      source  = "f5networks/bigip"
      version = "~> 1.22.0"
    }
  }
}

# Declarative AS3 HTTP / HTTPS Application Service
resource "bigip_as3" "http_service" {
  as3_json = jsonencode({
    "$schema" : "https://raw.githubusercontent.com/F5Networks/f5-appsvcs-extension/master/schema/latest/as3-schema.json",
    "class" : "AS3",
    "action" : "deploy",
    "persist" : true,
    "declaration" : {
      "class" : "ADC",
      "schemaVersion" : "3.50.0",
      "id" : "urn:f5:rseries:${var.tenant_name}:${var.app_name}",
      "label" : "AS3 Service for ${var.app_name}",
      (var.tenant_name) : {
        "class" : "Tenant",
        (var.app_name) : {
          "class" : "Application",
          "template" : "generic",
          "serviceMain" : {
            "class" : var.enable_tls ? "Service_HTTPS" : "Service_HTTP",
            "virtualAddresses" : [var.virtual_ip],
            "virtualPort" : var.virtual_port,
            "snat" : var.snat_type,
            "pool" : "app_pool",
            "serverTLS" : var.enable_tls ? "webtls" : null
          },
          "app_pool" : {
            "class" : "Pool",
            "loadBalancingMode" : var.lb_method,
            "monitors" : [
              {
                "use" : "http_health_monitor"
              }
            ],
            "members" : [
              for m in var.pool_members : {
                "servicePort" : m.port,
                "serverAddresses" : m.servers
              }
            ]
          },
          "http_health_monitor" : {
            "class" : "Monitor",
            "monitorType" : "http",
            "interval" : var.monitor_interval,
            "timeout" : var.monitor_timeout,
            "send" : var.monitor_send_string,
            "receive" : var.monitor_recv_string
          },
          "webtls" : var.enable_tls ? {
            "class" : "TLS_Server",
            "certificates" : [
              {
                "certificate" : "app_cert"
              }
            ],
            "ciphers" : "ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384"
          } : null,
          "app_cert" : var.enable_tls ? {
            "class" : "Certificate",
            "certificate" : {
              "bigip" : var.cert_path
            }
          } : null
        }
      }
    }
  })
}
