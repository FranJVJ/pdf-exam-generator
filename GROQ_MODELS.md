# Modelos disponibles en Groq (Actualizados)

## 🚀 Modelos recomendados (2025)

### LLaMA 3 70B (Recomendado)
```typescript
model: groq("llama3-70b-8192")
```
- **Mejor para**: Generación de contenido complejo, razonamiento avanzado
- **Pros**: Más inteligente, mejores respuestas, 8K tokens de contexto
- **Contras**: Un poco más lento que modelos menores
- **Uso recomendado**: Proyectos que requieren alta calidad

### LLaMA 3 8B Instant
```typescript
model: groq("llama3-8b-8192")
```
- **Mejor para**: Respuestas rápidas, tareas simples
- **Pros**: Ultra-rápido, eficiente, 8K tokens
- **Contras**: Menos sofisticado que el 70B
- **Uso recomendado**: Prototipos, desarrollo, aplicaciones de alta velocidad

### Mixtral 8x7B
```typescript
model: groq("mixtral-8x7b-32768")
```
- **Mejor para**: Balance entre velocidad y calidad
- **Pros**: Buen balance, maneja contextos largos (32k tokens)
- **Contras**: No tan avanzado como LLaMA 3 70B
- **Uso recomendado**: Análisis de documentos largos

### Gemma 7B
```typescript
model: groq("gemma-7b-it")
```
- **Mejor para**: Tareas específicas, respuestas estructuradas
- **Pros**: Rápido, eficiente para tareas específicas
- **Contras**: Menos versátil que LLaMA
- **Uso recomendado**: Casos de uso específicos

## 🔄 Cómo cambiar el modelo

1. Abre `app/api/generate-questions/route.ts`
2. Busca la línea:
```typescript
model: groq("llama-3.1-70b-versatile"),
```
3. Reemplázala con el modelo que prefieras

## 📊 Comparación de rendimiento

| Modelo | Velocidad | Calidad | Contexto | Recomendado para |
|--------|-----------|---------|----------|------------------|
| LLaMA 3 70B | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 8K tokens | Producción, calidad |
| LLaMA 3 8B | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 8K tokens | Desarrollo, velocidad |
| Mixtral 8x7B | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 32K tokens | Documentos largos |
| Gemma 7B | ⭐⭐⭐⭐ | ⭐⭐⭐ | 4K tokens | Tareas específicas |

## 🎯 Consejos de uso

### Para preguntas de examen (nuestro caso):
- **Recomendado**: `llama3-70b-8192`
- **Alternativa rápida**: `llama3-8b-8192`

### Para análisis de PDFs largos:
- **Recomendado**: `mixtral-8x7b-32768`

### Para desarrollo/testing:
- **Recomendado**: `llama-3.1-8b-instant`

## 🔧 Configuración avanzada

También puedes configurar parámetros adicionales:

```typescript
const { text } = await generateText({
  model: groq("llama3-70b-8192"),
  temperature: 0.7,        // Creatividad (0.0 - 2.0)
  maxTokens: 2000,         // Máximo de tokens en respuesta
  topP: 0.9,              // Diversidad de palabras
  stop: ["END"],          // Palabras que detienen la generación
  prompt: "Tu prompt aquí..."
})
```

### Parámetros recomendados para preguntas de examen:
```typescript
temperature: 0.3,        // Baja creatividad para precisión
maxTokens: 1500,         // Suficiente para 5 preguntas
topP: 0.8,              // Balance entre diversidad y consistencia
```
