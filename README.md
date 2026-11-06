# TurnoFácil — primera entrega

Proyecto académico para modelar un flujo frecuente en un negocio de servicios: registrar una cita y dejar constancia de una notificación simulada. Esta entrega se centra en dos APIs independientes que se ejecutan conectadas mediante Docker Compose.

## Alcance de esta entrega

- `api-agenda`: crea, lista y consulta reservas, con persistencia SQLite.
- `servicio-notificaciones`: recibe la solicitud interna y registra un mensaje simulado en SQLite.
- `compose.yaml`: construye y conecta los servicios; publica los puertos 8000 y 8001 y declara volúmenes persistentes.
- No se envían correos reales ni se incluyen aquí automatizaciones de CI de fases posteriores.

## Inicio local

Se requiere Docker Desktop con Docker Compose. Desde la raíz:

```bash
docker compose up --build
```

- Agenda: http://localhost:8000/docs
- Notificaciones: http://localhost:8001/docs
- Salud: `http://localhost:8000/health` y `http://localhost:8001/health`

Crea una reserva desde la interfaz OpenAPI de la agenda (`POST /reservations`) y consulta el resultado simulado con `GET /notifications` en el servicio de notificaciones. Para detener los servicios: `docker compose down`.

## Estructura

```text
api-agenda/                 API de reservas
servicio-notificaciones/    API de avisos simulados
compose.yaml                Orquestación local
entregas/                   Informe APA de la primera entrega
```

## Documento académico

[Informe de la primera entrega (DOCX)](entregas/entrega-1-turnofacil-apa.docx)

## Referencia del repositorio

https://github.com/imbryandev/turnofacil-primera-entrega
