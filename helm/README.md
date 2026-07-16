# Django Blog Helm Chart

Este Helm Chart permite desplegar la aplicación de Django + Ninja en un clúster de Kubernetes, incluyendo de manera opcional una base de datos PostgreSQL como sub-chart (utilizando la imagen oficial de Bitnami).

## Estructura del Chart

- **Templates**:
  - `deployment.yaml`: Despliegue de los pods de Django API (con replicas autocalculadas o autoscaling).
  - `service.yaml` e `ingress.yaml`: Exposición del servicio.
  - `configmap.yaml` y `secrets.yaml`: Variables de entorno y secretos del sistema.
  - `job-migrate.yaml`: Un **Helm Hook** (`pre-install` / `pre-upgrade`) que ejecuta automáticamente las migraciones de Django (`python manage.py migrate`) y opcionalmente el seeding (`python manage.py seed`) antes de que el nuevo despliegue comience, garantizando cero downtime y una base de datos lista. Este Job incluye un `initContainer` inteligente que espera a que la base de datos esté lista antes de proceder.
  - `hpa.yaml`: Horizontal Pod Autoscaler (deshabilitado por defecto).
  - `serviceaccount.yaml`: Service Account para los pods.

## Requisitos Previos

1. Tener configurado e instalado **Helm** (v3+).
2. Tener acceso a un clúster de Kubernetes (`kubectl`).
3. (Opcional) Si deseas compilar las dependencias localmente, puedes correr:
   ```bash
   helm dependency update ./helm
   ```

## Configuración y Despliegue

### 1. Despliegue con Base de Datos PostgreSQL integrada (Sub-chart)

Por defecto, el chart viene configurado con `postgresql.enabled: true`. Esto desplegará automáticamente PostgreSQL en tu clúster.

Para instalar el chart:
```bash
helm install django-blog ./helm
```

### 2. Despliegue con Base de Datos Externa

Si ya tienes un servidor de base de datos PostgreSQL y no quieres que Helm cree uno nuevo:

1. Configura `postgresql.enabled: false` en tu archivo `values.yaml` o mediante la línea de comando.
2. Rellena los datos de tu base de datos en la sección `externalDatabase` en `values.yaml`.

Ejemplo de comando de instalación:
```bash
helm install django-blog ./helm \
  --set postgresql.enabled=false \
  --set externalDatabase.host="db.example.com" \
  --set externalDatabase.username="mi_usuario" \
  --set externalDatabase.password="mi_password" \
  --set externalDatabase.database="mi_db"
```

## Configuración Importante (`values.yaml`)

| Parámetro | Descripción | Por defecto |
|-----------|-------------|-------------|
| `replicaCount` | Número de pods para el backend | `2` |
| `image.repository` | Imagen Docker del backend | `django-blog` |
| `django.debug` | Activar/Desactivar modo DEBUG en Django | `"false"` |
| `django.secretKey` | Secret key de producción para Django | *(Una por defecto, cambiar en producción)* |
| `django.runMigrations` | Ejecutar migraciones automáticamente | `true` |
| `django.seedData` | Sembrar datos iniciales (ideal para demo/dev) | `true` |
| `postgresql.enabled` | Desplegar Postgres como parte del release | `true` |
