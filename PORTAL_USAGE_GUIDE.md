# 🧪 IA-Ops Veritas - Guía Completa de Uso del Portal

## 🌐 **Portal Desplegado y Funcionando**

### 📊 **Servicios Activos**
- ✅ **Unified Portal**: http://localhost:8876 *(PUNTO DE ENTRADA PRINCIPAL)*
- ✅ **Test Results Viewer**: http://localhost:8877
- ✅ **Project Manager**: http://localhost:8874
- ✅ **Repository Analyzer**: http://localhost:8875
- ✅ **Test Manager**: http://localhost:8870
- ✅ **Execution Engine**: http://localhost:8871
- ✅ **Quality Analytics**: http://localhost:8872
- ✅ **Evidence Manager**: http://localhost:8873
- ✅ **Veritas Portal**: http://localhost:8869
- ✅ **MinIO**: http://localhost:9898
- ✅ **PostgreSQL**: localhost:5432
- ✅ **Redis**: localhost:6379

---

## 🚀 **CÓMO USAR EL PORTAL PASO A PASO**

### **1. Acceso Principal**
```
👉 Abrir: http://localhost:8876
```
Este es tu **Portal Unificado** donde tienes acceso a todos los servicios.

### **2. Navegación del Portal**

#### **🏠 Dashboard Principal**
- **Ubicación**: Página de inicio del portal
- **Funciones**:
  - Ver estadísticas generales (proyectos, tests, ejecuciones)
  - Acciones rápidas (crear proyecto, generar reportes)
  - Reportes recientes de pruebas
  - Health check de servicios

#### **📱 Sidebar de Navegación**
El sidebar izquierdo contiene todas las secciones:

**Dashboard**
- 🏠 Overview - Vista general del sistema

**Project Management**
- 📊 Project Manager - Gestión de proyectos
- 🔍 Repository Analyzer - Análisis de repositorios

**Testing Services**
- 🧪 Test Manager - Gestión de casos de prueba
- ⚡ Execution Engine - Motor de ejecución
- 📈 Quality Analytics - Análisis de calidad
- 📋 Evidence Manager - Gestión de evidencias

**Reports & Results**
- 📊 Test Results Viewer - Visor de resultados HTML
- 🗂️ MinIO Reports - Reportes almacenados

**External**
- 🔧 MinIO Console - Consola de administración

---

## 📋 **FLUJO DE TRABAJO COMPLETO**

### **Paso 1: Crear un Proyecto**
1. En el **Dashboard**, click "📊 New Project"
2. O ir a **Project Manager** en sidebar
3. Click "+ Nuevo Proyecto"
4. Llenar formulario:
   - **Nombre**: Nombre del proyecto
   - **Repository URL**: URL del repositorio Git
   - **Descripción**: Descripción del proyecto
5. Click "Crear Proyecto"

### **Paso 2: Analizar Repositorio**
1. En **Project Manager**, click "🔍 Analizar" en un proyecto
2. O ir directamente a **Repository Analyzer**
3. El sistema analizará el código y generará:
   - Historias de usuario automáticas
   - Planes de prueba
   - Casos de prueba sugeridos

### **Paso 3: Gestionar Tests**
1. Ir a **Test Manager** en sidebar
2. Ver casos de prueba generados
3. Crear nuevos casos manualmente si es necesario
4. Organizar en suites de prueba

### **Paso 4: Ejecutar Pruebas**
1. Ir a **Execution Engine**
2. Seleccionar proyecto y casos de prueba
3. Configurar parámetros de ejecución
4. Iniciar ejecución

### **Paso 5: Ver Resultados**
1. Ir a **Test Results Viewer**
2. Ver reportes HTML generados automáticamente
3. O generar reporte de muestra desde Dashboard
4. Los reportes incluyen:
   - Métricas de ejecución (total, passed, failed, pass rate)
   - Detalles de cada caso de prueba
   - Duración y mensajes de error
   - Cobertura de código

### **Paso 6: Análisis de Calidad**
1. Ir a **Quality Analytics**
2. Ver métricas de calidad del código
3. Análisis de tendencias
4. Reportes de cobertura

---

## 🎯 **FUNCIONES PRINCIPALES**

### **📊 Generación de Reportes**
- **Desde Dashboard**: Click "📊 Generate Sample Report"
- **Automático**: Los reportes se generan tras cada ejecución
- **Formato**: HTML profesional con métricas completas
- **Almacenamiento**: MinIO para persistencia

### **🔍 Test Results Viewer**
- **Acceso**: Sidebar > Test Results Viewer
- **Funciones**:
  - Lista de todos los reportes disponibles
  - Visualización HTML profesional
  - Métricas detalladas por test case
  - Exportación y compartición

### **📈 Analytics y Métricas**
- **Dashboard**: Estadísticas en tiempo real
- **Quality Analytics**: Métricas de calidad profundas
- **Tendencias**: Análisis histórico de ejecuciones

### **🗂️ Gestión de Archivos**
- **MinIO Integration**: Almacenamiento de reportes y evidencias
- **Console**: http://localhost:9899 (minioadmin/minioadmin)
- **Buckets**: Organización automática por proyecto

---

## 🔧 **CARACTERÍSTICAS TÉCNICAS**

### **🎨 Diseño Unificado**
- **CSS Centralizado**: Diseño consistente en todos los servicios
- **Responsive**: Funciona en desktop y móvil
- **Dark Theme**: Sidebar oscuro profesional
- **Navegación Fluida**: Sin recargas de página

### **⚡ Performance**
- **Redis Cache**: Cache de datos para velocidad
- **PostgreSQL**: Base de datos robusta
- **MinIO**: Almacenamiento escalable de archivos

### **🔗 Integración**
- **API Unificada**: Backend centralizado
- **Microservicios**: Arquitectura modular
- **Health Checks**: Monitoreo automático

---

## 📱 **ACCESOS RÁPIDOS**

### **Para Desarrolladores**
```bash
# Ver logs de servicios
docker logs iaops-unified-portal
docker logs iaops-test-results-viewer

# Reiniciar servicios
cd /home/giovanemere/ia-ops/ia-ops-veritas
./scripts/deploy-full-stack.sh

# Health check manual
curl http://localhost:8876/health
```

### **Para Usuarios**
- **Portal Principal**: http://localhost:8876
- **Generar Reporte**: Dashboard > "Generate Sample Report"
- **Ver Reportes**: Sidebar > "Test Results Viewer"
- **Gestionar Proyectos**: Sidebar > "Project Manager"

---

## 🎉 **¡PORTAL LISTO PARA USAR!**

El portal está completamente desplegado y funcional. Puedes:

1. **Navegar** por todos los servicios desde el portal unificado
2. **Crear proyectos** y analizarlos automáticamente
3. **Generar reportes** profesionales en HTML
4. **Gestionar tests** de forma centralizada
5. **Ver métricas** y analytics en tiempo real

**¡Comienza explorando el Dashboard en http://localhost:8876!** 🚀
