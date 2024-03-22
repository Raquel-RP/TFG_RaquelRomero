# eBPF Desarrollo de Programas
(Bumblebee: https://bumblebee.io/EN   https://github.com/solo-io/bumblebee)

Un programa eBPF consta de dos partes principales: la parte del **espacio del kernel** y la parte del **espacio del usuario**. La parte del espacio del kernel contiene la lógica real del programa eBPF, mientras que la parte del espacio del usuario es responsable de cargar, ejecutar y monitorear el programa del espacio del kernel.

> Pasos previos
> - Instalar compiladores LLVM y Clang
> https://releases.llvm.org/download.html
> https://llvm.org/docs/GettingStarted.html#getting-the-source-code-and-building-llvm
> - Instalar framework de desarrollo BCC (eBPF Compiler Collection)
>  https://github.com/iovisor/bcc/blob/master/INSTALL.md (depende de la distro)
> - Instalar herramienta ecli y tools del compilador ecc
>  wget https://aka.pw/bpf-ecli -O ecli && chmod +x ./ecli
>  wget https://github.com/eunomia-bpf/eunomia-bpf/releases/latest/download/ecc && chmod +x ./ecc


**Partes de un programa eBPF:**
- Espacio del kernel: contiene la lógica del programa eBPF
- Espacio del usuario: responsable de la carga, ejecución y monitorización del programa del espacio del kernel

**Proceso de desarrollo de programas eBPF:**
1. Escribir programa eBPF (en C): Se ejecuta en el espacio del kernel y hace tareas específicas
2. Escribir programa del espacio de usuario (en Python, C, etc...): necesario usar la API que da BCC para cargar y manipular el programa del espacio del kernel.
3. Compilar el programa eBPF: usar BCC tool para compilar (C -> bytecode).
4. Carga y ejecución del programa eBPF: en el programa del espacio de usuario usar la API de BCC para cargar el programa compilado de eBPF en el kernel y luego ejecutarlo.
5. Unloading el programa eBPF: cuando ya no haga falta más, el programa del espacio de usuario debe hacer el unload del kernel con la BCC API.
6. Debugging y optimizacion: usar herramientas como bpftool.

**Ejemplo de compilado y ejecución de programa eBPF:**
```sh
$ ./ecc ejemplo.bpf.c
Compiling bpf object...
Packing ebpf object and config into package.json...

$ sudo ./ecli run package.json
Running eBPF program...
```
Esto generaría los siguientes ficheros:
- ejemplo.bpf.o
- ejemplo.skel.json
- package.json

Para ver la salida del programa, en el caso de que no tenga programa del espacio de usuario chequearemos la carpeta _/sys/kernel/debug/tracing/trace_pipe_:
```sh
$ sudo cat /sys/kernel/debug/tracing/trace_pipe | grep "output que busquemos"
```
---
### Framework básico de un programa eBPF

- Incluir archivos de headers.
- Definir una licencia: normalmente utilizando "_Dual BSD/GPL_".
- Definir una función BPF: por ejemplo, denominada _handle_tp_, que toma _void *ctx_ como parámetro y devuelve int. Suele ser en lenguaje C.
- Usar funciones auxiliares de BPF: como _bpf_get_current_pid_tgid()_ y _bpf_printk()_.
- Añadir valor de retorno.

**Tracepoints:**

Técnica de instrumentación estática del kernel, técnicamente son **funciones de seguimiento colocadas en el código fuente del kernel**, que son esencialmente puntos de sondeo (_probe points_) con condiciones de control insertadas en el código fuente, lo que permite el posprocesamiento con funciones de procesamiento adicionales.
Por ejemplo, el método de seguimiento estático más común en el kernel es **printk**, que genera mensajes de log.
Hay tracepoints al inicio y al final de las syscalls, eventos del programador (scheduler events), operaciones del sistema de archivos y E/S del disco. Los tracepoints son una API estable y su número es limitado.


---
### Helper function bpf_clone_redirect
Clona y redirige el paquete asociado con skb a otro dispositivo de red de índice _ifindex_. Se pueden utilizar interfaces de entrada y salida para la redirección. El valor BPF_F_INGRESS en las flags se utiliza para hacer la distinción (la ruta de entrada se selecciona si la flag está presente, la ruta de salida en caso contrario). Esta es la única flag admitida por ahora.

En comparación con el helper bpf_redirect(), bpf_clone_redirect() tiene el costo asociado de duplicar el búfer de paquetes, pero esto se puede ejecutar desde el programa eBPF. Por el contrario, bpf_redirect() es más eficiente, pero se maneja mediante un código de acción donde la redirección ocurre solo después de que el programa eBPF haya regresado.

Una llamada a este helper es susceptible de cambiar el búfer de paquetes subyacente. Por lo tanto, en el momento de la carga, todas las comprobaciones de los punteros realizadas previamente por el verificador se invalidan y deben realizarse nuevamente, si el asistente se utiliza en combinación con el acceso directo a paquetes.

**Returns**
0 en caso de éxito, o un error negativo en caso de fallo. El error positivo indica una posible caída o congestión en el dispositivo de destino. Los códigos de error positivos particulares no están definidos.
```
static long (*bpf_clone_redirect)(struct __sk_buff *skb, __u32 ifindex, __u64 flags) = (void *) 13;
```
**Tipos de programas**
Esta helper call se puede utilizar en los siguientes tipos de programas:

BPF_PROG_TYPE_LWT_XMIT
BPF_PROG_TYPE_SCHED_ACT
BPF_PROG_TYPE_SCHED_CLS

---
### Tutoriales eBPF (Links)
https://eunomia.dev/tutorials/1-helloworld/

https://cilium.io/labs/categories/getting-started/

Labs de cilium: https://play.instruqt.com/embed/isovalent/tracks/cilium-getting-started

https://github.com/zoidyzoidzoid/awesome-ebpf

---
### Objetivos

- filtrar por PID
- comunicaciones de internet
- dumpcap
- hacer ping y ver el PID y extrapolar su comunicacion a wireshark viendo que hace (icmp)

- Cap 2: por que hace falta, dificultades, estadisticas, citas, autores
