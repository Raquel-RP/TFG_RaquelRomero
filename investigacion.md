## INVESTIGACIÓN TFG

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

### Tutoriales eBPF (Links)
https://eunomia.dev/tutorials/1-helloworld/

https://cilium.io/labs/categories/getting-started/

Labs de cilium: https://play.instruqt.com/embed/isovalent/tracks/cilium-getting-started

https://github.com/zoidyzoidzoid/awesome-ebpf

---

### Tutorial bpftrace 
Lenguaje de tracing de alto nivel y tiempo de ejecución para Linux basado en BPF. Admite seguimiento estático y dinámico tanto para el kernel como para el espacio de usuario.

#### >> bpftrace -l 'tracepoint:syscalls:sys_enter_*'

Hace un listado de todos los probes y se puede poner un termino de busqueda.
Un probe es un punto de instrumentación para capturar datos de eventos.

#### >> bpftrace -e 'BEGIN { printf("hello world\n"); }'
> Attaching 1 probe...
> hello world
> ^C

Esto imprime un mensaje de bienvenida. La palabra BEGIN es un probe especial que se activa al inicio del programa, antes que el resto de tracepoint, normalmente para imprimir mensajes iniciales. Puede usarlo para configurar variables e imprimir encabezados.
Se puede asociar una acción con probes, en { }. Este ejemplo llama a printf() cuando se activa el probe. Con -e indicamos que ejecute el programa/expresion a continuación.

#### >> bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("%s %s\n", comm, str(args.filename)); }'
> Attaching 1 probe...
> systemd-journal /proc/1856/status
> systemd-journal /proc/1856/status
> ...

Este archivo de seguimiento se abre a medida que ocurren y estamos imprimiendo el nombre del proceso y la ruta. Este archivo de seguimiento se abre a medida que ocurren y estamos imprimiendo el nombre del proceso y la ruta.

Comienza con el probe tracepoint:syscalls:sys_enter_openat: este es el tipo de probe de tracepoint (rastreo estático del kernel) y está instrumentando cuándo comienza (se ingresa) la llamada al sistema openat(). Se prefieren los tracepoints o puntos de seguimiento a los kprobes, ya que los puntos de seguimiento tienen una API estable. 
*comm* es una variable incorporada que tiene el nombre del proceso actual. Otras funciones integradas similares incluyen pid y tid.
*args* es una estructura que contiene todos los argumentos del punto de seguimiento. Esta estructura se genera automáticamente mediante información de punto de seguimiento basada en bpftrace. Los miembros de esta estructura se pueden encontrar con: bpftrace -vl tracepoint:syscalls:sys_enter_openat.
*args.filename* accede a la estructura args y obtiene el valor del miembro del nombre de archivo.
*str()* convierte un puntero en la cadena a la que apunta.

#### >> bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @[comm] = count(); }'
> Attaching 1 probe...
> ^C
> 
> @[wpa_supplicant]: 1
> @[ThreadPoolSingl]: 2
> @[(udev-worker)]: 3
> @[QXcbEventQueue]: 3
> @[gedit]: 4

Esto resume las syscalls por nombre de proceso, imprimiendo un informe en Ctrl-C.

@: denota un tipo de variable especial llamado mapa, que puede almacenar y resumir datos de diferentes maneras. Puede agregar un nombre de variable opcional después de @, por ejemplo, "@num", ya sea para mejorar la legibilidad o para diferenciar entre más de un mapa.
[]: Los corchetes opcionales permiten establecer una clave para el mapa, muy parecido a una matriz asociativa. (Como una tabla donde la columna 1 y 2 estan asociadas, por ejemplo, notas de un examen alumno->nota)
count(): esta es una función de mapa. count() cuenta el número de veces que se llama. Dado que esto se guarda mediante comm, el resultado es un recuento de frecuencia de syscalls por nombre de proceso.
Los mapas se imprimen automáticamente cuando finaliza bpftrace (por ejemplo, mediante Ctrl-C).

#### >> bpftrace -e 'tracepoint:syscalls:sys_exit_read /pid == 18644/ { @bytes = hist(args.ret); }'
> Attaching 1 probe...
> ^C
> 
> @bytes:
> [0, 1]                12 |@@@@@@@@@@@@@@@@@@@@                                |
> [2, 4)                18 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                     |
> [4, 8)                 0 |                                                    |
> [8, 16)                0 |                                                    |
> [16, 32)               0 |                                                    |
> [32, 64)              30 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
> [64, 128)             19 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                    |
> [128, 256)             1 |@

Esto resume el valor de retorno de la función del kernel sys_read() para el PID 18644, imprimiéndolo como un histograma.

/.../: Este es un filtro (también conocido como predicate), que actúa como filtro para la acción. La acción solo se ejecuta si la expresión filtrada es verdadera, en este caso, solo para el ID de proceso 18644. Se admiten operadores booleanos ("&&", "||").
ret: este es el valor de retorno de la función. Para sys_read(), esto es -1 (error) o la cantidad de bytes leídos correctamente.
@: Este es un mapa similar a la lección anterior, pero esta vez sin claves ([]) y el nombre "bytes" que decora la salida.
hist(): Esta es una función de mapa que resume el argumento como un histograma de potencia de 2. El resultado muestra filas que comienzan con notación de intervalo, donde, por ejemplo, [128, 256) significa que el valor es: 128<=valor<256. Otras funciones de mapa incluyen lhist() (hist lineal), count(), sum(), avg(), min() y max().

#### >> bpftrace -e 'kretprobe:vfs_read { @bytes = lhist(retval, 0, 2000, 200); }'
> Attaching 1 probe...
> ^C
> 
> @bytes:
> (..., 0)               7 |@@                                                  |
> [0, 200)             161 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
> [200, 400)             0 |                                                    |
> [400, 600)             0 |                                                    |
> [600, 800)             0 |                                                    |
> [800, 1000)            0 |                                                    |
> [1000, 1200)           2 |                                                    |

Resume los bytes read() como un histograma lineal y realiza un seguimiento mediante el seguimiento dinámico del kernel.

Comienza con el probe kretprobe:vfs_read: este es el tipo de sonda kretprobe (rastreo dinámico del kernel de funciones de retorno) que instrumenta la función del kernel vfs_read(). También existe el tipo kprobe, para instrumentar cuando las funciones comienzan a ejecutarse (se ingresan). Estos son tipos de probes potentes que le permiten rastrear decenas de miles de funciones del kernel diferentes. Sin embargo, estos son tipos de probes "inestables": dado que pueden rastrear cualquier función del kernel, no hay garantía de que su kprobe/kretprobe funcione entre versiones del kernel, ya que los nombres de las funciones, los argumentos, los valores de retorno y las funciones pueden cambiar. Además, dado que está rastreando el kernel sin formato, deberá explorar el código fuente del kernel para comprender qué significan estos probes, argumentos y valores de retorno.
lhist(): este es un histograma lineal, donde los argumentos son: valor, mínimo, máximo, paso. El primer argumento (retval) de vfs_read() es el valor de retorno: el número de bytes leídos.

#### >> bpftrace -e 'kprobe:vfs_read { @start[tid] = nsecs; } kretprobe:vfs_read /@start[tid]/ { @ns[comm] = hist(nsecs - @start[tid]); delete(@start[tid]); }'

> Attaching 2 probes...
> ^C
> 
> @ns[NetworkManager]:
> [8K, 16K)              1 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
> 
> @ns[sudo]:
> [8K, 16K)              5 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
> [16K, 32K)             2 |@@@@@@@@@@@@@@@@@@@@                                |
> 
> @ns[haroopad]:
> [1K, 2K)               2 |@@@                                                 |
> [2K, 4K)               0 |                                                    |
> [4K, 8K)               6 |@@@@@@@@@                                           |
> [8K, 16K)             32 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
> 
> @ns[telegram-deskto]:
> [1K, 2K)               6 |@@@@@@@@@@@@@                                       |
> [2K, 4K)               7 |@@@@@@@@@@@@@@@                                     |
> [4K, 8K)              23 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
> [8K, 16K)             18 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@            |
> [16K, 32K)             1 |@@                                                  |
> [32K, 64K)             1 |@@                                                  |
> 
> @ns[thunderbird]:
> [512, 1K)              1 |@@                                                  |
> [1K, 2K)               1 |@@                                                  |
> [2K, 4K)               8 |@@@@@@@@@@@@@@@@@@@                                 |
> [4K, 8K)              21 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
> [8K, 16K)             14 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                  |
> [16K, 32K)            19 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@     |
> 
> @start[3912]: 3951921123390
> @start[3899]: 3951924159969
> @start[1398]: 3951936619915

Resume el tiempo empleado en read(), en nanosegundos, como un histograma, por nombre de proceso.

@start[tid]: Esto utiliza el ID del hilo como clave. Puede haber muchas lecturas en curso y queremos almacenar una marca de tiempo de inicio para cada una. Podríamos construir un identificador único para cada lectura y usarlo como clave. Pero debido a que los subprocesos del kernel solo pueden ejecutar una llamada al sistema a la vez, podemos usar el ID del subproceso como identificador único, ya que cada subproceso no puede ejecutar más de uno.
nsecs: Nanosegundos desde el arranque. Este es un contador de marca de tiempo de alta resolución que se puede utilizar para cronometrar eventos.
/@start[tid]/: Este filtro verifica que la hora de inicio fue vista y registrada. Sin este filtro, este programa puede iniciarse durante una lectura y solo captar el final, lo que da como resultado un cálculo de tiempo de ahora - cero, en lugar de ahora -@[] inicio.
delete(@start[tid]): esto libera la variable.
https://eunomia.dev/tutorials/bpftrace-tutorial/

- - -

### eBPF Tutorial
(Bumblebee: https://bumblebee.io/EN   https://github.com/solo-io/bumblebee)

Un programa eBPF consta de dos partes principales: la parte del espacio del kernel y la parte del espacio del usuario. La parte del espacio del kernel contiene la lógica real del programa eBPF, mientras que la parte del espacio del usuario es responsable de cargar, ejecutar y monitorear el programa del espacio del kernel.

> Pasos previos
> - Instalar compiladores LLVM y Clang 
> https://releases.llvm.org/download.html   
> https://llvm.org/docs/GettingStarted.html#getting-the-source-code-and-building-llvm
> - Instalar framework de desarrollo BCC (eBPF Compiler Collection)
>  https://github.com/iovisor/bcc/blob/master/INSTALL.md (depende de la distro)
> - Instalar herramienta ecli y tools del compilador ecc
>  wget https://aka.pw/bpf-ecli -O ecli && chmod +x ./ecli
>  wget https://github.com/eunomia-bpf/eunomia-bpf/releases/latest/download/ecc && chmod +x ./ecc
 
---
### Objetivos

- filtrar por PID
- comunicaciones de internet
- dumpcap
- hacer ping y ver el PID y extrapolar su comunicacion a wireshark viendo que hace (icmp)


- por que hace falta, dificultades, estadisticas, citas, autores
- 