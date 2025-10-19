#!/bin/bash

cave_shaker() {
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Rembrandt USB4/Thunderbolt NHI controller #1
  echo 'auto' > '/sys/bus/pci/devices/0000:76:00.5/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Rembrandt Data Fabric: Device 18h; Function 0
  echo 'auto' > '/sys/bus/pci/devices/0000:00:18.0/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Rembrandt Data Fabric: Device 18h; Function 5
  echo 'auto' > '/sys/bus/pci/devices/0000:00:18.5/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] FCH SMBus Controller
  echo 'auto' > '/sys/bus/pci/devices/0000:00:14.0/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Audio Coprocessor
  echo 'auto' > '/sys/bus/pci/devices/0000:75:00.5/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Rembrandt Data Fabric: Device 18h; Function 7
  echo 'auto' > '/sys/bus/pci/devices/0000:00:18.7/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h-19h PCIe Dummy Host Bridge
  echo 'auto' > '/sys/bus/pci/devices/0000:00:02.0/power/control'
  # Runtime PM for PCI Device MEDIATEK Corp. MT7921 802.11ax PCI Express Wireless Network Adapter
  echo 'auto' > '/sys/bus/pci/devices/0000:04:00.0/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h-19h PCIe GPP Bridge
  echo 'auto' > '/sys/bus/pci/devices/0000:00:02.2/power/control'
  # Runtime PM for PCI Device NVIDIA Corporation AD107 High Definition Audio Controller
  echo 'auto' > '/sys/bus/pci/devices/0000:01:00.1/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Rembrandt Data Fabric: Device 18h; Function 3
  echo 'auto' > '/sys/bus/pci/devices/0000:00:18.3/power/control'
  # Runtime PM for PCI Device Kingston Technology Company, Inc. OM8SEP4 Design-In PCIe 4 NVMe SSD (TLC) (DRAM-less)
  echo 'auto' > '/sys/bus/pci/devices/0000:05:00.0/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h-19h PCIe GPP Bridge
  echo 'auto' > '/sys/bus/pci/devices/0000:00:02.4/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD/ATI] Rembrandt [Radeon 680M]
  echo 'auto' > '/sys/bus/pci/devices/0000:75:00.0/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h-19h PCIe GPP Bridge
  echo 'auto' > '/sys/bus/pci/devices/0000:00:01.1/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Rembrandt Data Fabric: Device 18h; Function 2
  echo 'auto' > '/sys/bus/pci/devices/0000:00:18.2/power/control'
  # Runtime PM for PCI Device Realtek Semiconductor Co., Ltd. RTL8111/8168/8211/8411 PCI Express Gigabit Ethernet Controller
  echo 'auto' > '/sys/bus/pci/devices/0000:03:00.0/power/control'
  # Runtime PM for disk sda
  echo 'auto' > '/sys/block/sda/device/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 19h USB4/Thunderbolt PCIe tunnel
  echo 'auto' > '/sys/bus/pci/devices/0000:00:03.1/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] FCH LPC Bridge
  echo 'auto' > '/sys/bus/pci/devices/0000:00:14.3/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h-19h Internal PCIe GPP Bridge
  echo 'auto' > '/sys/bus/pci/devices/0000:00:08.1/power/control'
  # Runtime PM for PCI Device NVIDIA Corporation AD107M [GeForce RTX 4050 Max-Q / Mobile]
  echo 'auto' > '/sys/bus/pci/devices/0000:01:00.0/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h-19h PCIe GPP Bridge
  echo 'auto' > '/sys/bus/pci/devices/0000:00:01.2/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD/ATI] Radeon High Definition Audio Controller [Rembrandt/Strix]
  echo 'auto' > '/sys/bus/pci/devices/0000:75:00.1/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Rembrandt Data Fabric: Device 18h; Function 1
  echo 'auto' > '/sys/bus/pci/devices/0000:00:18.1/power/control'
  # Runtime PM for PCI Device SK hynix Gold P31/BC711/PC711 NVMe Solid State Drive
  echo 'auto' > '/sys/bus/pci/devices/0000:02:00.0/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h-19h PCIe Dummy Host Bridge
  echo 'auto' > '/sys/bus/pci/devices/0000:00:01.0/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h-19h PCIe Dummy Host Bridge
  echo 'auto' > '/sys/bus/pci/devices/0000:00:04.0/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h-19h PCIe Dummy Host Bridge
  echo 'auto' > '/sys/bus/pci/devices/0000:00:03.0/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h-19h PCIe Dummy Host Bridge
  echo 'auto' > '/sys/bus/pci/devices/0000:00:08.0/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h-19h PCIe GPP Bridge
  echo 'auto' > '/sys/bus/pci/devices/0000:00:02.1/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h/19h/1ah HD Audio Controller
  echo 'auto' > '/sys/bus/pci/devices/0000:75:00.6/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h-19h Internal PCIe GPP Bridge
  echo 'auto' > '/sys/bus/pci/devices/0000:00:08.3/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h-19h IOMMU
  echo 'auto' > '/sys/bus/pci/devices/0000:00:00.2/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Rembrandt Data Fabric: Device 18h; Function 6
  echo 'auto' > '/sys/bus/pci/devices/0000:00:18.6/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 19h PSP/CCP
  echo 'auto' > '/sys/bus/pci/devices/0000:75:00.2/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Family 17h-19h PCIe Root Complex
  echo 'auto' > '/sys/bus/pci/devices/0000:00:00.0/power/control'
  # Runtime PM for PCI Device Advanced Micro Devices, Inc. [AMD] Rembrandt Data Fabric: Device 18h; Function 4
  echo 'auto' > '/sys/bus/pci/devices/0000:00:18.4/power/control'
}

main() {
  cave_shaker
  sleep 15
  cave_shaker
  sleep 30
  cave_shaker
}
