#!/bin/bash

echo "🌱 Seeding IA-Ops Dev Core with sample data"
echo "==========================================="

BASE_URL="http://localhost"

# Crear repositorios de ejemplo
echo "📁 Creating sample repositories..."

repos=(
    '{"name":"ia-ops-frontend","url":"https://github.com/giovanemere/ia-ops-frontend","branch":"main","description":"Frontend application for IA-Ops"}'
    '{"name":"ia-ops-backend","url":"https://github.com/giovanemere/ia-ops-backend","branch":"main","description":"Backend services for IA-Ops"}'
    '{"name":"ia-ops-docs","url":"https://github.com/giovanemere/ia-ops-docs","branch":"main","description":"Documentation site"}'
    '{"name":"ia-ops-mobile","url":"https://github.com/giovanemere/ia-ops-mobile","branch":"develop","description":"Mobile application"}'
)

for repo in "${repos[@]}"; do
    echo "Creating repository..."
    curl -s -X POST "$BASE_URL:8860/repositories" \
        -H "Content-Type: application/json" \
        -d "$repo" | jq -r '.name // "Error"'
done

echo ""
echo "📋 Creating sample tasks..."

# Crear tareas de ejemplo
tasks=(
    '{"name":"Build Frontend","type":"build","command":"npm run build","repository_id":1}'
    '{"name":"Run Tests","type":"test","command":"npm test","repository_id":1}'
    '{"name":"Deploy to Staging","type":"deploy","command":"docker deploy staging","repository_id":1}'
    '{"name":"Sync Documentation","type":"sync","command":"mkdocs build","repository_id":3}'
    '{"name":"Build Mobile App","type":"build","command":"flutter build","repository_id":4}'
    '{"name":"Backend Tests","type":"test","command":"pytest","repository_id":2}'
)

for task in "${tasks[@]}"; do
    echo "Creating task..."
    curl -s -X POST "$BASE_URL:8861/tasks" \
        -H "Content-Type: application/json" \
        -d "$task" | jq -r '.data.name // "Error"'
done

echo ""
echo "🎯 Executing some tasks for demo..."

# Ejecutar algunas tareas
curl -s -X POST "$BASE_URL:8861/tasks/1/execute" > /dev/null
curl -s -X POST "$BASE_URL:8861/tasks/2/execute" > /dev/null

echo ""
echo "✅ Sample data created successfully!"
echo ""
echo "📊 Summary:"
echo "  - Repositories: $(curl -s $BASE_URL:8860/repositories | jq -r '.count // .data | length')"
echo "  - Tasks: $(curl -s $BASE_URL:8861/tasks | jq -r '.count // .data | length')"
echo ""
echo "🔗 View data:"
echo "  - Repositories: curl $BASE_URL:8860/repositories | jq"
echo "  - Tasks: curl $BASE_URL:8861/tasks | jq"
echo ""
echo "🎉 Ready for frontend development!"
