# UNIX Administration Wiki

A centralised knowledge base of HTML runbooks, procedures, and reference material for day-to-day UNIX systems administration across AIX and Linux environments.

## Purpose

This wiki serves as a living library of operational documentation — written by engineers, for engineers. Each article is a self-contained HTML runbook that can be opened in any browser, printed, or shared without external dependencies. The goal is to capture proven procedures, reduce tribal knowledge, and provide a reliable reference during both routine maintenance and incident response.

## What's inside

| Directory | Scope |
|---|---|
| **aix/lvm/** | Volume group management — rootvg, datavg, mirroring, PV operations |
| **aix/storage/** | Disk provisioning, SAN zoning, `cfgmgr`, ODM maintenance |
| **aix/networking/** | TCP/IP configuration, SSH, routing, name resolution |
| **aix/administration/** | User management, RBAC, NIM, mksysb, errpt analysis |
| **linux/storage/** | LVM, raw partitions, XFS/ext4 filesystems, multipath |
| **linux/networking/** | NIC bonding, firewall rules, SSH hardening |
| **linux/administration/** | User management, systemd, cron, kernel parameters |
| **backup/veeam/** | Repository provisioning, backup jobs, agents, recovery procedures |
| **backup/tsm/** | Node registration, schedules, policy domains, disaster recovery |
| **vtl/** | FalconStor VTL — configuration, hardening, virtual tape library management |
| **security/** | Hardening runbooks, vulnerability remediation, patching procedures |
| **reference/** | Cheat sheets and quick-reference cards (FTP, SCP, rsync, etc.) |

## File format

All documentation is stored as standalone `.html` files — no static site generator, no build step. Open any file directly in a browser to view it.
