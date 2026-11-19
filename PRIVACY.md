# Política de Privacidad — KestrelWOL

**Última actualización:** Noviembre de 2026  
**Desarrollador / Responsable:** Carlos Cruz

## 1. Principio Fundamental: Arquitectura "Zero-Data"
**KestrelWOL** opera bajo una arquitectura estrictamente **local-first y offline-first**. El desarrollador no recopila, almacena, transmite, vende ni procesa ningún dato personal, archivo, métrica de uso ni información técnica generada por el usuario.

## 2. Ausencia de Telemetría y Rastreadores
Esta aplicación:
* **No contiene telemetría** ni sistemas de registro de errores (*crash reporting*) que envíen información a servidores externos.
* **No utiliza cookies**, identificadores de publicidad ni herramientas de analítica de terceros.
* **No establece conexiones de red salientes ocultas** ni requiere cuentas en la nube. *(Nota: Si la herramienta ejecuta diagnósticos de red o consultas bajo demanda iniciadas explícitamente por el usuario, dichas peticiones se realizan directamente desde el dispositivo del usuario sin pasar por servidores intermediarios del desarrollador).*

## 3. Prohibición de Uso para Entrenamiento de IA
Ningún dato, texto, imagen, configuración o archivo procesado dentro de **KestrelWOL** es extraído ni utilizado para entrenar, ajustar (*fine-tuning*) o alimentar modelos de Inteligencia Artificial propios o de terceros. Todo procesamiento se ejecuta de forma aislada en el hardware local del usuario.

## 4. Almacenamiento y Control del Usuario
Todos los archivos de configuración, bases de datos locales, registros (*logs*) o exportaciones generadas se almacenan únicamente en el dispositivo local del usuario. El usuario conserva el control total y puede eliminarlos borrando los archivos locales o desinstalando la aplicación.

## 5. Cumplimiento Normativo (RGPD / LOPDGDD)
De conformidad con el Reglamento General de Protección de Datos de la Unión Europea (RGPD - Reglamento UE 2016/679) y la Ley Orgánica 3/2018 (LOPDGDD), al no existir recogida ni tratamiento de datos personales por parte del desarrollador, no se generan ficheros de datos bajo responsabilidad del autor.
