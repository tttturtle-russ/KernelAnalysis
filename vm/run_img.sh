#!/bin/bash
PROJECTROOT="$VM_DIR"/bin
MEM_DIR=/dev/shm/kconcur
IMG="$VM_DIR"/image/bullseye.img

if [ ! -d $MEM_DIR ];then
  mkdir -p $MEM_DIR
fi

qemu-system-x86_64 \
  -m 4G \
  -smp 4 \
  -drive file=$IMG,format=raw \
  -kernel "$KERNEL_DIR"/arch/x86/boot/bzImage \
  -append "console=ttyS0 root=/dev/sda earlyprintk=serial net.ifnames=0 nokaslr isolcpus=0,1,2" \
  -net user,host=10.0.2.10,hostfwd=tcp:127.0.0.1:2222-:22 \
  -net nic,model=e1000 \
  -net nic,model=virtio \
  -fsdev local,id=test_dev,path=$PROJECTROOT,security_model=none -device virtio-9p-pci,fsdev=test_dev,mount_tag=project_mount \
  -fsdev local,id=data_dev,path=$MEM_DIR,security_model=none -device virtio-9p-pci,fsdev=data_dev,mount_tag=data_mount \
  -nographic \
  -enable-kvm \
  -pidfile "$VM_DIR"/.pid \
  -s \
  -device usb-ehci,id=ehci \
  -device usb-kbd\
  -device virtio-vga\
  -device usb-mouse\
  -device usb-kbd\
  -device usb-tablet\
  -machine q35 \
  -device piix3-usb-uhci\
  -device amd-iommu \
  -chardev socket,id=char0,path=/tmp/vcon0,server=on,wait=off \
  -device virtio-serial \
  -device virtio-serial-pci \
  -device virtconsole \
  -device virtserialport \
  -device e1000,netdev=net0 \
  -device virtio-rng-pci\
  -device virtio-net\
  -netdev user,id=net0 \
  -device pci-serial\
  -device virtserialport,chardev=char0,name=org.foo.bar.0\
  -device virtio-serial-pci \
  -chardev socket,path=/tmp/vmchannel,server=on,wait=off,id=vmchannel\
  -device virtserialport,chardev=vmchannel,name=org.qemu.guest_agent.0\
  -cpu host #> "$VM_DIR"/.log 2>&1

  #-snapshot \
