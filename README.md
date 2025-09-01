# 🧪 IA-Ops Veritas - Testing & Quality Assurance Platform

Plataforma completa de testing y aseguramiento de calidad para el ecosistema IA-Ops.

## 🚀 Servicios Incluidos

- **🧪 Test Manager** (8870) - Gestión de casos de prueba
- **📊 Test Execution Engine** (8871) - Motor de ejecución de pruebas
- **📈 Quality Analytics** (8872) - Análisis de calidad y métricas
- **🔍 Evidence Manager** (8873) - Gestión de evidencias y reportes

## 🌐 URLs de Acceso

- **Test Manager**: http://localhost:8870
- **Test Execution Engine**: http://localhost:8871
- **Quality Analytics**: http://localhost:8872
- **Evidence Manager**: http://localhost:8873

## 🏗️ Integración con Ecosistema IA-Ops

### Conexiones
- **ia-ops-dev-core**: APIs de repositorios, tareas y logs
- **ia-ops-minio**: Almacenamiento de evidencias y reportes
- **ia-ops-docs**: Portal principal de gestión

### Flujo de Testing
```
Portal (8845) → Veritas (8870-8873) → Dev Core (8860-8865) → MinIO (9898/9899)
```

## 🛠️ Instalación Rápida

```bash
# 1. Clonar repositorio
git clone git@github.com:giovanemere/ia-ops-veritas.git
cd ia-ops-veritas

# 2. Configurar entorno
cp docker/.env.example docker/.env

# 3. Iniciar servicios
./scripts/start.sh

# 4. Verificar servicios
./scripts/status.sh
```

## 📊 Características

### Test Manager (8870)
- Gestión CRUD de casos de prueba
- Organización por suites y categorías
- Integración con repositorios de código
- API REST completa

### Test Execution Engine (8871)
- Ejecución automática de pruebas
- Soporte para múltiples frameworks
- Paralelización de ejecución
- Reportes en tiempo real

### Quality Analytics (8872)
- Métricas de calidad de código
- Análisis de cobertura
- Tendencias históricas
- Dashboard de métricas

### Evidence Manager (8873)
- Almacenamiento de evidencias
- Generación de reportes
- Integración con MinIO
- Exportación de resultados

## 🔧 Comandos Rápidos

```bash
# Iniciar todos los servicios
./scripts/start.sh

# Detener servicios
./scripts/stop.sh

# Ver estado
./scripts/status.sh

# Ver logs
./scripts/logs.sh
```

## 🔗 Integración con Otros Servicios

### Dev Core Integration
- Sincronización con repositorios
- Ejecución de pruebas en builds
- Logs centralizados

### MinIO Integration
- Almacenamiento de evidencias
- Reportes persistentes
- Archivos de configuración

### Portal Integration
- Dashboard unificado
- Gestión desde portal principal
- APIs proxy integradas

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

---

**🧪 Parte del ecosistema IA-Ops - Testing & Quality Assurance**
