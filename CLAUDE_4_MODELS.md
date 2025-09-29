# Claude 4 Models Configuration

## Available Claude 4 Models (2025)

The Braid system now supports the latest Claude 4 series models:

### **Claude 4 Opus** - `claude-4-opus-20250101`
- **Best for**: Complex reasoning, creative tasks, advanced analysis
- **Speed**: Slower but highest quality
- **Use cases**: Research, complex problem solving, creative writing

### **Claude 4 Sonnet** - `claude-4-sonnet-20250101` ⭐ **DEFAULT**
- **Best for**: Balanced performance and speed
- **Speed**: Fast with excellent quality
- **Use cases**: General AI agent tasks, business automation, data processing

### **Claude 4 Haiku** - `claude-4-haiku-20250101`
- **Best for**: Quick responses, simple tasks
- **Speed**: Fastest
- **Use cases**: Real-time chat, simple workflows, rapid prototyping

## Configuration

### Default Model
The system defaults to **Claude 4 Sonnet** for the best balance of speed and capability.

### Switching Models
You can specify different models when creating agents:

```json
{
  "agent_type": "research",
  "config": {
    "model": "claude-4-opus-20250101"  // For complex research tasks
  }
}
```

### Environment Variables
Only one environment variable needed:
- `ANTHROPIC_API_KEY` - Your Anthropic API key

## Model Capabilities

All Claude 4 models support:
- ✅ 200K+ context window
- ✅ Advanced reasoning and analysis
- ✅ Code generation and debugging
- ✅ Multi-language support
- ✅ Tool use and function calling
- ✅ Image analysis (where supported)
- ✅ JSON mode and structured outputs

## Pricing Considerations

- **Haiku**: Most cost-effective for high-volume tasks
- **Sonnet**: Best value for most use cases
- **Opus**: Premium pricing for premium capabilities

Choose the model that best fits your specific use case and budget requirements.
