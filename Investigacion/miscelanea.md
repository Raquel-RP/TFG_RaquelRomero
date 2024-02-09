## MISCELÁNEA

### Herramienta eBPF "Make the Kernel programmable"

https://alexmarket.medium.com/entendiendo-ebpf-una-tecnolog%C3%ADa-revolucionaria-en-linux-2ba7cb1e36b5
https://ebpf.io/what-is-ebpf/

- Ejecución y escritura de programas personalizados en el Kernel
- Máquina virtual que se ejecuta dentro del kernel de Linux
- Programas eBPF escritos en lenguaje de alto nivel
- Rastreo y perfilamiento (tracing & profiling): Los programas eBPF se pueden usar para rastrear aplicaciones y llamadas al sistema

El kernel de Linux contiene el tiempo de ejecución de eBPF necesario para ejecutar programas eBPF. Implementa la llamada al sistema bpf(2) para interactuar con programas, mapas, BTF y varios puntos adjuntos desde donde se pueden ejecutar programas eBPF. El kernel contiene un verificador eBPF para verificar la seguridad de los programas y un compilador JIT para traducir programas a código de máquina nativo. Las herramientas del espacio de usuario, como bpftool y libbpf, también se mantienen como parte del kernel ascendente

Ejemplos del libro Linux Observability with bpf: https://github.com/bpftools/linux-observability-with-bpf

Conformado por:
1.	eBPF Language
    - sudo C code: más común junto con compiladores para pasarlo a bytecode
    - Language Frameworks: lenguajes de más alto nivel (cilium, bcc, libbpf, ...) que producen eBPF bytecode

2.	eBPF Runtime
- Coge el bytecode y verifica que es seguro para ejecutarlo, lo compila (JIT Compiler) y lo corre en el hook point requerido



Process Tracer via exec() syscalls: https://github.com/iovisor/bcc/blob/master/tools/execsnoop.py

---
### ETW 
3 partes:
- Proveedor: emitirá un registro, identificado por una ID única
- Sesión: combinará uno o más proveedores
- Consumidor: leerá los registros emitidos por una sesión (event logger, logman, netsh, tracert)

---

### Winshark 

https://github.com/airbus-cert/Winshark

Implementa un backend para libpcap para capturar eventos ETW

3 partes:
- Wireshark.exe: analiza y disecciona protocolos
- dumpcap.exe: captura paquetes
- libpcap (wpcap.dll): se encarga de la interfaz entre dumpcap.exe y el sistema operativo

Winshark funciona en sesiones ETW, es por eso que puede seleccionar una sesión ETW en lugar de la interfaz de red al inicio de la captura. Luego, Winshark genera disectores lua para cada proveedor basado en manifiesto registrado en su computadora, durante el paso de instalación. Winshark también puede analizar proveedores basados en registros de seguimiento.
Información de los procesos: carga de CPU, Bytes privados, Working Set (Bytes totales), PID, Descripción del proceso, nombre de la compañía. 

---

### eCapture Herramienta

https://github.com/gojue/ecapture

eCapture busca el archivo /etc/ld.so.conf predeterminado, para buscar directorios de carga del archivo SO y buscar la ubicación de las bibliotecas de fragmentos openssl. O puede usar el indicador --libssl para establecer la ruta de la biblioteca de fragmentos.

./ecapture tls -i eth0 -w pcapng -p 443 

Con ese comando podemos obtener el resultado en pcapng y leerlo con Wireshark directamente.

---

### Instalaciones hechas

- BPFTool:
https://github.com/libbpf/bpftool/blob/main/README.md

- libbpf: https://github.com/libbpf/libbpf
Biblioteca basada en C que contiene un loader BPF que toma archivos objeto BPF compilados y los prepara y carga en el kernel de Linux. libbpf asume el trabajo pesado de cargar, verificar y adjuntar programas BPF a varios hooks del kernel, lo que permite a los desarrolladores de aplicaciones BPF centrarse únicamente en la corrección y el rendimiento del programa BPF.

    ~  bpftool version                                                      255 ✘
bpftool v7.3.0
using libbpf v1.3
features: llvm, skeletons

---