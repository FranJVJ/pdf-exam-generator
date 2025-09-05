#!/usr/bin/env python3
# Verificar versión de Groq y probar inicialización

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️ python-dotenv not available")

try:
    import groq
    print(f"✅ Groq version: {groq.__version__}")
    
    # Probar inicialización básica
    client = groq.Groq()
    print("✅ Groq client initialized successfully")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
