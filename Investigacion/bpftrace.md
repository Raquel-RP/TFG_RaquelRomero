## Tutorial bpftrace 
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
