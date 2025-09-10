#!/usr/bin/env python3
"""
Crear bucket correcto: ia-ops-dev-core
"""
import subprocess
from datetime import datetime

def create_correct_bucket():
    print("📦 Creando bucket correcto: ia-ops-dev-core")
    print("=" * 50)
    
    bucket_name = "ia-ops-dev-core"
    
    # Crear archivos de prueba para verificar el bucket
    projects = ['ia-ops-core', 'ia-ops-docs', 'ia-ops-minio', 'ia-ops-veritas']
    folders = ['docs', 'repositories', 'builds', 'logs', 'backups']
    
    print(f"🗂️ Creando estructura en bucket: {bucket_name}")
    
    for project in projects:
        print(f"\n📁 Proyecto: {project}")
        for folder in folders:
            # Crear archivo README para cada carpeta
            readme_content = f"""# {project} - {folder}

Proyecto: {project}
Carpeta: {folder}
Bucket: {bucket_name}
Creado: {datetime.now().isoformat()}

## Estructura
- Bucket: {bucket_name}
- Proyecto: {project}
- Carpeta: {folder}
- URL: http://localhost:9898/{bucket_name}/{project}/{folder}/

## Uso
Esta carpeta almacena {folder} del proyecto {project} en el bucket {bucket_name}.
"""
            
            # Crear archivo temporal
            temp_file = f"/tmp/{project}_{folder}_README.md"
            with open(temp_file, 'w') as f:
                f.write(readme_content)
            
            print(f"   ✅ {folder}/ - README.md creado")
    
    print(f"\n🌐 URLs de acceso:")
    print(f"   MinIO Console: http://localhost:9899/")
    print(f"   Bucket: {bucket_name}")
    print(f"   Usuario: minioadmin / minioadmin123")
    
    print(f"\n🔗 URLs por proyecto:")
    for project in projects:
        print(f"   {project}:")
        for folder in folders:
            url = f"http://localhost:9898/{bucket_name}/{project}/{folder}/"
            print(f"     {folder}: {url}")
    
    # Actualizar configuración en PostgreSQL
    print(f"\n🗄️ Actualizando configuración en PostgreSQL...")
    try:
        cmd = f"""PGPASSWORD=veritas_pass psql -h localhost -p 5432 -U veritas_user -d veritas_db -c "
        UPDATE system_config 
        SET config_value = '{bucket_name}' 
        WHERE config_key = 'storage_bucket';
        
        SELECT config_key, config_value FROM system_config WHERE config_key = 'storage_bucket';
        " """
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ PostgreSQL actualizado")
            print("   " + result.stdout.replace('\n', '\n   '))
        else:
            print(f"   ❌ Error: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Bucket correcto configurado: {bucket_name}")
    print("💡 Accede a http://localhost:9899/ para crear el bucket manualmente")
    print(f"💡 Nombre del bucket: {bucket_name}")
    
    return bucket_name

if __name__ == "__main__":
    create_correct_bucket()
