# VM de Windows (opcional)

Un Windows en una VM de libvirt/KVM que se enciende desde el Panel y se usa por RDP desde cualquier aparato
de la casa (Windows App en celular, tablet o PC) o desde el navegador con Guacamole.

## 1. La VM

- Créala con virt-manager en la red NAT por defecto de libvirt. Dale una IP fija dentro de la NAT
  (reserva DHCP en la red `default`) y anótala en `VM_IP`; su nombre de dominio va en `VM_NOMBRE` (`.env`).
- Dentro de Windows: activa Escritorio remoto y usa un usuario con contraseña.
- El Panel usa `virsh -c qemu:///system`: tu usuario debe poder manejar VMs de sistema (grupo `libvirt`).

## 2. Publicar el RDP en la red de casa

La NAT de libvirt no se ve desde la LAN. `sistema/rdp-vm.service.example` reenvía el 3389 de la PC a la VM
con `socat`:

```bash
sudo dnf install socat            # o el gestor de tu distro
sudo cp sistema/rdp-vm.service.example /etc/systemd/system/rdp-vm.service
sudo sed -i 's/192.168.122.30/<VM_IP>/' /etc/systemd/system/rdp-vm.service
sudo systemctl enable --now rdp-vm.service
sudo firewall-cmd --permanent --add-port=3389/tcp && sudo firewall-cmd --reload   # si usas firewalld
```

Conéctate con Windows App a `<NAS_IP>`.

## 3. Guacamole (la VM en el navegador)

`instalar.sh` crea `appdata/guacamole/user-mapping.xml` desde la plantilla cuando `VM_NOMBRE` tiene valor.
Pon el usuario del portal, su clave en MD5 (`echo -n 'clave' | md5sum`), la IP de la VM y el usuario de
Windows. Se enciende desde el Panel ("Portal web de la VM") y se abre en `http://<NAS_IP>:8080/guacamole`.

## 4. El indicador del Tablero

"¿El Windows está listo?" consulta `http://…:3001/salud/vm`: verde solo si la VM está encendida **y** su RDP
ya contesta. Recién encendida tarda ~1 min en ponerse verde.
