# 🚀 Despliegue en Railway - Guía Paso a Paso

## 📋 Prerrequisitos
1. Cuenta en [Railway](https://railway.app)
2. Cuenta en [GitHub](https://github.com) 
3. Código fuente en tu repositorio de GitHub

**📝 Nota importante**: Railway automáticamente instalará Tesseract OCR en el contenedor para el procesamiento de imágenes.

## 🔧 Configuración Inicial

### 1. Preparar el Repositorio
```bash
# Asegúrate de que todos los cambios estén subidos
git add .
git commit -m "Add Python API for Railway deployment"
git push origin main
```

### 2. Configurar Railway
1. Ve a [railway.app](https://railway.app)
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en "New Project"
4. Selecciona "Deploy from GitHub repo"
5. Elige tu repositorio `pdf-exam-generator`

### 3. Configurar Variables de Entorno
En el dashboard de Railway:
1. Ve a la pestaña "Variables"
2. Agrega estas variables:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Configurar el Build
Railway automáticamente detectará:
- `api/requirements.txt` para instalar dependencias Python
- `railway.toml` para configuración de despliegue
- `Procfile` como backup

## 🌐 Actualizar Frontend

### 1. Obtener la URL de Railway
Después del despliegue, Railway te dará una URL como:
`https://tu-app-nombre.railway.app`

### 2. Actualizar configuración local
En tu `.env.local`:
```bash
# Cambiar esta línea cuando tengas la URL de production
NEXT_PUBLIC_API_BASE_URL=https://tu-app-nombre.railway.app
```

### 3. Redesplegar el frontend
```bash
# Si usas Vercel
vercel --prod

# O si usas otro servicio, sigue sus instrucciones
```

## 🧪 Verificar el Despliegue

### 1. Probar la API directamente
Visita: `https://tu-app-nombre.railway.app/health`
Deberías ver: `{"status": "healthy", "service": "pdf-exam-generator-api"}`

### 2. Probar el frontend
1. Sube un PDF de prueba
2. Verifica que se generen las preguntas
3. Completa el examen y verifica los resultados

## 🔍 Debugging

### Ver Logs en Railway
1. En el dashboard de Railway
2. Ve a la pestaña "Deployments"
3. Haz clic en el despliegue activo
4. Ve a "Logs" para ver errores

### Logs Comunes
```bash
# Verificar que las dependencias se instalaron
[build] Installing dependencies...

# Verificar que la app se inició
[deploy] Starting uvicorn server...

# Verificar requests
[app] INFO: Processing PDF: documento.pdf, type: test
```

## 🛠️ Solución de Problemas

### Error: "Import errors"
- Verifica que `requirements.txt` esté en la carpeta `api/`
- Asegúrate de que todas las dependencias están listadas

### Error: "Port binding"
- Railway asigna automáticamente el puerto via `$PORT`
- No cambies la configuración de puerto en `main.py`

### Error: "GROQ_API_KEY not found"
- Verifica que la variable de entorno esté configurada en Railway
- Asegúrate de que no hay espacios extra en el valor

### Error: "PDF processing failed"
- Los PDFs de prueba deben tener texto extraíble
- PDFs escaneados (solo imágenes) pueden fallar
- Verifica el tamaño del archivo (máximo 10MB)

## 📊 Monitoreo

### Métricas de Railway
- CPU usage
- Memory usage
- Request count
- Response times

### Health Check
La API incluye un endpoint `/health` para monitoreo automático.

## 🔄 Actualizaciones

Para actualizar la API:
```bash
# 1. Hacer cambios en api/main.py
# 2. Commit y push
git add .
git commit -m "Update API"
git push origin main

# 3. Railway redesplegará automáticamente
```

## 💡 Optimizaciones Adicionales

### 1. Caching
```python
# Agregar en main.py si es necesario
from functools import lru_cache

@lru_cache(maxsize=100)
def cache_pdf_content(file_hash: str):
    # Implementar cache de contenido PDF
    pass
```

### 2. Rate Limiting
```python
# Agregar en main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/generate-questions")
@limiter.limit("5/minute")  # 5 requests por minuto
async def generate_questions(...):
    # función existente
```

### 3. Logging Avanzado
```python
# Agregar en main.py
import structlog

logger = structlog.get_logger()
```
