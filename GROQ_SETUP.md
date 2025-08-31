# Cómo obtener tu API Key de Groq - GRATIS 🚀

## Paso 1: Registrarse en Groq
1. Ve a [https://console.groq.com/](https://console.groq.com/)
2. Haz clic en "Sign Up" para crear una cuenta
3. Puedes registrarte con:
   - Google
   - GitHub
   - Email

## Paso 2: Verificar tu cuenta
1. Verifica tu email si te registraste con email
2. Accede al dashboard de Groq

## Paso 3: Generar API Key
1. Una vez en el dashboard, ve a "API Keys" en el menú lateral
2. Haz clic en "Create API Key"
3. Dale un nombre a tu clave (ej: "PDF-Exam-Generator")
4. Copia la API key generada ⚠️ **IMPORTANTE: Guárdala inmediatamente, no podrás verla después**

## Paso 4: Configurar en tu proyecto
1. Abre el archivo `.env.local` en la raíz de tu proyecto
2. Reemplaza `your_groq_api_key_here` con tu API key real:
```
GROQ_API_KEY=gsk_tu_api_key_aqui
```

## ¿Por qué Groq es mejor que OpenAI para este proyecto?

### ✅ Ventajas de Groq:
- **100% Gratuito**: Hasta 3,500 requests por día sin costo
- **Ultra-rápido**: Respuestas en milisegundos
- **Sin tarjeta de crédito**: No necesitas agregar método de pago
- **Modelos potentes**: LLaMA 3.1 70B y Mixtral
- **Open Source**: Transparencia total

### ❌ Desventajas de OpenAI:
- **Caro**: Cada request cuesta dinero
- **Requiere tarjeta**: Necesitas método de pago
- **Más lento**: Mayor latencia
- **Límites estrictos**: Rate limiting agresivo para cuentas gratuitas

## Límites de uso gratuito en Groq:
- **Requests por día**: 3,500
- **Tokens por minuto**: 30,000
- **Requests por minuto**: 30

Para la mayoría de casos de uso personales, esto es más que suficiente.

## Troubleshooting

### Error: "Invalid API Key"
- Verifica que copiaste la API key completa
- Asegúrate de que no hay espacios antes o después
- Reinicia el servidor de desarrollo

### Error: "Rate limit exceeded"
- Espera un minuto y vuelve a intentar
- Verifica que no estés haciendo muchos requests seguidos

### ¿No ves el archivo .env.local?
- Asegúrate de estar en la carpeta raíz del proyecto
- En Windows, habilita "Mostrar archivos ocultos"
- El archivo debe estar al mismo nivel que package.json
