from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pdfplumber
import tempfile
import os
from typing import List, Optional
import json
from groq import Groq
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Exam Generator API", version="1.0.0")

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar el dominio exacto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class Question(BaseModel):
    id: int
    question: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str

class UserAnswer(BaseModel):
    questionId: int
    answer: str

class GradeRequest(BaseModel):
    questions: List[Question]
    userAnswers: List[UserAnswer]

class ExamResult(BaseModel):
    questionId: int
    userAnswer: str
    correctAnswer: str
    explanation: str
    isCorrect: bool
    score: Optional[int] = None

# Configurar cliente Groq
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
    return Groq(api_key=api_key)

@app.get("/")
async def root():
    return {"message": "PDF Exam Generator API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "pdf-exam-generator-api"}

@app.post("/generate-questions")
async def generate_questions(
    pdf: UploadFile = File(...),
    examType: str = Form("test"),
    randomSeed: str = Form(None)
):
    """
    Genera preguntas basadas en un PDF usando pdfplumber + Groq AI
    """
    try:
        logger.info(f"Processing PDF: {pdf.filename}, type: {examType}")
        
        # Validar archivo PDF
        if not pdf.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Validar tamaño (10MB máximo)
        content = await pdf.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large ({len(content)/1024/1024:.1f}MB). Maximum 10MB allowed."
            )
        
        # Extraer texto del PDF usando pdfplumber
        pdf_content = ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(content)
            temp_file.flush()
            
            try:
                with pdfplumber.open(temp_file.name) as pdf_doc:
                    logger.info(f"PDF opened successfully. Pages: {len(pdf_doc.pages)}")
                    
                    # Extraer texto de todas las páginas
                    for page_num, page in enumerate(pdf_doc.pages, 1):
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                pdf_content += f"\n\n--- Página {page_num} ---\n{page_text}"
                                logger.info(f"Page {page_num}: {len(page_text)} characters extracted")
                        except Exception as page_error:
                            logger.warning(f"Error extracting text from page {page_num}: {page_error}")
                            continue
                    
            finally:
                # Limpiar archivo temporal
                os.unlink(temp_file.name)
        
        if len(pdf_content.strip()) < 100:
            raise HTTPException(
                status_code=422,
                detail="Could not extract sufficient text from PDF. The file may be scanned images or corrupted."
            )
        
        logger.info(f"Successfully extracted {len(pdf_content)} characters from PDF")
        
        # Generar preguntas usando Groq
        client = get_groq_client()
        
        # Limitar el contenido para evitar exceder límites de tokens
        max_content_length = 6000
        if len(pdf_content) > max_content_length:
            pdf_content = pdf_content[:max_content_length] + "..."
            logger.info(f"Content truncated to {max_content_length} characters")
        
        # Prompt según el tipo de examen
        if examType == "test":
            prompt = f"""
Basándote en el siguiente contenido de un PDF educativo, crea exactamente 20 preguntas de múltiple opción en formato JSON.

Contenido del PDF:
{pdf_content}

Instrucciones:
1. Crea 20 preguntas variadas que cubran diferentes aspectos del contenido
2. Cada pregunta debe tener 4 opciones (A, B, C, D)
3. Incluye la respuesta correcta y una explicación detallada
4. Las preguntas deben ser de diferentes niveles de dificultad
5. Asegúrate de que solo una opción sea correcta

Formato JSON requerido:
{{
  "questions": [
    {{
      "id": 1,
      "question": "Texto de la pregunta",
      "options": ["Opción A", "Opción B", "Opción C", "Opción D"],
      "correct_answer": "A",
      "explanation": "Explicación detallada de por qué esta es la respuesta correcta"
    }}
  ]
}}
"""
        else:  # development
            prompt = f"""
Basándote en el siguiente contenido de un PDF educativo, crea exactamente 5 preguntas de desarrollo en formato JSON.

Contenido del PDF:
{pdf_content}

Instrucciones:
1. Crea 5 preguntas abiertas que requieran análisis y comprensión profunda
2. No incluyas opciones múltiples
3. Proporciona una respuesta modelo detallada
4. Las preguntas deben fomentar el pensamiento crítico

Formato JSON requerido:
{{
  "questions": [
    {{
      "id": 1,
      "question": "Pregunta que requiere desarrollo y análisis",
      "correct_answer": "Respuesta modelo detallada que explique los conceptos clave",
      "explanation": "Criterios de evaluación y puntos importantes a considerar"
    }}
  ]
}}
"""
        
        # Hacer request a Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000
        )
        
        # Parsear respuesta JSON
        try:
            questions_data = json.loads(response.choices[0].message.content)
            logger.info(f"Generated {len(questions_data['questions'])} questions")
            return questions_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq response as JSON: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate valid questions")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/grade-exam")
async def grade_exam(request: GradeRequest):
    """
    Califica las respuestas del examen usando Groq AI
    """
    try:
        logger.info(f"Grading exam with {len(request.questions)} questions")
        
        client = get_groq_client()
        
        # Preparar datos para la calificación
        exam_data = {
            "questions": [q.dict() for q in request.questions],
            "user_answers": [a.dict() for a in request.userAnswers]
        }
        
        prompt = f"""
Califica este examen y proporciona retroalimentación detallada en formato JSON.

Datos del examen:
{json.dumps(exam_data, ensure_ascii=False, indent=2)}

Instrucciones:
1. Para preguntas de múltiple opción: marca como correcto/incorrecto
2. Para preguntas de desarrollo: asigna una puntuación de 0-100 basada en la calidad de la respuesta
3. Proporciona explicaciones detalladas para cada respuesta
4. Se constructivo en la retroalimentación

Formato JSON requerido:
{{
  "results": [
    {{
      "questionId": 1,
      "userAnswer": "respuesta del usuario",
      "correctAnswer": "respuesta correcta",
      "explanation": "explicación detallada",
      "isCorrect": true/false,
      "score": 100 (solo para preguntas de desarrollo, opcional para múltiple opción)
    }}
  ]
}}
"""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=3000
        )
        
        try:
            results_data = json.loads(response.choices[0].message.content)
            logger.info(f"Graded {len(results_data['results'])} answers")
            return results_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse grading response as JSON: {e}")
            raise HTTPException(status_code=500, detail="Failed to grade exam")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in grading: {e}")
        raise HTTPException(status_code=500, detail=f"Grading error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
