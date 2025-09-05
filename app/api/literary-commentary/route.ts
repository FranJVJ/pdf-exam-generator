import { type NextRequest, NextResponse } from "next/server"
import { generateText } from "ai"
import { groq } from "@ai-sdk/groq"

export async function POST(request: NextRequest) {
  try {
    // Verificar que la API key de Groq esté configurada
    if (!process.env.GROQ_API_KEY) {
      return NextResponse.json(
        { 
          error: "Groq API key not configured. Please add GROQ_API_KEY to your .env.local file.",
          instructions: "1. Go to https://console.groq.com/\n2. Create a free account\n3. Generate an API key\n4. Add GROQ_API_KEY=your_key_here to .env.local"
        }, 
        { status: 500 }
      )
    }

    let text: string;
    const contentType = request.headers.get('content-type');

    if (contentType?.includes('application/json')) {
      // Modo texto: recibir JSON
      const body = await request.json();
      text = body.text;
    } else if (contentType?.includes('multipart/form-data')) {
      // Modo PDF: procesar FormData
      const formData = await request.formData();
      const file = formData.get('pdf') as File;
      
      if (!file) {
        return NextResponse.json(
          { error: "No PDF file provided" }, 
          { status: 400 }
        );
      }

      // Validar tamaño del archivo (10MB máximo)
      if (file.size > 10 * 1024 * 1024) {
        return NextResponse.json(
          { error: "El archivo PDF es demasiado grande. Máximo 10MB." }, 
          { status: 400 }
        );
      }

      // En producción (Vercel), usar fallback honesto
      if (process.env.VERCEL) {
        return NextResponse.json(
          { 
            error: "Procesamiento de PDF no disponible en la versión online",
            suggestion: "Por limitaciones técnicas del servidor de producción, el análisis de PDFs solo está disponible en desarrollo local. Por favor, copia el texto del PDF y úsalo en el modo 'Escribir texto'."
          }, 
          { status: 400 }
        );
      }

      // En desarrollo local, procesar con pdfplumber
      try {
        const arrayBuffer = await file.arrayBuffer();
        const buffer = Buffer.from(arrayBuffer);
        
        const tempDir = 'temp';
        const fs = await import('fs');
        const path = await import('path');
        const { exec } = await import('child_process');
        const { promisify } = await import('util');
        const execAsync = promisify(exec);
        
        // Crear directorio temporal si no existe
        if (!fs.existsSync(tempDir)) {
          fs.mkdirSync(tempDir, { recursive: true });
        }
        
        // Generar nombre único para el archivo temporal
        const tempFileName = `temp_literary_${Date.now()}_${Math.random().toString(36).substr(2, 9)}.pdf`;
        const tempFilePath = path.join(tempDir, tempFileName);
        
        try {
          // Escribir el archivo PDF temporal
          fs.writeFileSync(tempFilePath, buffer);
          
          // Ejecutar el script Python para extraer texto
          const pythonPath = 'F:/KPOP/pdf-exam-generator/.venv/Scripts/python.exe';
          const scriptPath = 'pdf_extractor.py';
          const command = `"${pythonPath}" "${scriptPath}" "${tempFilePath}"`;
          
          console.log('Executing literary PDF extraction:', command);
          
          const { stdout, stderr } = await execAsync(command, {
            cwd: process.cwd(),
            timeout: 30000 // 30 segundos timeout
          });
          
          if (stderr) {
            console.warn('Python stderr:', stderr);
          }
          
          // Parsear el resultado JSON del script Python
          const result = JSON.parse(stdout);
          
          if (!result.success) {
            throw new Error(result.error || 'Failed to extract text from PDF');
          }
          
          text = result.text;
          
        } finally {
          // Limpiar archivo temporal
          try {
            if (fs.existsSync(tempFilePath)) {
              fs.unlinkSync(tempFilePath);
            }
          } catch (cleanupError) {
            console.warn('Error cleaning up temp file:', cleanupError);
          }
        }

        if (!text || text.trim().length < 30) {
          return NextResponse.json(
            { 
              error: "No se pudo extraer texto suficiente del PDF",
              suggestion: "El PDF podría estar vacío, ser una imagen, o tener texto no seleccionable. Intenta copiar el texto manualmente y usar el modo 'Escribir texto'."
            }, 
            { status: 400 }
          );
        }

      } catch (error) {
        console.error('Error procesando PDF:', error);
        return NextResponse.json(
          { 
            error: "Error procesando el PDF",
            suggestion: "Hubo un problema técnico procesando el archivo. Intenta copiar el texto manualmente y usar el modo 'Escribir texto'."
          }, 
          { status: 500 }
        );
      }
    } else {
      return NextResponse.json(
        { error: "Invalid content type" }, 
        { status: 400 }
      );
    }

    if (!text || typeof text !== 'string' || text.trim().length === 0) {
      return NextResponse.json(
        { error: "No text provided for literary commentary" }, 
        { status: 400 }
      )
    }

    // Verificar longitud mínima y máxima
    if (text.trim().length < 50) {
      return NextResponse.json(
        { error: "El texto debe tener al menos 50 caracteres para generar un comentario significativo" }, 
        { status: 400 }
      )
    }

    if (text.length > 8000) {
      return NextResponse.json(
        { error: "El texto es demasiado largo. Máximo 8000 caracteres." }, 
        { status: 400 }
      )
    }

    console.log('Generating literary commentary for text length:', text.length)

    // Generar comentario literario con Groq
    const prompt = `Eres un experto en literatura de Asia Oriental (China, Japón, Corea, Sudeste Asiático). Tu tarea es realizar un comentario literario profundo y académico del siguiente texto.

TEXTO A ANALIZAR:
"${text}"

Proporciona un comentario literario completo que incluya:

1. **ANÁLISIS TEMÁTICO**: 
   - Identifica y explica los temas principales y secundarios
   - Analiza cómo se desarrollan estos temas a lo largo del texto

2. **ESTILO Y TÉCNICA NARRATIVA**:
   - Examina el estilo de escritura, tono y registro
   - Identifica recursos literarios utilizados (metáforas, símiles, etc.)
   - Analiza la estructura narrativa y técnicas empleadas

3. **CONTEXTO CULTURAL Y HISTÓRICO**:
   - Sitúa el texto en su contexto cultural asiático
   - Explica referencias históricas, filosóficas o culturales relevantes
   - Identifica elementos específicos de la tradición literaria asiática

4. **INTERPRETACIÓN Y SIGNIFICADO**:
   - Proporciona una interpretación profunda del significado
   - Analiza simbolismos y elementos alegóricos
   - Explica la relevancia y mensaje del texto

5. **CARACTERÍSTICAS ESPECÍFICAS**:
   - Si es posible, identifica elementos típicos de la literatura del país/región específica
   - Comenta sobre influencias filosóficas (confucianismo, budismo, taoísmo, etc.)

INSTRUCCIONES DE ESTILO:
- **HUMANIZA EL TEXTO**: Escribe de manera natural y fluida, evitando un tono robótico o mecánico
- Usa un lenguaje académico pero accesible y conversacional
- Incluye transiciones suaves entre ideas y párrafos
- Varía la longitud y estructura de las oraciones para crear ritmo natural
- Emplea un tono personal y comprometido, como si fueras un profesor apasionado por la literatura
- Evita repeticiones excesivas de palabras y frases formulaicas
- Haz que el análisis fluya naturalmente, conectando ideas de forma orgánica

El comentario debe ser académico pero engagador, con aproximadamente 400-600 palabras. Mantén un equilibrio entre rigor académico y humanidad en la escritura.`

    const { text: commentary } = await generateText({
      model: groq("llama-3.3-70b-versatile"),
      prompt: prompt,
      temperature: 0.7,
    })

    if (!commentary || commentary.trim().length === 0) {
      throw new Error("No se pudo generar el comentario literario")
    }

    console.log('Literary commentary generated successfully, length:', commentary.length)

    return NextResponse.json({
      commentary: commentary.trim(),
      metadata: {
        textLength: text.length,
        generatedAt: new Date().toISOString()
      }
    })

  } catch (error) {
    console.error("Error generating literary commentary:", error)
    
    // Manejo específico de errores de Groq
    if (error instanceof Error) {
      if (error.message.includes('rate limit')) {
        return NextResponse.json(
          { 
            error: "Límite de solicitudes alcanzado. Por favor, espera unos minutos antes de intentar de nuevo.",
            retryAfter: 60
          }, 
          { status: 429 }
        )
      }
      
      if (error.message.includes('timeout')) {
        return NextResponse.json(
          { error: "El servidor tardó demasiado en responder. Inténtalo de nuevo." }, 
          { status: 408 }
        )
      }
    }

    return NextResponse.json(
      { 
        error: "Error interno del servidor al generar el comentario literario",
        details: error instanceof Error ? error.message : "Unknown error"
      }, 
      { status: 500 }
    )
  }
}
