-- Tabla de configuraciones centralizadas
CREATE TABLE IF NOT EXISTS configurations (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    config_type VARCHAR(50) NOT NULL, -- 'provider', 'api_provider', 'system', 'auth'
    is_encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_configurations_key ON configurations(config_key);
CREATE INDEX IF NOT EXISTS idx_configurations_type ON configurations(config_type);

-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_configurations_updated_at 
    BEFORE UPDATE ON configurations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insertar configuraciones por defecto
INSERT INTO configurations (config_key, config_value, config_type) VALUES
('github', '{"configured": false, "user": "", "token": ""}', 'provider'),
('azure', '{"configured": false, "subscription_id": "", "tenant_id": "", "client_id": "", "client_secret": ""}', 'provider'),
('aws', '{"configured": false, "access_key": "", "secret_key": "", "region": "us-east-1"}', 'provider'),
('gcp', '{"configured": false, "project_id": "", "service_account_key": ""}', 'provider'),
('oci', '{"configured": false, "tenancy": "", "user": "", "fingerprint": "", "key_file": ""}', 'provider'),
('openai', '{"configured": false, "api_key": "", "organization": "", "model": "gpt-4", "max_tokens": 4000}', 'api_provider'),
('google_ai', '{"configured": false, "api_key": "", "model": "gemini-pro"}', 'api_provider'),
('bedrock', '{"configured": false, "access_key": "", "secret_key": "", "region": "us-east-1", "model": "anthropic.claude-3-sonnet-20240229-v1:0"}', 'api_provider'),
('anthropic', '{"configured": false, "api_key": "", "model": "claude-3-sonnet-20240229"}', 'api_provider'),
('azure_ai', '{"configured": false, "api_key": "", "endpoint": "", "deployment": "", "version": "2024-02-15-preview"}', 'api_provider'),
('postgres', '{"host": "localhost", "port": 5434, "database": "postgres", "user": "postgres", "password": ""}', 'system'),
('redis', '{"host": "localhost", "port": 6380, "password": "", "database": 0}', 'system'),
('minio', '{"host": "localhost", "port": 9899, "access_key": "minioadmin", "secret_key": "", "bucket": "iaops-portal", "region": "us-east-1", "ssl": false}', 'system')
ON CONFLICT (config_key) DO NOTHING;
