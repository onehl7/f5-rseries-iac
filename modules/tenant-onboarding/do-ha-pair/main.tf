terraform {
  required_version = ">= 1.6.0"
  required_providers {
    bigip = {
      source  = "f5networks/bigip"
      version = "~> 1.22.0"
    }
  }
}

# Declarative Onboarding HA Clustering & Device Group Definition
resource "bigip_do" "ha_pairing" {
  do_json = jsonencode({
    "$schema" : "https://raw.githubusercontent.com/F5Networks/f5-declarative-onboarding/master/schema/latest/base.schema.json",
    "class" : "DO",
    "declaration" : {
      "class" : "Device",
      "schemaVersion" : "1.42.0",
      "async" : true,
      "label" : "LTM Active/Standby HA Pairing for ${var.pair_name}",
      "Common" : {
        "class" : "Tenant",
        "myFailover" : {
          "class" : "Failover",
          "unicastAddress" : var.local_sync_ip,
          "unicastPeerAddress" : var.peer_sync_ip
        },
        "myConfigSync" : {
          "class" : "ConfigSync",
          "configsyncIp" : var.local_sync_ip
        },
        "myDeviceTrust" : {
          "class" : "DeviceTrust",
          "userName" : var.peer_admin_user,
          "password" : var.peer_admin_password,
          "remoteHost" : var.peer_mgmt_ip
        },
        "myDeviceGroup" : {
          "class" : "DeviceGroup",
          "type" : "sync-failover",
          "members" : [
            var.local_hostname,
            var.peer_hostname
          ],
          "autoSync" : true,
          "networkFailover" : true
        }
      }
    }
  })

  timeout = 45
}
