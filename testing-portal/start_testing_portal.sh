#!/bin/bash

echo "🧪 IA-Ops Testing Portal Startup"
echo "================================="

# Verificar dependencias
echo "📦 Checking dependencies..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Instalar dependencias si no existen
if [ ! -f "requirements.txt" ]; then
    echo "📝 Creating requirements.txt..."
    cat > requirements.txt << EOF
flask>=2.3.0
requests>=2.31.0
aiohttp>=3.8.0
psutil>=5.9.0
matplotlib>=3.7.0
pandas>=2.0.0
asyncio
threading
pathlib
argparse
EOF
fi

# Instalar dependencias
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Verificar archivos necesarios
echo "📁 Checking required files..."

required_files=(
    "test_cases_complete.json"
    "mock_services.py"
    "performance_automation.py"
    "test_portal_runner.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
    echo "  ✅ $file"
done

# Crear directorio de resultados
mkdir -p test-results
echo "✅ Test results directory created"

# Función para mostrar ayuda
show_help() {
    echo ""
    echo "🚀 Usage Options:"
    echo "=================="
    echo ""
    echo "1. Run with mock services (recommended for development):"
    echo "   ./start_testing_portal.sh --mocks"
    echo ""
    echo "2. Run against real services:"
    echo "   ./start_testing_portal.sh --real"
    echo ""
    echo "3. Run specific test suite:"
    echo "   ./start_testing_portal.sh --suite unit"
    echo "   ./start_testing_portal.sh --suite integration"
    echo "   ./start_testing_portal.sh --suite performance"
    echo ""
    echo "4. Start only mock services:"
    echo "   ./start_testing_portal.sh --mocks-only"
    echo ""
    echo "5. Performance monitoring (continuous):"
    echo "   ./start_testing_portal.sh --monitor"
    echo ""
}

# Función para verificar servicios reales
check_real_services() {
    echo "🔍 Checking real services availability..."
    
    services=(
        "Repository Manager:8860"
        "Task Manager:8861"
        "Log Manager:8862"
        "DataSync Manager:8863"
        "GitHub Runner Manager:8864"
        "TechDocs Builder:8865"
    )
    
    available_count=0
    
    for service in "${services[@]}"; do
        name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1; then
            echo "  ✅ $name (Port $port): Available"
            ((available_count++))
        else
            echo "  ❌ $name (Port $port): Unavailable"
        fi
    done
    
    echo "📊 Services available: $available_count/6"
    
    if [ $available_count -eq 0 ]; then
        echo ""
        echo "⚠️  No real services are available!"
        echo "💡 Consider starting the backend services first:"
        echo "   cd ../ia-ops-dev-core"
        echo "   ./scripts/start-with-swagger.sh"
        echo ""
        echo "🎭 Or use mock services for testing:"
        echo "   ./start_testing_portal.sh --mocks"
        return 1
    fi
    
    return 0
}

# Función para iniciar servicios mock
start_mock_services() {
    echo "🎭 Starting mock services..."
    
    # Verificar si ya están corriendo
    if pgrep -f "mock_services.py" > /dev/null; then
        echo "⚠️  Mock services are already running"
        echo "💡 Stop them first: pkill -f mock_services.py"
        return 1
    fi
    
    # Iniciar servicios mock en background
    python3 mock_services.py &
    MOCK_PID=$!
    
    # Esperar a que inicien
    echo "⏳ Waiting for mock services to start..."
    sleep 5
    
    # Verificar que estén corriendo
    if kill -0 $MOCK_PID 2>/dev/null; then
        echo "✅ Mock services started successfully (PID: $MOCK_PID)"
        echo $MOCK_PID > .mock_services.pid
        
        # Verificar endpoints
        mock_services=(
            "Repository Manager Mock:18860"
            "Task Manager Mock:18861"
            "Log Manager Mock:18862"
        )
        
        for service in "${mock_services[@]}"; do
            name=$(echo $service | cut -d: -f1)
            port=$(echo $service | cut -d: -f2)
            
            if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1; then
                echo "  ✅ $name: http://localhost:$port"
            else
                echo "  ⏳ $name: Starting..."
            fi
        done
        
        return 0
    else
        echo "❌ Failed to start mock services"
        return 1
    fi
}

# Función para detener servicios mock
stop_mock_services() {
    if [ -f ".mock_services.pid" ]; then
        PID=$(cat .mock_services.pid)
        if kill -0 $PID 2>/dev/null; then
            echo "🛑 Stopping mock services (PID: $PID)..."
            kill $PID
            rm .mock_services.pid
            echo "✅ Mock services stopped"
        else
            echo "⚠️  Mock services not running"
            rm .mock_services.pid
        fi
    else
        echo "⚠️  No mock services PID file found"
    fi
}

# Función para ejecutar pruebas
run_tests() {
    local use_mocks=$1
    local test_suite=$2
    
    echo ""
    echo "🧪 Starting test execution..."
    echo "Test suite: $test_suite"
    echo "Use mocks: $use_mocks"
    echo ""
    
    # Construir comando
    cmd="python3 test_portal_runner.py --suite $test_suite"
    
    if [ "$use_mocks" = "true" ]; then
        cmd="$cmd --mocks"
    fi
    
    # Ejecutar pruebas
    echo "🚀 Executing: $cmd"
    echo ""
    
    $cmd
    test_exit_code=$?
    
    echo ""
    if [ $test_exit_code -eq 0 ]; then
        echo "🎉 All tests passed successfully!"
    else
        echo "⚠️  Some tests failed (exit code: $test_exit_code)"
    fi
    
    return $test_exit_code
}

# Función para monitoreo continuo
start_monitoring() {
    echo "📊 Starting continuous performance monitoring..."
    
    python3 -c "
import asyncio
from performance_automation import PerformanceTestRunner

async def monitor():
    runner = PerformanceTestRunner()
    thread = runner.run_continuous_monitoring(duration_hours=24)
    print('📈 Monitoring started for 24 hours...')
    print('Press Ctrl+C to stop')
    
    try:
        while thread.is_alive():
            await asyncio.sleep(60)
            print('📊 Monitoring active...')
    except KeyboardInterrupt:
        print('🛑 Monitoring stopped')

asyncio.run(monitor())
"
}

# Función de cleanup
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    stop_mock_services
    exit 0
}

# Trap para cleanup
trap cleanup EXIT INT TERM

# Procesar argumentos
case "${1:-help}" in
    --mocks)
        echo "🎭 Running tests with mock services"
        start_mock_services || exit 1
        run_tests "true" "${2:-all}"
        ;;
    
    --real)
        echo "🔧 Running tests against real services"
        check_real_services || exit 1
        run_tests "false" "${2:-all}"
        ;;
    
    --suite)
        if [ -z "$2" ]; then
            echo "❌ Test suite not specified"
            show_help
            exit 1
        fi
        echo "🎯 Running specific test suite: $2"
        check_real_services || {
            echo "💡 Falling back to mock services..."
            start_mock_services || exit 1
            run_tests "true" "$2"
        }
        run_tests "false" "$2"
        ;;
    
    --mocks-only)
        echo "🎭 Starting mock services only"
        start_mock_services || exit 1
        echo ""
        echo "🎉 Mock services are running!"
        echo "📝 Test them manually or run tests in another terminal"
        echo "🛑 Press Ctrl+C to stop services"
        
        # Mantener servicios corriendo
        while true; do
            sleep 1
        done
        ;;
    
    --monitor)
        echo "📊 Starting performance monitoring"
        start_monitoring
        ;;
    
    --stop)
        echo "🛑 Stopping all services"
        stop_mock_services
        ;;
    
    --help|help|*)
        show_help
        ;;
esac
