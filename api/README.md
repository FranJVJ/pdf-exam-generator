# 🐍 PDF Exam Generator API

API backend en FastAPI con procesamiento robusto de PDFs y OCR.

## ✨ Características

- **📄 Procesamiento PDFs**: `pdfplumber` para extracción de texto nativa
- **🖼️ OCR Imágenes**: `Tesseract` para español e inglés
- **🤖 IA Integrada**: `Groq AI` para generación y calificación de preguntas
- **🚀 FastAPI**: API moderna con documentación automática
- **📊 Logging**: Sistema de logs detallado para debugging

## 🛠️ Desarrollo Local

### Prerrequisitos
- Python 3.9+
- Tesseract OCR (para desarrollo local)

### Instalación Tesseract Local

#### Windows
```bash
# Con chocolatey
choco install tesseract

# O descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
```

#### macOS
```bash
brew install tesseract tesseract-lang
```

#### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
```

### Configuración
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu GROQ_API_KEY

# 3. Ejecutar servidor
uvicorn main:app --reload --port 8000
```

## 📚 Endpoints

### `POST /generate-questions`
Genera preguntas desde un PDF.

**Parámetros:**
- `pdf` (file): Archivo PDF
- `examType` (string): "test" | "development"
- `randomSeed` (string, opcional)

### `POST /extract-text-from-image`
Extrae texto de una imagen usando OCR.

**Parámetros:**
- `image` (file): Archivo de imagen (JPG, PNG, etc.)

**Respuesta:**
```json
{
  "text": "Texto extraído...",
  "length": 150
}
```

### `POST /grade-exam`
Califica respuestas del examen.

**Body:**
```json
{
  "questions": [...],
  "userAnswers": [...]
}
```

### `GET /health`
Health check del servicio.

## 🚀 Despliegue

### Railway (Recomendado)
El proyecto incluye:
- `Dockerfile` con Tesseract preinstalado
- `railway.toml` configurado
- Detección automática de Python

### Variables de Entorno Requeridas
```bash
GROQ_API_KEY=tu_api_key_aqui
```

## 🧪 Testing

```bash
# Health check
curl http://localhost:8000/health

# Test OCR
curl -X POST "http://localhost:8000/extract-text-from-image" \
  -F "image=@test-image.jpg"

# Test PDF processing
curl -X POST "http://localhost:8000/generate-questions" \
  -F "pdf=@test.pdf" \
  -F "examType=test"
```

## 📖 Documentación Automática

Una vez ejecutando, visita:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐛 Troubleshooting

### Error: "Tesseract not found"
- **Railway**: Se instala automáticamente via Dockerfile
- **Local**: Seguir instrucciones de instalación según OS

### Error: "Language not found"
```bash
# Verificar idiomas instalados
tesseract --list-langs

# Instalar idiomas adicionales (Ubuntu)
sudo apt-get install tesseract-ocr-spa tesseract-ocr-eng
```

### Error: "Image processing failed"
- Verificar formato de imagen (JPG, PNG soportados)
- Tamaño máximo: 5MB
- Asegurar que la imagen contenga texto legible
