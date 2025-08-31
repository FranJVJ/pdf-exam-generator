# PDF Exam Generator

Una aplicación web que permite generar exámenes de opción múltiple a partir de contenido PDF usando IA.

## Características

- 📄 Carga de archivos PDF
- 🤖 Generación automática de preguntas usando Groq (LLaMA 3.1)
- ✅ Sistema de calificación automática
- 🎨 Interfaz moderna con Next.js y Tailwind CSS

## Configuración

### 1. Instalar dependencias

```bash
npm install --legacy-peer-deps
```

### 2. Configurar Groq API

1. Ve a [https://console.groq.com/](https://console.groq.com/)
2. Crea una cuenta gratuita
3. Genera una API key
4. Crea un archivo `.env.local` en la raíz del proyecto:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Ejecutar el proyecto

```bash
npm run dev
```

La aplicación estará disponible en [http://localhost:3000](http://localhost:3000)

## Modelos disponibles en Groq

- `llama-3.1-70b-versatile` (recomendado) - LLaMA 3.1 70B
- `llama-3.1-8b-instant` - LLaMA 3.1 8B (más rápido)
- `mixtral-8x7b-32768` - Mixtral 8x7B

Para cambiar el modelo, modifica el archivo `app/api/generate-questions/route.ts`:

```typescript
model: groq("llama-3.1-8b-instant"), // Cambia aquí
```

## Ventajas de Groq

- ✨ **Gratuito**: Hasta 3,500 requests por día
- ⚡ **Rápido**: Inferencia ultra-rápida
- 🔓 **Open Source**: Modelos LLaMA y Mixtral
- 💰 **Sin costos**: No necesitas tarjeta de crédito

## Estructura del proyecto

```
app/
├── api/
│   ├── generate-questions/   # Endpoint para generar preguntas
│   └── grade-exam/          # Endpoint para calificar exámenes
├── components/              # Componentes React
└── page.tsx                # Página principal
```
