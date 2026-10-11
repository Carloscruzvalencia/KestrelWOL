# Guía: Conexión RDP sin Bloquear la Pantalla Física (100% Nativo de Windows)

Esta guía explica cómo controlar un ordenador remoto por **Escritorio Remoto de Windows (RDP)** **sin que se bloquee la pantalla local**, utilizando exclusivamente las herramientas nativas del sistema operativo **sin necesidad de instalar software adicional de terceros**.

---

## 📌 ¿Por qué Windows bloquea la pantalla por defecto?

Por diseño y políticas de licencia de Microsoft en Windows 10 y Windows 11 (ediciones Pro y Enterprise):
* El sistema solo permite **una sesión interactiva de usuario activa** a la vez.
* Al iniciar una conexión RDP estándar (`mstsc /v:IP`), Windows traslada la interfaz gráfica a la red y **bloquea la pantalla física** por privacidad (mostrando la pantalla de inicio de sesión de Windows con *"Otro usuario ha iniciado sesión"*).
* Al desconectarte del RDP estándar, la máquina remota permanece en la pantalla de bloqueo.

A continuación se presentan los **dos métodos oficiales y nativos** para solucionar ambos escenarios.

---

## 🚀 Método 1: RDP Shadowing (Modo Sombra Nativo)

El **Modo Sombra (Session Shadowing)** es una función integrada en Windows que permite unirse a la sesión de consola física activa en tiempo real. 

### Ventajas:
* ✅ **No instala nada**: Utiliza componentes ya presentes en Windows.
* ✅ **Pantalla física activa**: Lo que haces se ve tanto en tu pantalla como en el monitor físico del otro ordenador al mismo tiempo.
* ✅ **Control total**: Permite mover el ratón y escribir en el teclado de forma compartida.

---

### Paso 1: Configurar el ordenador remoto (Solo se hace una vez)

Debes permitir que Windows acepte conexiones en modo sombra sin solicitar confirmación manual al usuario:

#### Opción A — Desde el Editor de Directivas de Grupo (Recomendado):
1. En el ordenador remoto, presiona `Win + R`, escribe `gpedit.msc` y pulsa **Enter**.
2. Navega por el árbol de la izquierda hasta la siguiente ruta:
   ```text
   Configuración del equipo
     └── Plantillas administrativas
           └── Componentes de Windows
                 └── Servicios de Escritorio remoto
                       └── Host de sesión de Escritorio remoto
                             └── Conexiones
   ```
3. En el panel derecho, haz doble clic en la directiva:
   **"Establecer reglas para el control remoto de sesiones de usuario de Servicios de Escritorio remoto"**.
4. Selecciona la opción **Habilitada**.
5. En el menú desplegable *Opciones*, selecciona:
   **"Control total sin el permiso del usuario"**.
6. Haz clic en **Aplicar** y **Aceptar**.

#### Opción B — Mediante símbolo del sistema como Administrador:
Abre **PowerShell** o **CMD** como Administrador en el equipo remoto y ejecuta:
```cmd
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services" /v Shadow /t REG_DWORD /d 2 /f
```
*(El valor `2` corresponde a Control total sin requerir consentimiento).*

---

### Paso 2: Conectarte desde tu ordenador

Desde tu equipo, puedes conectarte directamente a la sesión activa mediante la terminal o creando un archivo `.bat`:

1. Abre **CMD** o **PowerShell** y ejecuta:
   ```cmd
   mstsc /v:IP_DEL_EQUIPO /shadow:1 /control /noConsentPrompt
   ```
   *(Sustituye `IP_DEL_EQUIPO` por la IP local del equipo, por ejemplo `192.168.1.50`).*

> [!NOTE]
> En la mayoría de equipos con Windows, el identificador de la pantalla física (sesión de consola) es `1`.  
> Si te indica que la sesión no existe, puedes averiguar el número exacto ejecutando en la consola:
> ```cmd
> qwinsta /server:IP_DEL_EQUIPO
> ```
> y ver el número que figura junto a la fila `console`.

---

## 🔄 Método 2: Desconectar RDP normal sin dejar el equipo bloqueado

Si prefieres seguir usando la conexión RDP clásica de un solo clic, el problema habitual es que **al cerrar la ventana de RDP, el ordenador remoto queda bloqueado**.

Para cerrar la sesión RDP y **devolver la pantalla inmediatamente al escritorio físico desbloqueado**:

### Paso 1: Crear el script de salida en el equipo remoto
1. En el **ordenador remoto**, abre el Bloc de notas y pega esta línea:
   ```cmd
   for /f "skip=1 tokens=3" %%s in ('query user %USERNAME%') do tscon %%s /dest:console
   ```
2. Guarda el archivo en el escritorio remoto con el nombre:
   `Desconectar_Sin_Bloqueo.bat`

### Paso 2: Crear acceso directo con permisos de Administrador
El comando `tscon.exe` requiere privilegios elevados:
1. Haz clic derecho sobre `Desconectar_Sin_Bloqueo.bat` ➔ **Crear acceso directo**.
2. Haz clic derecho en el acceso directo ➔ **Propiedades**.
3. En la pestaña *Acceso directo*, pulsa en **Opciones avanzadas...**.
4. Marca la casilla **"Ejecutar como administrador"** y pulsa **Aceptar**.

### ¿Cómo se usa?
Cuando termines de trabajar por RDP en el equipo remoto, **en lugar de cerrar la ventana con la cruz (✕)**, haz doble clic en el acceso directo del escritorio.
* La ventana RDP se cerrará automáticamente en tu pantalla.
* La sesión se transferirá de inmediato al monitor físico del ordenador remoto, **quedando el escritorio abierto y desbloqueado**.

---

## 🛡️ Verificación de Firewall de Windows

Si la conexión no responde, asegúrate de que el Firewall de Windows en el equipo remoto permite el tráfico de Escritorio Remoto:

Ejecuta en PowerShell como Administrador en el equipo remoto:
```powershell
Enable-NetFirewallRule -DisplayGroup "Escritorio remoto"
```
O en sistemas en inglés:
```powershell
Enable-NetFirewallRule -DisplayGroup "Remote Desktop"
```

---

## 📋 Resumen Rápido

| Objetivo | Solución Nativa | Comando / Herramienta |
| :--- | :--- | :--- |
| **Controlar el PC viendo la pantalla física a la vez** | RDP Shadowing | `mstsc /v:IP /shadow:1 /control /noConsentPrompt` |
| **Salir de RDP dejando el escritorio abierto** | Transferencia a Consola | `tscon <ID> /dest:console` |
| **Permisos de Shadowing sin aviso** | Directiva de Grupo (GPO) | `gpedit.msc` ➔ Directiva de Control Remoto de Sesiones |
