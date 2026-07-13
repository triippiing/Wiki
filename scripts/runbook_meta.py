#!/usr/bin/env python3
"""Approved identity data for every runbook: RB-ID + one-line operation.

This file is the source of truth for the top-of-page identity strip. It is
DATA, not code — it exists so the decisions survive a lost session and can be
resumed cold. See docs/META_GRID_MIGRATION.md.

Scheme:  RB-<DOMAIN>-<PLATFORM>-<NNN>

  DOMAIN    PATCH  patching / upgrade / migration / hardening
            PERF   performance diagnosis
            ADM    routine administration (users, logs)
            LVM    disks, volume groups, filesystems
            NET    networking
            SEC    access / key management
            BKP    backup imaging
            TSM    IBM Spectrum Protect / TSM
            COH    Cohesity
            REF    lookup / reference sheet

  PLATFORM  AIX · LNX · VMW · VTL · SRV (server-side, e.g. TSM server itself)

The five IDs that already existed in the runbooks are preserved exactly.

`operation` is the one-line summary shown in the identity strip. Keep it SHORT
(≈ 40 chars) — it sits beside the ID and the review date, and the fuller
description already appears directly above the grid as the page subtitle.

STATUS: IDs approved by Jack 2026-07-13. The `operation` strings are DRAFTS I
proposed and are NOT yet approved — review them before or during the migration.
"""
from __future__ import annotations

# rel_path -> (rb_id, operation)
RUNBOOKS: dict[str, tuple[str, str]] = {
    # ── AIX · patching & migration ──
    "aix/administration/aix_tl_upgrade.html": (
        "RB-PATCH-AIX-001", "In-place TL / SP update"),
    "aix/administration/aix_71_to_72_migration_nim.html": (
        "RB-PATCH-AIX-002", "Version migration · 7.1 → 7.2 · nimadm"),
    "aix/administration/aix_71_to_72_migration_bootmedia.html": (
        "RB-PATCH-AIX-003", "Version migration · 7.1 → 7.2 · boot media"),
    "vtl/VTL tomcat patching and hardening.html": (
        "RB-PATCH-VTL-001", "Tomcat CVE remediation & hardening"),

    # ── AIX · operations ──
    "aix/administration/aix_performance_triage.html": (
        "RB-PERF-AIX-001", "Performance triage · CPU / memory / I/O"),
    "aix/administration/user_administration.html": (
        "RB-ADM-AIX-001", "User & group administration"),
    "aix/lvm/AIX rootvg disk replacement.html": (
        "RB-LVM-AIX-001", "rootvg mirror disk replacement"),
    "aix/lvm/aix_lvm_basics.html": (
        "RB-LVM-AIX-002", "VG / LV / filesystem provisioning"),
    "aix/networking/aix_vlan_ip_discovery_runbook.html": (
        "RB-NET-AIX-001", "VLAN & IP discovery"),
    "aix/networking/sshkey_aix_to_hmc_runbook.html": (
        "RB-SEC-AIX-001", "SSH key auth · AIX → HMC"),
    "backup/aix/aix_mksysb.html": (
        "RB-BKP-AIX-001", "mksysb image · local, NIM, tape"),

    # ── Linux ──
    "linux/administration/linux_log_housekeeping.html": (
        "RB-ADM-LNX-001", "Log housekeeping & logrotate config"),
    "linux/administration/logrotate_config.html": (
        "RB-ADM-LNX-002", "Logrotate · HMC backup logs"),
    "linux/networking/linux_networking.html": (
        "RB-NET-LNX-001", "Interfaces, routes, NetworkManager, firewalld"),
    "linux/storage/linux_disk_and_lvm_operations.html": (
        "RB-LVM-LNX-001", "Disk & LVM · extend / recover"),
    "linux/storage/Veeam linux fs creation .html": (
        "RB-LVM-LNX-002", "Veeam repo · disk provisioning"),
    "linux/administration/rhel_licensing_cheat_sheet.html": (
        "RB-REF-LNX-001", "RHEL licensing · subscription-manager"),

    # ── Backup ──
    "backup/tsm/tsm_baclient_nim_install.html": (
        "RB-TSM-AIX-001", "BA client binary NIM install"),
    "backup/tsm/TSM customer onboarding.html": (
        "RB-TSM-SRV-001", "Customer onboarding · node & policy setup"),
    "backup/tsm/TSM server and stgpool setup.html": (
        "RB-TSM-SRV-002", "Storage architecture · SSD + COS tiered pools"),
    "cohesity/backups/cohesity_register_vcenter_source.html": (
        "RB-COH-VMW-001", "Register vSphere (vCenter) source"),
}


def lookup(rel_path: str) -> tuple[str, str] | None:
    return RUNBOOKS.get(rel_path)


if __name__ == "__main__":
    print(f"{len(RUNBOOKS)} runbooks\n")
    for rel, (rb_id, op) in sorted(RUNBOOKS.items(), key=lambda kv: kv[1][0]):
        print(f"  {rb_id:<17} {op:<46} {rel}")
