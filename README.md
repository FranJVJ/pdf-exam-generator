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

# 📚 PDF Exam Generator

Una aplicación web moderna que convierte documentos PDF en exámenes interactivos usando inteligencia artificial.

## ✨ Características

- 🔄 **Dos tipos de examen**: Test (20 preguntas múltiple opción) y Desarrollo (5 preguntas abiertas)
- 🤖 **IA powered**: Usa Groq AI (LLaMA 3-70B) para generar preguntas inteligentes
- 📄 **Procesamiento de PDFs**: Extrae texto automáticamente usando pdfplumber
- 🎯 **Corrección automática**: Evaluación instantánea con retroalimentación detallada
- 🔀 **Preguntas variadas**: Sistema de aleatorización para evitar repetición
- 💰 **Completamente gratis**: Sin costos de API usando Groq
- ⚡ **Interfaz moderna**: Construido con Next.js 15 y Tailwind CSS

## 🚀 Demo en Vivo

> En proceso de deployment a Vercel

## 🛠️ Tecnologías

- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: Next.js API Routes
- **IA**: Groq AI (LLaMA 3-70B-8192)
- **PDF Processing**: pdfplumber (Python)
- **Deployment**: Vercel (próximamente)

## 📋 Requisitos Previos

- Node.js 18+ 
- Python 3.8+
- Cuenta gratuita en [Groq](https://console.groq.com/)

## ⚙️ Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/pdf-exam-generator.git
cd pdf-exam-generator
```

2. **Instalar dependencias de Node.js**
```bash
npm install
```

3. **Configurar entorno Python**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install pdfplumber
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env.local
```

Agregar tu API key de Groq en `.env.local`:
```
GROQ_API_KEY=tu_api_key_aqui
```

5. **Iniciar el servidor de desarrollo**
```bash
npm run dev
```

## 🎮 Uso

1. Abre http://localhost:3000
2. Selecciona el tipo de examen (Test o Desarrollo)
3. Sube un archivo PDF
4. Genera preguntas automáticamente
5. Responde las preguntas
6. Obtén tu calificación y retroalimentación

## 📁 Estructura del Proyecto

```
pdf-exam-generator/
├── app/
│   ├── api/
│   │   ├── generate-questions/    # Generación de preguntas con IA
│   │   └── grade-exam/           # Corrección con IA
│   ├── page.tsx                  # Página principal
│   └── layout.tsx               # Layout de la aplicación
├── components/
│   └── ui/                      # Componentes de UI (shadcn/ui)
├── lib/
│   └── utils.ts                 # Utilidades
├── pdf_extractor.py             # Script Python para procesar PDFs
└── public/                      # Archivos estáticos
```

## 🔧 API Endpoints

### POST `/api/generate-questions`
Genera preguntas basadas en un PDF
- **Input**: FormData con PDF, tipo de examen, semilla aleatoria
- **Output**: JSON con preguntas generadas

### POST `/api/grade-exam`
Califica las respuestas del examen
- **Input**: JSON con preguntas y respuestas del usuario
- **Output**: JSON con calificación y retroalimentación

## 🌟 Características Técnicas

- **Sistema de reintentos**: 3 intentos automáticos con Groq AI
- **Fallback inteligente**: Preguntas de ejemplo si falla la IA
- **Validación robusta**: Verificación de tipos de archivo y tamaño
- **Limpieza automática**: Eliminación de archivos temporales
- **Manejo de errores**: Sistema completo de logging y recuperación

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🙏 Reconocimientos

- [Groq](https://groq.com/) por la API de IA gratuita
- [shadcn/ui](https://ui.shadcn.com/) por los componentes de UI
- [pdfplumber](https://github.com/jsvine/pdfplumber) por el procesamiento de PDFs

---

⭐ ¡Dale una estrella si te gusta el proyecto!

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
