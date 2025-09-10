#!/bin/bash

echo "🔄 Reiniciando IA-Ops Dev-Core..."

# Reiniciar contenedores Docker
docker-compose restart

echo "✅ Dev-Core reiniciado"
echo "📊 API disponible en: http://localhost:8080"
echo "📋 Swagger UI: http://localhost:8080/docs"
