# Ejemplos de Configuración y Plantillas

Esta carpeta contiene archivos de referencia y plantillas de ejemplo para configurar y alimentar **KestrelWOL**:

---

## 📁 Archivos Disponibles

1. **`machines.example.json`**:
   - Plantilla base de configuración de equipos en formato JSON.
   - Si deseas iniciar con una configuración predefinida, copia este archivo como `data/machines.json`.

2. **`ignored.example.json`**:
   - Lista de IPs o dispositivos excluidos del escáner pasivo de red (por ejemplo routers, impresoras, switches gestionables).
   - Puedes copiarlo como `data/ignored.json`.

3. **`inventario.example.csv`**:
   - Plantilla formateada para la **importación masiva mediante CSV / Excel**.
   - Admite columnas: `name`, `ip`, `mac`, `zone`, `schedule_enabled`, `schedule_time`, `schedule_days`.
   - Se puede importar directamente con el botón **[📥 Importar CSV]** de la barra superior.
