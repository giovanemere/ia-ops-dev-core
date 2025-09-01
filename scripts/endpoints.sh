#!/bin/bash

echo "🔗 IA-Ops Dev Core Services - Available Endpoints"
echo "================================================="

services=(
    "8860:Repository Manager"
    "8861:Task Manager"
    "8862:Log Manager"
    "8863:DataSync Manager"
    "8864:GitHub Runner Manager"
    "8865:TechDocs Builder"
)

for service in "${services[@]}"; do
    port=$(echo $service | cut -d: -f1)
    name=$(echo $service | cut -d: -f2)
    
    echo ""
    echo "📋 $name (http://localhost:$port)"
    echo "   Health: http://localhost:$port/health"
    
    # Intentar obtener endpoints si existe el endpoint raíz
    if curl -s -f http://localhost:$port/ > /dev/null 2>&1; then
        echo "   Info: http://localhost:$port/"
        # Mostrar endpoints específicos si están disponibles
        case $port in
            8860)
                echo "   Repositories: http://localhost:$port/repositories"
                ;;
            8861)
                echo "   Tasks: http://localhost:$port/tasks"
                ;;
            8862)
                echo "   Logs: http://localhost:$port/logs"
                ;;
        esac
    fi
done

echo ""
echo "💡 Tip: Use 'curl http://localhost:PORT/' to see available endpoints for each service"
