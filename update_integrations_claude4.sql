-- Update Anthropic integration to use Claude 4 models
UPDATE integrations 
SET config = '{"api_key_env": "ANTHROPIC_API_KEY", "model": "claude-4-sonnet-20250101", "primary": true, "available_models": ["claude-4-opus-20250101", "claude-4-sonnet-20250101", "claude-4-haiku-20250101"]}'
WHERE name = 'anthropic';

-- Insert Claude 4 model configurations if they don't exist
INSERT INTO integrations (name, config) VALUES 
('claude-4-opus', '{"api_key_env": "ANTHROPIC_API_KEY", "model": "claude-4-opus-20250101", "description": "Most capable Claude 4 model"}'),
('claude-4-sonnet', '{"api_key_env": "ANTHROPIC_API_KEY", "model": "claude-4-sonnet-20250101", "description": "Balanced Claude 4 model - speed and quality"}'),
('claude-4-haiku', '{"api_key_env": "ANTHROPIC_API_KEY", "model": "claude-4-haiku-20250101", "description": "Fastest Claude 4 model"}')
ON CONFLICT (name) DO NOTHING;
