# 🧪 IA-Ops Veritas - Unified Testing & Quality Assurance Platform

Plataforma unificada de testing y aseguramiento de calidad para el ecosistema IA-Ops, optimizada para máximo rendimiento con todos los servicios en un solo contenedor.

## 🚀 Arquitectura Unificada

**Veritas Unified Service** (Puerto 8869) - Todos los servicios integrados:
- 🏠 **Main Portal** - Dashboard principal unificado
- 🧪 **Test Manager** - Gestión de casos de prueba
- ⚡ **Test Execution Engine** - Motor de ejecución de pruebas
- 📈 **Quality Analytics** - Análisis de calidad y métricas
- 📋 **Evidence Manager** - Gestión de evidencias y reportes
- 📊 **Test Results Viewer** - Visualización de resultados

## 🌐 URLs de Acceso

- **🏠 Main Portal**: http://localhost:8869 (Portal unificado)
- **📊 MinIO Console**: http://localhost:9899 (Gestión de archivos)

## 🗂️ Almacenamiento Organizado por Proyectos

### Estructura en MinIO (veritas-projects):
```
├── projects/           # Proyectos de testing
│   └── {project-name}/
│       ├── tests/      # Casos de prueba
│       ├── evidence/   # Evidencias de ejecución
│       ├── reports/    # Reportes generados
│       └── config.json # Configuración del proyecto
├── templates/          # Plantillas reutilizables
│   ├── test-cases/     # Plantillas de casos de prueba
│   └── reports/        # Plantillas de reportes
├── shared/             # Recursos compartidos
│   ├── assets/         # Assets comunes
│   └── configs/        # Configuraciones compartidas
├── archives/           # Proyectos archivados
│   └── completed-projects/
└── temp/               # Archivos temporales
    └── uploads/        # Área de subida temporal
```

## 🛠️ Instalación y Uso

### Inicio Rápido
```bash
# 1. Clonar repositorio
git clone git@github.com:giovanemere/ia-ops-veritas.git
cd ia-ops-veritas

# 2. Iniciar servicio unificado
./scripts/start-unified.sh

# 3. Verificar estado
./scripts/show-status.sh
```

### Comandos de Gestión
```bash
# Iniciar servicio unificado
./scripts/start-unified.sh

# Ver estado del sistema
./scripts/show-status.sh

# Ver logs en tiempo real
docker logs iaops-veritas-unified -f

# Detener servicio
docker-compose -f docker/docker-compose.unified.yml down

# Reiniciar servicio
./scripts/start-unified.sh
```

## 🔗 Integración con Servicios Existentes

### Base de Datos PostgreSQL
- **Host**: localhost:5432
- **Database**: veritas_db
- **User**: veritas_user
- **Password**: veritas_pass

### Redis Cache
- **Host**: localhost:6379
- **Uso**: Cache de configuración y sesiones

### MinIO Storage
- **Endpoint**: http://localhost:9898
- **Console**: http://localhost:9899
- **Credentials**: minioadmin / minioadmin123
- **Bucket**: veritas-projects

## 📊 Características del Servicio Unificado

### Ventajas de la Arquitectura Unificada:
- ✅ **Mejor Rendimiento**: Sin latencia entre servicios
- ✅ **Menor Uso de Recursos**: Un solo contenedor vs múltiples
- ✅ **Gestión Simplificada**: Un solo punto de control
- ✅ **Configuración Centralizada**: Variables de entorno unificadas
- ✅ **Logs Centralizados**: Un solo log stream
- ✅ **Despliegue Rápido**: Inicio más rápido del sistema

### APIs Disponibles:
- `GET /api/stats` - Estadísticas del sistema
- `GET /api/projects` - Listar proyectos
- `POST /api/projects` - Crear proyecto
- `GET /api/tests` - Listar casos de prueba
- `POST /api/tests` - Crear caso de prueba
- `GET /api/executions` - Listar ejecuciones
- `POST /api/executions` - Ejecutar prueba
- `GET /api/evidence` - Listar evidencias
- `GET /health` - Health check del sistema

## 🔧 Configuración Avanzada

### Variables de Entorno:
```bash
# Base de datos
POSTGRES_HOST=host.docker.internal
POSTGRES_DB=veritas_db
POSTGRES_USER=veritas_user
POSTGRES_PASSWORD=veritas_pass

# Redis
REDIS_HOST=host.docker.internal
REDIS_PORT=6379

# MinIO
MINIO_ENDPOINT=host.docker.internal:9898
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET=veritas-projects
```

## 🚦 Monitoreo y Salud

### Health Check:
```bash
curl http://localhost:8869/health
```

### Estadísticas:
```bash
curl http://localhost:8869/api/stats
```

### Logs:
```bash
docker logs iaops-veritas-unified -f
```

## 📁 Gestión de Archivos

### Acceso a MinIO Console:
1. Abrir http://localhost:9899
2. Login: minioadmin / minioadmin123
3. Navegar al bucket `veritas-projects`
4. Explorar la estructura organizada por proyectos

### Organización Automática:
- Los archivos se organizan automáticamente por proyecto
- Estructura de fechas para evidencias: `YYYY/MM/DD`
- Separación clara entre tests, evidencias y reportes

## 🔄 Migración desde Servicios Separados

Si tenías servicios separados anteriormente:
1. Los datos se mantienen en la misma base de datos
2. Los archivos en MinIO se reorganizan automáticamente
3. No se pierde información existente
4. Mejor rendimiento con la nueva arquitectura

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

---

**🧪 Parte del ecosistema IA-Ops - Testing & Quality Assurance**

> 💡 **Tip**: La arquitectura unificada proporciona mejor rendimiento y gestión simplificada comparada con servicios separados.

> 🎯 **Acceso Directo**: http://localhost:8869 para el portal principal y http://localhost:9899 para gestión de archivos.
