# Kernel Bare-Metal — Long Term

Eventual bare-metal boot:

POWER ON → UEFI/Firmware → Secure Boot → RAJARAM Bootloader → Hardware Discovery (CPU/GPU/NPU/RAM/Storage/Network/Sensors/Accelerators) → Memory Initialization → Interrupt Initialization → IOMMU Initialization → RAJARAM Core → Subsystem Initialization

For first implementation, replaced by Linux → RAJARAM service

## RAJARAM Microkernel (final stage)

- GDT / IDT
- Page Tables
- Interrupt Controller
- Scheduler
- Memory Manager
- IPC
- Capability Manager
- DMA Manager
- IOMMU
- Device Drivers
- Accelerator Runtime

This is major OS/hypervisor project, final stage not starting point.

## Hypervisor Version (intermediate)

RAJARAM HYPERVISOR → VM-A AI/GPU, VM-B Control/PLC, VM-C Research/FPGA
KVM useful because Linux exposes documented /dev/kvm interface through which VMs and vCPUs can be created and controlled.

## Build Order

00 SPECIFICATION → 01 SIMULATION → 02 RAJARAM CORE → 03 SARAM → 04 FAISANTH → 05 MULTI-AGENT → 06 PREMSOTH → 07 MAKESH+eBPF → 08 TRAINING FABRIC (DATAFORGE/SYNTHFORGE/FAILURE MEMORY/CURRICULUM/NEURAL FOUNDRY) → 09 MODEL EVOLUTION → 10 LOCAL AI → 11 BCI/Industrial/Robotics → 12 DISTRIBUTED COMPUTE → 13 KVM → 14 CUSTOM KERNEL → 15 BARE METAL
