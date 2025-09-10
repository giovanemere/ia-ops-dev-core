#!/bin/bash

# IA-Ops Dev-Core Microservices Management
# Gestión de microservicios independientes

case "$1" in
    start)
        echo "🚀 Iniciando microservicios Dev-Core..."
        cd docker && docker-compose up -d
        echo "✅ Microservicios iniciados"
        ;;
    
    stop)
        echo "🛑 Deteniendo microservicios Dev-Core..."
        cd docker && docker-compose down
        echo "✅ Microservicios detenidos"
        ;;
    
    restart)
        echo "🔄 Reiniciando microservicios Dev-Core..."
        cd docker && docker-compose restart
        echo "✅ Microservicios reiniciados"
        ;;
    
    status)
        echo "📊 Estado de microservicios Dev-Core:"
        cd docker && docker-compose ps
        ;;
    
    logs)
        echo "📋 Logs de microservicios (Ctrl+C para salir):"
        cd docker && docker-compose logs -f
        ;;
    
    *)
        echo "Uso: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Microservicios disponibles:"
        echo "  📂 Repository Manager (8860)"
        echo "  📋 Task Manager (8861)"
        echo "  📊 Log Manager (8862)"
        echo "  🔄 DataSync Manager (8863)"
        echo "  🏃 GitHub Runner Manager (8864)"
        exit 1
        ;;
esac
