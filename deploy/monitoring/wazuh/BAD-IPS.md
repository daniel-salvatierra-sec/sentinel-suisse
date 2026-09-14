# Lista negra LinkSwiss (`linkswiss-bad-ips`)

IPs **reincidentes** que ya viste en Wazuh (varios intentos SSH / scans).  
No sustituye el ban automático de 1 h: esto es **extra** (7 días por intento).

## Nunca añadas

- `63.178.67.83` (tu casa)
- `100.82.114.60` / `100.95.7.14` (Tailscale manager / VPS)
- IPs de Cloudflare/CDN si algún día proxy delante

## Instalación (una vez, en el manager VirtualBox)

```bash
sudo cp /var/ossec/etc/rules/local_rules.xml /var/ossec/etc/rules/local_rules.xml.bak-badips
sudo nano /var/ossec/etc/rules/local_rules.xml
```

Dentro del `<group name="linkswiss,">`, añade la regla **100830** (copia desde el repo  
`deploy/monitoring/wazuh/local_rules.xml`).

Crea la lista:

```bash
sudo touch /var/ossec/etc/lists/linkswiss-bad-ips
sudo chown root:wazuh /var/ossec/etc/lists/linkswiss-bad-ips
sudo chmod 640 /var/ossec/etc/lists/linkswiss-bad-ips
```

En `/var/ossec/etc/ossec.conf`, dentro de `<ruleset>`, junto a las otras `<list>`:

```xml
    <list>etc/lists/linkswiss-bad-ips</list>
```

Active response (después del bloque SSH de 1 h):

```xml
  <active-response>
    <command>firewall-drop</command>
    <location>local</location>
    <rules_id>100830</rules_id>
    <timeout>604800</timeout>
  </active-response>
```

`604800` = **7 días** por cada intento desde una IP listada.

Reinicia:

```bash
sudo systemctl restart wazuh-manager
sudo systemctl is-active wazuh-manager
```

## Añadir una IP mala

Formato CDB Wazuh: **`IP:`** (con dos puntos) por línea. Sin comentarios en el `.cdb` fuente.

```bash
sudo nano /var/ossec/etc/lists/linkswiss-bad-ips
```

Ejemplo (solo cuando estés seguro):

```
0.0.0.0:
203.0.113.50:
198.51.100.22:
```

Tras editar, **compila** la lista y reinicia:

```bash
sudo /var/ossec/bin/wazuh-makelists
sudo systemctl restart wazuh-manager
```

O con el script del repo:

```bash
sudo bash /path/to/add-bad-ip.sh 203.0.113.50
```

## Quitar una IP (error tuyo)

```bash
sudo nano /var/ossec/etc/lists/linkswiss-bad-ips
# borra la línea
sudo systemctl restart wazuh-manager
```

En el VPS LinkSwiss, si sigue bloqueada en iptables, espera a que expire el ban  
o revisa `sudo tail /var/ossec/logs/active-responses.log`.

## Flujo recomendado

1. Primera vez → ban 1 h automático (reglas 5710…), **no** añadas a la lista.
2. Misma IP varias veces en días → añade a `linkswiss-bad-ips`.
3. Siguiente intento SSH → alerta **100830** + ban **7 días**.
