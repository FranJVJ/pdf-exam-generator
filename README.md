# 📚 PDF Exam Generator

Una aplicación web moderna que convierte documentos PDF en exámenes interactivos usando inteligencia artificial.

## 🌟 Demo en Vivo

🔗 **[Prueba la aplicación aquí](https://pdf-exam-generator.vercel.app/)**

## ✨ Características

- 🔄 **Dos tipos de examen**: Test (20 preguntas múltiple opción) y Desarrollo (5 preguntas abiertas)
- 🤖 **IA powered**: Usa Groq AI (LLaMA 3.3-70B-Versatile) para generar preguntas inteligentes
- 📄 **Procesamiento de PDFs**: Extrae texto automáticamente usando pdfplumber
- 🖼️ **OCR integrado**: Procesamiento de imágenes con Tesseract (español/inglés)
- 🎯 **Corrección automática**: Evaluación instantánea con retroalimentación detallada
- 🔀 **Preguntas variadas**: Sistema de aleatorización para evitar repetición
- 💰 **Completamente gratis**: Sin costos de API usando Groq
- ⚡ **Interfaz moderna**: Construido con Next.js 15 y Tailwind CSS
- 📱 **Experiencia optimizada**: Validación en tiempo real y navegación intuitiva
- 🎨 **UI mejorada**: Scroll automático, validación de archivos y diseño visual limpio

## 🛠️ Tecnologías

- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: Next.js API Routes
- **IA**: Groq AI (LLaMA 3.3-70B-Versatile)
- **PDF Processing**: pdfplumber (Python)
- **Deployment**: Vercel

## 📋 Requisitos Previos

- Node.js 18+ 
- Python 3.8+
- Cuenta gratuita en [Groq](https://console.groq.com/)

## ⚙️ Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/FranJVJ/pdf-exam-generator.git
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

Crea un archivo `.env.local` en la raíz del proyecto y agrega tu API key de Groq:
```env
GROQ_API_KEY=tu_api_key_aqui
```

5. **Iniciar el servidor de desarrollo**
```bash
npm run dev
```

## 🎮 Uso

1. Abre http://localhost:3000
2. Selecciona el tipo de examen (Test o Desarrollo)
3. Sube un archivo PDF (lee las recomendaciones)
4. Genera preguntas automáticamente
5. Responde las preguntas
6. Obtén tu calificación y retroalimentación

## ⚠️ Compatibilidad de Archivos

### 🌐 **Versión Online (Vercel)**
- **Limitaciones**: Procesamiento limitado de PDFs complejos
- **Recomendación**: Para mejores resultados, usar la versión local
- **Manejo inteligente**: Sistema honesto que informa cuando no puede procesar un archivo

### 💻 **Versión Local**
- **Funcionamiento completo**: Extrae texto real de cualquier PDF usando pdfplumber
- **Sin limitaciones**: Procesa PDFs complejos, escaneados y con imágenes
- **Rendimiento óptimo**: Todas las funcionalidades disponibles

### 📋 **Limitaciones Generales**
- **Tamaño máximo**: 10MB por archivo
- **Libros escaneados**: Deben estar perfectamente escaneados o el texto puede detectarse incorrectamente
- **Presentaciones PDF**: Slides y diapositivas no son ideales para generar exámenes

### ✅ **Funcionan mejor**
- Documentos de texto y apuntes
- Material educativo con contenido textual claro  
- Temarios y manuales estructurados

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

- **Doble entorno**: Funcionamiento optimizado tanto en local como en producción
- **Validación en tiempo real**: Verificación de tamaño de archivos al seleccionar
- **Navegación mejorada**: Scroll automático y flujo de usuario optimizado
- **Manejo honesto de errores**: Informa claramente cuando no puede procesar un PDF
- **Sistema de reintentos**: 3 intentos automáticos con Groq AI
- **Fallback inteligente**: Manejo elegante de PDFs no procesables
- **Validación robusta**: Verificación de tipos de archivo y tamaño
- **Limpieza automática**: Eliminación de archivos temporales
- **Interface moderna**: Eliminación de elementos redundantes y mejor UX

## 💰 Ventajas de Groq

- ✨ **Gratuito**: Hasta 14,400 requests por día
- ⚡ **Rápido**: Inferencia ultra-rápida
- 🔓 **Open Source**: Modelos LLaMA y Mixtral
- 💰 **Sin costos**: No necesitas tarjeta de crédito

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## � **Nueva Arquitectura - Python + Railway**

### **¿Por qué Python?**
Después de múltiples intentos con JavaScript/Node.js, hemos migrado a Python para el procesamiento de PDFs debido a:

- **Mejor compatibilidad**: `pdfplumber` maneja PDFs complejos (incluyendo Wuolah) de forma nativa
- **Estabilidad**: Sin problemas de Canvas/OffscreenCanvas como en Vercel
- **Rendimiento**: Procesamiento más rápido y confiable de documentos
- **Escalabilidad**: Mejor manejo de memoria y recursos

### **Arquitectura Dual**
- **Frontend**: Next.js en Vercel (interfaz usuario)
- **Backend**: FastAPI en Railway (procesamiento PDFs + AI)

### **Desarrollo Local - Nueva API**

#### **Configurar Backend Python**
```bash
# 1. Instalar dependencias Python
cd api
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu GROQ_API_KEY

# 3. Ejecutar API
python -m uvicorn main:app --reload --port 8000
```

#### **Configurar Frontend**
```bash
# 1. Actualizar .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# 2. Ejecutar frontend
npm run dev
```

#### **Desarrollo Completo (Recomendado)**
```bash
# Ejecutar ambos servidores simultáneamente
npm run dev:full
```

### **Despliegue en Railway**
Ver [DEPLOYMENT.md](./DEPLOYMENT.md) para instrucciones completas.

#### **Pasos Rápidos**
1. Fork/clonar este repositorio
2. Crear cuenta en [Railway](https://railway.app)
3. Conectar repositorio GitHub
4. Configurar `GROQ_API_KEY` en variables de entorno
5. Railway detectará automáticamente la configuración Python
6. Actualizar `NEXT_PUBLIC_API_BASE_URL` en Vercel con la URL de Railway

## �🙏 Reconocimientos

- [Groq](https://groq.com/) por la API de IA gratuita
- [shadcn/ui](https://ui.shadcn.com/) por los componentes de UI
- [pdfplumber](https://github.com/jsvine/pdfplumber) por el procesamiento de PDFs
- [Vercel](https://vercel.com/) por el hosting gratuito
- [Railway](https://railway.app/) por el hosting Python

---

⭐ ¡Dale una estrella si te gusta el proyecto!

**Creado con ❤️ por [FranJVJ](https://github.com/FranJVJ)**
