# UNIX Administration Wiki

A centralised knowledge base of HTML runbooks, procedures, and reference material for day-to-day UNIX systems administration across AIX and Linux environments.

## Purpose

This wiki serves as a living library of operational documentation, compiled by myself over the course of my 7 year unix career. Each article is a self-contained HTML runbook that can be opened in any browser, printed, or shared without external dependencies. The goal is to capture proven procedures, reduce tribal knowledge, and provide a reliable reference during both routine maintenance and incident response tickets.

## How to browse

The wiki is published via GitHub Pages — the proper way to read it is at:

**https://triippiing.github.io/Wiki/**

The landing page (`index.html`) is auto-generated from the directory tree by `scripts/build_index.py`, which walks the wiki, groups runbooks by category, and produces a searchable index. Re-run that script after adding or renaming articles to refresh the front page.

Cloning the repo and opening the `.html` files directly also works — every runbook is self-contained with no external dependencies.

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
| **scripts/** | Tooling for the wiki itself — currently `build_index.py` for index generation |

Several of these directories are sparsely populated today and will fill out over time as procedures get written up. The full taxonomy is intentional — it's the shape the wiki is growing into, not a snapshot of what's already there.

## File format

All documentation is stored as standalone `.html` files — no framework, no theme, no JavaScript bundler. Each runbook can be opened directly in a browser, printed, or emailed without any build step. The only generated file is the root `index.html`, produced by `scripts/build_index.py` after new content is added.
