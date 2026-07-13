# Política de privacidad — Sentinel Suisse

**Versión:** 2026-07-13  
**Estado:** Proyecto personal / preproducción (borrador — revisión legal antes del lanzamiento público)

## 1. Responsable del tratamiento

Sentinel Suisse (proyecto personal)  
Contacto privacidad: privacy@sentinel-suisse.example *(sustituir antes de producción)*

## 2. Datos personales recopilados

| Dato | Finalidad |
|------|-----------|
| Correo electrónico | Cuenta de usuario, autenticación API, alertas por email |
| Dirección del canal (email o teléfono WhatsApp) | Envío de alertas por el canal elegido |
| Criterios de búsqueda guardados | Coincidencia con anuncios agregados |
| Registros de alertas (estado, marca temporal) | Prueba de envío, depuración — **sin contenido del mensaje** |

Los anuncios agregados provienen de fuentes públicas de terceros; no almacenamos datos sensibles en el cuerpo de las alertas.

## 3. Base legal (nLPD / RGPD aplicable)

- **Servicio de alertas:** ejecución del contrato / interés legítimo, con consentimiento explícito (registro y verificación del canal).
- **Agregación de anuncios:** datos públicos de terceros; enlace al anuncio original.

## 4. Plazo de conservación

| Dato | Plazo |
|------|-------|
| Cuenta y canales | Hasta eliminación de la cuenta |
| Búsquedas guardadas | Hasta eliminación por el usuario o con la cuenta |
| `raw_payload` de anuncios | 30 días como máximo (tarea de mantenimiento automática) |
| Registros de alertas | Eliminados en cascada con la cuenta |

## 5. Seguridad

- Cifrado en reposo (Fernet) para email y direcciones de canal.
- Contraseñas de admin con hash (bcrypt); claves API con hash — nunca en texto plano.
- API interna limitada a `127.0.0.1` en fase de desarrollo.

## 6. Encargados y transferencias

Según configuración: proveedor SMTP (p. ej. Mailtrap en desarrollo), WhatsApp Cloud API (Meta), hosting de base de datos. No se prevén transferencias fuera de Suiza/EEE sin información previa.

## 7. Sus derechos

Conforme a la nLPD, dispone de derechos de **acceso**, **rectificación** y **supresión**.

**Eliminación de cuenta (derecho al olvido):**

```http
DELETE /api/v1/users/me
X-API-Key: <su clave API>
```

La eliminación es **definitiva** y suprime en cascada canales, búsquedas guardadas y registros de alertas asociados.

Consultas: privacy@sentinel-suisse.example

## 8. Cambios

Esta política puede actualizarse; la versión y la fecha figuran al inicio y en la API `GET /api/v1/legal/privacy?lang=es`.
