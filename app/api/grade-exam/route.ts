import { type NextRequest, NextResponse } from "next/server"
import { generateText } from "ai"
import { groq } from "@ai-sdk/groq"

interface Question {
  id: number
  question: string
  options?: string[]
  correctAnswer?: number
  explanation: string
  type: 'multiple-choice' | 'development'
  expectedAnswer?: string
}

interface UserAnswer {
  questionId: number
  selectedOption?: number
  textAnswer?: string
}

export async function POST(request: NextRequest) {
  try {
    const { questions, userAnswers }: { questions: Question[]; userAnswers: UserAnswer[] } = await request.json()

    // Verificar que tenemos la API key de Groq
    const groqApiKey = process.env.GROQ_API_KEY
    if (!groqApiKey) {
      return NextResponse.json(
        { 
          error: "Groq API key not configured",
          instructions: "Please configure GROQ_API_KEY in .env.local for development question grading"
        }, 
        { status: 500 }
      )
    }

    const results = await Promise.all(
      questions.map(async (question) => {
        const userAnswer = userAnswers.find((answer) => answer.questionId === question.id)

        if (question.type === 'multiple-choice' && question.options && question.correctAnswer !== undefined) {
          // Corrección tradicional para preguntas de múltiple opción
          const isCorrect = userAnswer ? userAnswer.selectedOption === question.correctAnswer : false

          return {
            questionId: question.id,
            isCorrect,
            userAnswer: userAnswer && userAnswer.selectedOption !== undefined ? question.options[userAnswer.selectedOption] : "Sin respuesta",
            correctAnswer: question.options[question.correctAnswer],
            explanation: question.explanation,
            score: isCorrect ? 100 : 0
          }
        } else if (question.type === 'development') {
          // Corrección con IA para preguntas de desarrollo
          const userTextAnswer = userAnswer?.textAnswer || ""

          if (!userTextAnswer.trim()) {
            return {
              questionId: question.id,
              isCorrect: false,
              userAnswer: "Sin respuesta",
              correctAnswer: question.expectedAnswer || "Respuesta esperada no disponible",
              explanation: question.explanation,
              score: 0
            }
          }

          try {
            const { text } = await generateText({
              model: groq("llama-3.3-70b-versatile"),
              prompt: `
                Eres un profesor experto evaluando una pregunta de desarrollo. 
                
                PREGUNTA: ${question.question}
                
                RESPUESTA ESPERADA: ${question.expectedAnswer || question.explanation}
                
                RESPUESTA DEL ESTUDIANTE: ${userTextAnswer}
                
                Evalúa la respuesta del estudiante considerando:
                1. Exactitud conceptual (40%)
                2. Completitud de la respuesta (30%) 
                3. Claridad y organización (20%)
                4. Ejemplos o aplicaciones (10%)
                
                Proporciona:
                - Un puntaje de 0 a 100
                - Retroalimentación constructiva
                - Si es correcta (puntaje >= 60)
                
                Responde ÚNICAMENTE con un JSON válido:
                {
                  "score": 85,
                  "isCorrect": true,
                  "feedback": "Excelente respuesta que demuestra...",
                  "areas_improvement": "Para mejorar podrías..."
                }
              `,
            })

            const evaluation = JSON.parse(text)
            
            return {
              questionId: question.id,
              isCorrect: evaluation.isCorrect,
              userAnswer: userTextAnswer,
              correctAnswer: question.expectedAnswer || "Ver retroalimentación",
              explanation: `${evaluation.feedback}\n\nÁreas de mejora: ${evaluation.areas_improvement}`,
              score: evaluation.score
            }
          } catch (aiError) {
            console.error("Error evaluating development question:", aiError)
            
            // Fallback: evaluación básica por longitud y palabras clave
            const wordCount = userTextAnswer.trim().split(/\s+/).length
            let score = 0
            
            if (wordCount >= 100) score += 40  // Longitud adecuada
            if (wordCount >= 50) score += 20   // Longitud mínima
            if (userTextAnswer.includes("porque") || userTextAnswer.includes("debido")) score += 15  // Explicaciones
            if (userTextAnswer.includes("ejemplo") || userTextAnswer.includes("por ejemplo")) score += 15  // Ejemplos
            if (userTextAnswer.length > 200) score += 10  // Desarrollo extenso
            
            const isCorrect = score >= 60
            
            return {
              questionId: question.id,
              isCorrect,
              userAnswer: userTextAnswer,
              correctAnswer: question.expectedAnswer || "Ver retroalimentación",
              explanation: `Evaluación automática: ${isCorrect ? 'Respuesta aceptable' : 'Requiere más desarrollo'}. Se evaluó principalmente la extensión y estructura de la respuesta.`,
              score
            }
          }
        }

        // Fallback para tipos desconocidos
        return {
          questionId: question.id,
          isCorrect: false,
          userAnswer: "Tipo de pregunta no reconocido",
          correctAnswer: "Error en el tipo de pregunta",
          explanation: "Hubo un problema procesando esta pregunta.",
          score: 0
        }
      })
    )

    return NextResponse.json({ results })
  } catch (error) {
    console.error("Error grading exam:", error)
    return NextResponse.json(
      { 
        error: "Failed to grade exam",
        details: error instanceof Error ? error.message : "Unknown error"
      }, 
      { status: 500 }
    )
  }
}
