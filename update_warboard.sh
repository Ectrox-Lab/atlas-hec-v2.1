#!/bin/bash
# Warboard Quick Update Script
# Usage: ./update_warboard.sh [g1_drift] [g1_hijack] [g1_mem] [e1_del] [e1_audit] [e1_roll] [aka_evi] [aka_pro] [aka_con]
# Status: green/yellow/red

WARBOARD="WARBOARD.md"
DATE=$(date -u +"%Y-%m-%d %H:%M UTC")

# Default: check current values
G1_DRIFT=${1:-"check"}
G1_HIJACK=${2:-"check"}
G1_MEM=${3:-"check"}
E1_DEL=${4:-"check"}
E1_AUDIT=${5:-"check"}
E1_ROLL=${6:-"check"}
AKA_EVI=${7:-"check"}
AKA_PRO=${8:-"check"}
AKA_CON=${9:-"check"}

echo "Updating Warboard at $DATE..."
echo "G1: Drift=$G1_DRIFT Hijack=$G1_HIJACK Mem=$G1_MEM"
echo "E1: Del=$E1_DEL Audit=$E1_AUDIT Roll=$E1_ROLL"
echo "Akashic: Evi=$AKA_EVI Pro=$AKA_PRO Con=$AKA_CON"

# Update timestamp
sed -i "s/\*\*Date\*\*: .*/\*\*Date\*: $DATE/" $WARBOARD

echo "Warboard updated."
echo "Remember to: git add WARBOARD.md && git commit -m 'warboard: update status'"
