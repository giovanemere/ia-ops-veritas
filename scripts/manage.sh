#!/bin/bash

# IA-Ops Veritas Management Script
# Uso: ./scripts/manage.sh [start|stop|restart|status|logs]

case "$1" in
    start)
        echo "🚀 Iniciando servicios IA-Ops Veritas..."
        ./scripts/start-unified.sh
        ;;
    
    stop)
        echo "🛑 Deteniendo servicios IA-Ops Veritas..."
        docker-compose down
        echo "✅ Servicios detenidos"
        ;;
    
    restart)
        echo "🔄 Reiniciando servicios IA-Ops Veritas..."
        docker-compose restart
        echo "✅ Servicios reiniciados"
        echo "🌐 Portal: http://localhost:8869"
        ;;
    
    status)
        echo "📊 Estado de servicios IA-Ops Veritas:"
        docker-compose ps
        ;;
    
    logs)
        echo "📋 Logs de servicios (Ctrl+C para salir):"
        docker-compose logs -f
        ;;
    
    *)
        echo "Uso: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Comandos disponibles:"
        echo "  start   - Iniciar todos los servicios (con build)"
        echo "  stop    - Detener todos los servicios"
        echo "  restart - Reiniciar servicios (sin build)"
        echo "  status  - Ver estado de los servicios"
        echo "  logs    - Ver logs en tiempo real"
        echo ""
        echo "Ejemplo: ./scripts/manage.sh restart"
        exit 1
        ;;
esac
