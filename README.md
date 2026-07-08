# CPU-ISA-Runtime-Check

## Installation

1. Ten Python 3 disponible en `PATH` o en `python/python.exe` dentro del proyecto.
2. Ten PHP disponible en `PATH` o en `php/php.exe` dentro del proyecto.
3. Ejecuta `lanzar_diagnostico_cpu.bat`.

## Requirements

- Windows x64
- Python 3
- PHP
- `py-cpuinfo` opcional para ampliar la deteccion por flags

## Origen del proyecto

Este proyecto nació como una herramienta personal para investigar las capacidades reales de ejecución de distintas extensiones ISA en procesadores x86.

Originalmente solo necesitaba comprobar si determinadas instrucciones podían ejecutarse correctamente en distintos entornos (máquinas virtuales, servidores web y equipos físicos). Mientras desarrollaba esa pequeña utilidad fueron apareciendo nuevas ideas y, en el transcurso del mismo desarrollo, terminó convirtiéndose en una colección de pruebas de ejecución para distintas tecnologías ISA.

Decidí publicarlo porque pensé que podía resultar útil para otras personas interesadas en este tipo de diagnósticos o como base para proyectos similares, ya que no encontré ninguna herramienta que abordara exactamente este enfoque (aunque tampoco realicé una búsqueda exhaustiva).

Planeo reorganizar el código en futuras versiones para separar mejor los distintos componentes del proyecto. Aun así, decidí publicar esta primera versión antes de esa reestructuración por si a alguien le resulta más útil partir desde una implementación sencilla y directa que desde una arquitectura más elaborada.

---

# Funcionamiento

Actualmente el proyecto compara distintas fuentes de información sobre las capacidades del procesador y las complementa con pruebas de ejecución reales.

En términos simples:

- `probe_cpu.py` informa lo que el sistema operativo y otras fuentes reportan.
- `runtime_feature_tests.py` intenta ejecutar instrucciones representativas de cada tecnología ISA.
- `index.php` reúne toda la información y la presenta en una única interfaz.

---

## Flujo actual

### Archivos principales

- `lanzar_diagnostico_cpu.bat`: levanta el servidor PHP local y abre la página.
- `index.php`: página principal y orquestador web.
- `probe_cpu.py`: recopila información general del sistema, Windows Processor Features y datos provenientes de `py-cpuinfo`.
- `isa_runtime_test.py`: ejecuta las pruebas ISA en procesos independientes y consolida los resultados.
- `runtime_feature_tests.py`: contiene una función por tecnología; algunas ejecutan código máquina y otras devuelven `NO PROBADO`.

### Flujo de ejecución

1. El usuario inicia la aplicación mediante `lanzar_diagnostico_cpu.bat`.
2. `index.php` localiza una instalación válida de Python.
3. `index.php` ejecuta `probe_cpu.py` y recibe un bloque JSON con la información del sistema.
4. `index.php` ejecuta `isa_runtime_test.py --json`.
5. `isa_runtime_test.py` recorre todas las tecnologías soportadas.
6. Cada tecnología se ejecuta en un proceso hijo independiente.
7. Cada proceso invoca la función correspondiente en `runtime_feature_tests.py`.
8. La prueba devuelve `OK`, `NO PROBADO` o finaliza debido a una excepción producida por la ejecución de la instrucción.
9. `isa_runtime_test.py` consolida todos los resultados y devuelve un único JSON.
10. `index.php` construye la tabla final comparando la información reportada por cada fuente.

---

# Generación del código máquina

Las secuencias de código máquina incluidas en `runtime_feature_tests.py` no fueron escritas manualmente.

Cada prueba fue desarrollada originalmente en ensamblador, ensamblada mediante NASM y posteriormente convertida al formato hexadecimal utilizado por el proyecto.

Durante el desarrollo se aplican dos verificaciones distintas de roundtrip, no solo una:

```
Assembly
    ↓
NASM
    ↓
Código máquina
    ↓
NDISASM
    ↓
Assembly
    ↓
NASM
    ↓
Código máquina
```

**Verificación 1 — roundtrip binario:** se comprueba que el código máquina (A) y el código máquina (B) sean idénticos byte a byte. Esto confirma que el ciclo completo es autoconsistente: NASM no reinterpretó de forma ambigua lo que `ndisasm` produjo.

**Verificación 2 — roundtrip de mnemonic:** se compara el assembly escrito originalmente contra el assembly recuperado por `ndisasm`. Esta verificación busca detectar el caso en que NASM elija silenciosamente una codificación alternativa distinta a la escrita (por ejemplo, promover una instrucción legacy a su forma VEX), lo cual pasaría la Verificación 1 sin ser detectado, ya que esta solo confirma consistencia interna del ciclo, no que la codificación elegida sea la que se pretendía escribir.

Adicionalmente, se ensambla con la bandera `-O0` para desactivar el optimizador de NASM, evitando que sustituya automáticamente una instrucción por una forma alternativa más corta.

La generación y verificación fueron realizadas utilizando:

- NASM 3.02
- NDISASM 3.02
---

# Advertencias

Este proyecto ejecuta código máquina nativo.

Cada prueba se ejecuta en un proceso independiente para aislar fallos producidos por instrucciones no soportadas o por otras excepciones durante la ejecución.

Aunque las pruebas han sido escritas para ser lo más pequeñas posible, este software debe ejecutarse únicamente en sistemas de confianza y bajo responsabilidad del usuario.

Algunas tecnologías (por ejemplo, AMX) dependen no solo del hardware, sino también del soporte del sistema operativo. Un fallo en la prueba no implica necesariamente que el procesador carezca de dicha extensión.

Como caso límite, algunas tecnologías requieren estructuras de datos o configuraciones auxiliares antes de poder ejecutar la instrucción representativa. Dichas estructuras son construidas por el propio proyecto antes de realizar la prueba. Si la preparación de ese entorno falla por cualquier motivo, el resultado podrá interpretarse como un fallo de la tecnología, produciendo un falso negativo.

---

# Trabajo futuro

Actualmente la mayoría de las pruebas verifican que una instrucción representativa de cada tecnología pueda ejecutarse correctamente sin producir una excepción.

Como siguiente etapa del proyecto, planeo ampliar estas pruebas para verificar también el comportamiento funcional de las instrucciones. La idea es ejecutar cada tecnología sobre datos de entrada conocidos y comprobar que el resultado obtenido coincida con el esperado.

En otras palabras, el objetivo es evolucionar desde una validación de **"la instrucción puede ejecutarse"** hacia una validación de **"la instrucción produce el resultado correcto"**.

No todas las tecnologías pueden verificarse de esta forma con una única instrucción representativa, por lo que esta ampliación se realizará progresivamente y caso por caso.

Eventualmente seria ideal llegar a un caso en que el generate que actualmente es solo una herramienta aparte, generara el archivo runtime_feature_tests.py completo para no editar manualmente el archivo con lenguaje de maquina, por ahora solo se copia y pega.