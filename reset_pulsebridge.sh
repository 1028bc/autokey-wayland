#!/bin/bash
# PulseBridge Emergency Recovery Script
echo "[RECOVERY] Initiating PulseBridge Kill Switch..."
pkill -9 pulsebridge
echo "[SUCCESS] All pulsebridge processes terminated."
