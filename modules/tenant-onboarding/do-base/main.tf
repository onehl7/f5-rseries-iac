terraform {
  required_version = ">= 1.6.0"
  required_providers {
    bigip = {
      source  = "f5networks/bigip"
      version = "~> 1.22.0"
    }
  }
}

# F5 Declarative Onboarding (DO) Base Platform Configuration
resource "bigip_do" "base_onboarding" {
  do_json = jsonencode({
    "$schema" : "https://raw.githubusercontent.com/F5Networks/f5-declarative-onboarding/master/schema/latest/base.schema.json",
    "class" : "DO",
    "declaration" : {
      "class" : "Device",
      "schemaVersion" : "1.42.0",
      "async" : true,
      "label" : "Base TMOS Onboarding for ${var.hostname}",
      "Common" : {
        "class" : "Tenant",
        "hostname" : var.hostname,
        "myNtp" : {
          "class" : "NTP",
          "servers" : var.ntp_servers,
          "timezone" : var.timezone
        },
        "myDns" : {
          "class" : "DNS",
          "nameServers" : var.dns_servers,
          "search" : var.dns_search_domains
        },
        "mySyslog" : {
          "class" : "SyslogRemoteServer",
          "remoteServers" : [
            for s in var.syslog_servers : {
              "host" : s.host,
              "remotePort" : s.port
            }
          ]
        },
        "mySnmp" : {
          "class" : "SNMP",
          "communities" : {
            "comm1" : {
              "communityName" : var.snmp_community,
              "access" : "read-only"
            }
          }
        }
      }
    }
  })

  timeout = 30
}
