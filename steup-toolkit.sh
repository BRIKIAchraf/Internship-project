#!/bin/bash

# Define variables
SD_CARD="/dev/sda"
OS_IMAGE_XZ="2023-12-05-raspios-bookworm-arm64-full.img.xz"
OS_IMAGE="${OS_IMAGE_XZ%.xz}" # Removes the .xz extension
MOUNT_POINT="/mnt/raspi"

# Step 1: Flash Raspberry Pi OS onto the SD card
echo "Decompressing Raspberry Pi OS image..."
unxz --keep "$OS_IMAGE_XZ"

echo "Flashing Raspberry Pi OS to SD card ($SD_CARD)..."
dd if="$OS_IMAGE" of="$SD_CARD" bs=4M status=progress
sync

# Step 2: Mount the boot partition of the Raspberry Pi OS
echo "Mounting the boot partition..."
BOOT_PARTITION="${SD_CARD}1"
mkdir -p $MOUNT_POINT
mount "$BOOT_PARTITION" $MOUNT_POINT

# Step 3: Enable SSH on the Raspberry Pi OS
echo "Enabling SSH..."
touch "$MOUNT_POINT/ssh"

# Step 4: Copy necessary files to the SD card
echo "Copying Docker, Docker Compose files, and setup scripts..."
cp Dockerfile docker-compose.yml install_requirements.sh setup-toolkit.sh "$MOUNT_POINT"

# Unmount the boot partition
umount $MOUNT_POINT

# Step 5: Mount the root partition (assuming it's the second partition) to install Python packages
echo "Mounting the root partition..."
ROOT_PARTITION="${SD_CARD}2"
mkdir -p $MOUNT_POINT
mount "$ROOT_PARTITION" $MOUNT_POINT

# Copy the requirements.txt to the root partition
cp requirements.txt "$MOUNT_POINT/home/pi"

# Unmount the root partition
umount $MOUNT_POINT

echo "Script execution completed. The Raspberry Pi OS is ready on the SD card with SSH enabled."

# Reminder to the user
echo "Remember to run 'install_requirements.sh' and 'setup-toolkit.sh' after booting the Raspberry Pi for the first time."
