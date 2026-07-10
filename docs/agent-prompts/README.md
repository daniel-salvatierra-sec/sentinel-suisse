# Prompts de agente por fase

Cada fase tiene un archivo `fase-N.md` con instrucciones de seguridad explícitas para el agente de IA.

| Fase | Archivo | Estado |
|------|---------|--------|
| 0 | Entorno seguro | Completada |
| 1 | Modelo de datos | Pendiente |
| 2 | CRUD interno | Pendiente |
| 3 | Ingesta | Pendiente |
| 4 | Búsqueda + preferencias | Pendiente |
| 5 | Alertas WhatsApp | Pendiente |

**Regla:** el agente nunca ve credenciales reales. Usar `os.getenv()` y `.env.example` como referencia.
