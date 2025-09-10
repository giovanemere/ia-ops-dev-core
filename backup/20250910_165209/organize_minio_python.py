#!/usr/bin/env python3
"""
Organizar MinIO usando Python - Estructura por proyectos
"""
import io
from datetime import datetime

def organize_minio():
    print("🗂️ Organizando MinIO con Python")
    print("=" * 40)
    
    try:
        from minio import Minio
        
        # Cliente MinIO
        client = Minio('localhost:9898', 
                      access_key='minioadmin', 
                      secret_key='minioadmin123', 
                      secure=False)
        
        bucket_name = 'ia-ops-storage'
        
        # Crear bucket si no existe
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"✅ Bucket creado: {bucket_name}")
        else:
            print(f"✅ Bucket existe: {bucket_name}")
        
        # Proyectos y estructura
        projects = [
            "ia-ops-core",
            "ia-ops-docs", 
            "ia-ops-minio",
            "ia-ops-veritas"
        ]
        
        folders = ["docs", "repositories", "builds", "logs", "backups"]
        
        print(f"\n📁 Creando estructura por proyectos...")
        
        for project in projects:
            print(f"\n📦 {project}:")
            
            for folder in folders:
                # Crear archivo README para cada carpeta
                readme_content = f"""# {project} - {folder}

Proyecto: {project}
Tipo: {folder}
Creado: {datetime.now().isoformat()}

## Estructura
- Proyecto: {project}
- Carpeta: {folder}
- Bucket: {bucket_name}

## Uso
Esta carpeta almacena {folder} del proyecto {project}.
"""
                
                # Subir README
                object_name = f"{project}/{folder}/README.md"
                
                try:
                    client.put_object(
                        bucket_name,
                        object_name,
                        io.BytesIO(readme_content.encode('utf-8')),
                        len(readme_content.encode('utf-8')),
                        content_type='text/markdown'
                    )
                    print(f"   ✅ {folder}/")
                except Exception as e:
                    print(f"   ❌ {folder}/: {e}")
        
        # Listar estructura creada
        print(f"\n🔍 Estructura creada en bucket '{bucket_name}':")
        try:
            objects = client.list_objects(bucket_name, recursive=True)
            count = 0
            for obj in objects:
                print(f"   📄 {obj.object_name}")
                count += 1
            print(f"\n📊 Total archivos: {count}")
        except Exception as e:
            print(f"❌ Error listando: {e}")
        
        # URLs de acceso
        print(f"\n🌐 Acceso:")
        print(f"   Console: http://localhost:9899/")
        print(f"   Bucket: {bucket_name}")
        print(f"   Usuario: minioadmin / minioadmin123")
        
        # Ejemplo de URLs por proyecto
        print(f"\n🔗 URLs por proyecto:")
        for project in projects:
            print(f"   {project}:")
            for folder in folders:
                url = f"http://localhost:9898/{bucket_name}/{project}/{folder}/"
                print(f"     {folder}: {url}")
        
        return True
        
    except ImportError:
        print("❌ Módulo 'minio' no disponible")
        print("💡 Instalar con: pip install minio")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    organize_minio()
