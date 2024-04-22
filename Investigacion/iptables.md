### USER ID CON IPTABLES
La idea de esta implementación es crear un nuevo user del sistema a través del cual iremos filtrando todos sus procesos.
Este filtrado se realizará con iptables.

(Opción de hacerlo con eBPF: https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/tree/samples/bpf/xdp2skb_meta_kern.c?h=v6.1#n57)

 sudo useradd user_filter
 
 Si quisiera generar un UID concreto
 sudo useradd -u 1500 user_filter
 
>  sudo passwd user_filter                                     
New password: 1234
Retype new password: 1234

sudo iptables -N FILTER_BY_UID
sudo iptables -A FILTER_BY_UID -m owner --uid-owner user_filter -j MARK --set-mark 1

sudo iptables -A FORWARD -m mark --mark 1 -j REDIRECT --to-port 8080

id user_filter
uid=1001(user_filter) gid=1001(user_filter) groups=1001(user_filter)


Chain INPUT (policy ACCEPT)
target     prot opt source               destination

Chain FORWARD (policy ACCEPT)
target     prot opt source               destination

Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination
FILTER_BY_UID  all  --  anywhere             anywhere

Chain FILTER_BY_UID (1 references)
target     prot opt source               destination
DROP       all  --  anywhere             anywhere             owner UID match user_filter

### NFLOG

`sudo iptables -A OUTPUT -m owner --uid-owner 1001 -j CONNMARK --set-mark 1`
`sudo iptables -A INPUT -m connmark --mark 1 -j NFLOG`
`sudo iptables -A OUTPUT -m connmark --mark 1 -j NFLOG`
`dumpcap -i nflog -w uid-1001.pcap`

NFLOG --nflog-group 2 
núemero de registros

sudo iptables -L
> Chain INPUT (policy ACCEPT)
> target     prot opt source               destination
> NFLOG      all  --  anywhere             anywhere             connmark match  0x1 nflog-group 30
> 
> Chain FORWARD (policy ACCEPT)
> target     prot opt source               destination
> 
> Chain OUTPUT (policy ACCEPT)
> target     prot opt source               destination
> CONNMARK   all  --  anywhere             anywhere             owner UID match user_filter CONNMARK set 0x1
> NFLOG      all  --  anywhere             anywhere             connmark match  0x1 nflog-group 30


https://serverfault.com/questions/610989/linux-nflog-documentation-configuration-from-c

sudo systemctl enable iptables.service

Para llamar cualquier comando desde otro user
sudo -u user_filter curl http://192.168.1.1

**CÓODIGO PYTHON**
- python-iptables (pip install python-iptables)
sudo pip install --upgrade python-iptables 
https://developers.redhat.com/blog/2020/08/18/iptables-the-two-variants-and-their-relationship-with-nftables#the_kernel_api
sudo iptables-legacy -L

**PRUEBAS**
- users de /etc/passwd
- user: systemd-resolve

**POETRY**
https://www.freecodecamp.org/news/how-to-build-and-publish-python-packages-with-poetry/
- poetry add "paquete version"
- poetry update 
- poetry shell : acceder al ambiente virutal
- poetry export --output requirements.txt
- poetry build
- poetry publish

**OPEN EDR**
- Directorio /opt/COMODO
- Agente /opt/COMODO/ECC
- https://ketanic3gmailcom.itsm-us1.comodo.com/dashboard/widgets/overview#/dashboard/overview
**MEJORAS CÓDIGO**
- Marcado que compruebe que no haya una marca ya igual
- Asignado de UID que compruebe que no existe
- Imprimir resultados (uid dado, iptables añadidas)
- Correr el programa por nombre de usuario o UID
- Poder añadir varios usuarios, que compruebe si la cadena ya está creada
- Mejora de como llamar a la app (add iptables)
- Chekear si la cadena ya esta creada

**ELK STACK**
Docker completo:
https://github.com/deviantony/docker-elk?tab=readme-ov-file
docker-compose up setup
docker-compose up
docker-compose down -v
