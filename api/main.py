from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pdfplumber
import tempfile
import os
from typing import List, Optional
import json
from groq import Groq
import logging
from PIL import Image
import pytesseract

# Cargar variables de entorno desde .env en desarrollo
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
    print(f"✅ GROQ_API_KEY configured: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables")
except Exception as e:
    print(f"❌ Error loading .env file: {e}")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Exam Generator API", version="1.0.0")

# Manejador de errores de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error on {request.method} {request.url}")
    logger.error(f"Validation errors: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "message": "Request validation failed"}
    )

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
    answer: Optional[str] = None  # Para preguntas de múltiple opción
    textAnswer: Optional[str] = None  # Para preguntas de desarrollo
    
    def get_answer(self) -> str:
        """Retorna la respuesta, sin importar si es answer o textAnswer"""
        return self.answer or self.textAnswer or ""

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
    
    # Configurar cliente con la nueva sintaxis
    os.environ["GROQ_API_KEY"] = api_key  # Asegurar que esté en environment
    return Groq()  # Sintaxis simplificada como en tu ejemplo

@app.get("/")
async def root():
    return {"message": "PDF Exam Generator API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "pdf-exam-generator-api"}

@app.post("/extract-text-from-image")
async def extract_text_from_image(
    image: UploadFile = File(...)
):
    """
    Extrae texto de una imagen usando OCR con Tesseract
    """
    try:
        logger.info(f"Processing image: {image.filename}")
        
        # Validar que sea una imagen
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        
        # Validar tamaño (5MB máximo)
        content = await image.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400, 
                detail=f"Image too large ({len(content)/1024/1024:.1f}MB). Maximum 5MB allowed."
            )
        
        # Procesar imagen con OCR
        temp_file_path = None
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_file.write(content)
                temp_file.flush()
                temp_file_path = temp_file.name
            
            # Abrir imagen con PIL
            img = Image.open(temp_file_path)
            
            # Intentar usar Tesseract si está disponible
            try:
                # Configurar la ruta de Tesseract para Windows
                import os
                tesseract_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
                ]
                
                # Encontrar y configurar Tesseract
                for path in tesseract_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        logger.info(f"Using Tesseract from: {path}")
                        break
                else:
                    # Si no se encuentra en las rutas estándar, confiar en el PATH
                    logger.info("Using Tesseract from PATH")
                
                # Configurar Tesseract para español e inglés
                custom_config = r'--oem 3 --psm 6 -l spa+eng'
                
                # Extraer texto
                extracted_text = pytesseract.image_to_string(img, config=custom_config)
                
                logger.info(f"Extracted {len(extracted_text)} characters from image")
                
                if len(extracted_text.strip()) < 10:
                    raise HTTPException(
                        status_code=422,
                        detail="Could not extract sufficient text from image. Make sure the image contains clear, readable text."
                    )
                
                return {
                    "text": extracted_text.strip(),
                    "length": len(extracted_text.strip())
                }
                
            except Exception as tesseract_error:
                logger.warning(f"Tesseract not available: {tesseract_error}")
                # Fallback para desarrollo local sin Tesseract
                raise HTTPException(
                    status_code=501, 
                    detail="OCR service not available in development mode. Tesseract OCR is required for image processing. Please install Tesseract or deploy to Railway where it's pre-installed."
                )
                
        finally:
            # Limpiar archivo temporal con manejo robusto de errores
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except (PermissionError, OSError) as e:
                    logger.warning(f"Could not delete temporary file {temp_file_path}: {e}")
                    # En Windows, a veces necesitamos esperar un poco
                    import time
                    time.sleep(0.1)
                    try:
                        os.unlink(temp_file_path)
                    except (PermissionError, OSError):
                        logger.warning(f"Temporary file {temp_file_path} will be cleaned up by system")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR error: {e}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

@app.post("/extract-text-from-pdf")
async def extract_text_from_pdf(pdf: UploadFile = File(...)):
    """Extraer texto de un archivo PDF"""
    try:
        logger.info(f"Processing PDF: {pdf.filename}")
        
        # Validar que sea un PDF
        if not pdf.filename or not pdf.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Crear archivo temporal
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                content = await pdf.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Extraer texto usando pdfplumber
            pdf_content = ""
            with pdfplumber.open(temp_file_path) as pdf_file:
                for page in pdf_file.pages:
                    text = page.extract_text()
                    if text:
                        pdf_content += text + "\n"
            
            if len(pdf_content.strip()) < 10:
                raise HTTPException(
                    status_code=422,
                    detail="Could not extract text from PDF. The file may be scanned images or corrupted."
                )
            
            logger.info(f"Successfully extracted {len(pdf_content)} characters from PDF")
            
            return {
                "text": pdf_content.strip(),
                "length": len(pdf_content.strip()),
                "filename": pdf.filename
            }
            
        finally:
            # Limpiar archivo temporal
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except (PermissionError, OSError) as e:
                    logger.warning(f"Could not delete temporary file {temp_file_path}: {e}")
                    import time
                    time.sleep(0.1)
                    try:
                        os.unlink(temp_file_path)
                    except (PermissionError, OSError):
                        logger.warning(f"Temporary file {temp_file_path} will be cleaned up by system")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")

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
        logger.info(f"Received examType value: '{examType}' (type: {type(examType)})")
        
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
        temp_file_path = None
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(content)
                temp_file.flush()
                temp_file_path = temp_file.name
            
            # Procesar PDF
            with pdfplumber.open(temp_file_path) as pdf_doc:
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
            # Limpiar archivo temporal con manejo robusto de errores
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except (PermissionError, OSError) as e:
                    logger.warning(f"Could not delete temporary file {temp_file_path}: {e}")
                    # En Windows, a veces necesitamos esperar un poco
                    import time
                    time.sleep(0.1)
                    try:
                        os.unlink(temp_file_path)
                    except (PermissionError, OSError):
                        logger.warning(f"Temporary file {temp_file_path} will be cleaned up by system")
        
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
        logger.info(f"Checking examType condition: examType='{examType}', examType == 'test': {examType == 'test'}")
        
        if examType == "test":
            logger.info("Using MULTIPLE CHOICE prompt for test type")
            prompt = f"""
IMPORTANTE: Debes crear preguntas de MÚLTIPLE OPCIÓN (Multiple Choice). NO generes preguntas de desarrollo o abiertas.

Basándote en el siguiente contenido de un PDF educativo, crea exactamente 20 preguntas de múltiple opción en formato JSON.

Contenido del PDF:
{pdf_content}

Instrucciones OBLIGATORIAS:
1. Crea EXACTAMENTE 20 preguntas de MÚLTIPLE OPCIÓN (no preguntas abiertas)
2. Cada pregunta DEBE tener exactamente 4 opciones: A, B, C, D
3. Cada pregunta DEBE incluir el campo "options" con las 4 opciones
4. Incluye la respuesta correcta (A, B, C o D) y una explicación detallada
5. Las preguntas deben ser de diferentes niveles de dificultad
6. Asegúrate de que solo una opción sea correcta

Formato JSON OBLIGATORIO (ejemplo):
{{
  "questions": [
    {{
      "id": 1,
      "question": "¿Cuál de las siguientes opciones es correcta sobre el tema X?",
      "options": ["Opción A - Primera respuesta", "Opción B - Segunda respuesta", "Opción C - Tercera respuesta", "Opción D - Cuarta respuesta"],
      "correct_answer": "A",
      "explanation": "Explicación detallada de por qué la opción A es correcta"
    }}
  ]
}}

RECUERDA: Debes generar 20 preguntas de MÚLTIPLE OPCIÓN con el formato exacto mostrado arriba.
"""
        else:  # development
            logger.info("Using DEVELOPMENT prompt for development type")
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
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=6000  # Aumentado para acomodar 20 preguntas de múltiple opción
        )
        
        # Parsear respuesta JSON
        try:
            raw_content = response.choices[0].message.content
            logger.info(f"Raw response from Groq (first 500 chars): {raw_content[:500]}...")
            
            if not raw_content or raw_content.strip() == "":
                logger.error("Groq returned empty response")
                raise HTTPException(status_code=500, detail="Groq returned empty response")
            
            # Extraer JSON del markdown si está envuelto en ```json
            json_content = raw_content
            if "```json" in raw_content:
                # Encontrar el contenido entre ```json y ```
                start_marker = "```json"
                end_marker = "```"
                start_idx = raw_content.find(start_marker)
                if start_idx != -1:
                    start_idx += len(start_marker)
                    end_idx = raw_content.find(end_marker, start_idx)
                    if end_idx != -1:
                        json_content = raw_content[start_idx:end_idx].strip()
                        logger.info(f"Extracted JSON from markdown wrapper")
            
            questions_data = json.loads(json_content)
            
            # Verificar si las preguntas tienen el formato correcto
            if 'questions' in questions_data:
                sample_question = questions_data['questions'][0] if questions_data['questions'] else {}
                has_options = 'options' in sample_question
                logger.info(f"Question format check - Has options: {has_options}")
                if has_options:
                    logger.info(f"Sample question: {sample_question.get('question', 'N/A')}")
                    logger.info(f"Sample options: {sample_question.get('options', 'N/A')}")
                else:
                    logger.warning("Generated questions do NOT have options field - this might be development questions instead of multiple choice!")
            
            logger.info(f"Generated {len(questions_data['questions'])} questions")
            return questions_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq response as JSON: {e}")
            logger.error(f"Raw content that failed to parse: '{raw_content[:500]}...'")
            logger.error(f"Extracted JSON content: '{json_content[:500]}...'")
            
            # Si el JSON está incompleto y estamos generando preguntas de test, reintentar con menos
            if examType == "test" and "Expecting" in str(e):
                logger.info("JSON appears incomplete, retrying with 10 questions instead of 20...")
                
                # Regenerar prompt con menos preguntas
                reduced_prompt = prompt.replace("exactamente 20 preguntas", "exactamente 10 preguntas").replace("20 preguntas", "10 preguntas")
                
                try:
                    response = client.chat.completions.create(
                        model="deepseek-r1-distill-llama-70b",
                        messages=[{"role": "user", "content": reduced_prompt}],
                        temperature=0.7,
                        max_tokens=6000
                    )
                    
                    raw_content = response.choices[0].message.content
                    logger.info("Retry successful with reduced questions")
                    
                    # Procesar la respuesta del retry
                    json_content = raw_content
                    if "```json" in raw_content:
                        start_marker = "```json"
                        end_marker = "```"
                        start_idx = raw_content.find(start_marker)
                        if start_idx != -1:
                            start_idx += len(start_marker)
                            end_idx = raw_content.find(end_marker, start_idx)
                            if end_idx != -1:
                                json_content = raw_content[start_idx:end_idx].strip()
                    
                    questions_data = json.loads(json_content)
                    
                    # Verificar formato de preguntas
                    if 'questions' in questions_data:
                        sample_question = questions_data['questions'][0] if questions_data['questions'] else {}
                        has_options = 'options' in sample_question
                        logger.info(f"Retry - Question format check - Has options: {has_options}")
                    
                    logger.info(f"Generated {len(questions_data['questions'])} questions (after retry)")
                    return questions_data
                    
                except Exception as retry_error:
                    logger.error(f"Retry also failed: {retry_error}")
                    # Continuar con el error original
            
            raise HTTPException(status_code=500, detail="Failed to generate valid questions - JSON parsing error")
        
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
        logger.info(f"Grading exam with {len(request.questions)} questions and {len(request.userAnswers)} answers")
        
        # Debug: log the received data
        logger.info(f"Questions received: {[{'id': q.id, 'has_options': q.options is not None} for q in request.questions]}")
        logger.info(f"User answers received: {[{'questionId': a.questionId, 'answer_length': len(a.get_answer())} for a in request.userAnswers]}")
        
        results = []
        development_questions = []
        development_answers = []
        
        # Procesar cada pregunta
        for question in request.questions:
            user_answer = next((a for a in request.userAnswers if a.questionId == question.id), None)
            if not user_answer:
                continue
                
            if question.options:  # Pregunta de múltiple opción
                # Calificación local - no necesita IA
                user_response = user_answer.get_answer().strip().upper()
                correct_answer = question.correct_answer.strip().upper()
                is_correct = user_response == correct_answer
                
                result = ExamResult(
                    questionId=question.id,
                    userAnswer=user_response,
                    correctAnswer=correct_answer,
                    explanation=question.explanation,
                    isCorrect=is_correct
                )
                results.append(result)
                logger.info(f"Multiple choice Q{question.id}: {user_response} vs {correct_answer} = {'✓' if is_correct else '✗'}")
                
            else:  # Pregunta de desarrollo
                # Estas necesitan IA para calificar
                development_questions.append(question)
                development_answers.append(user_answer)
        
        # Si hay preguntas de desarrollo, calificarlas con IA
        if development_questions:
            logger.info(f"Sending {len(development_questions)} development questions to AI for grading...")
            client = get_groq_client()
            
            # Preparar datos solo para preguntas de desarrollo
            exam_data = {
                "questions": [q.dict() for q in development_questions],
                "user_answers": [{"questionId": a.questionId, "answer": a.get_answer()} for a in development_answers]
            }
        
            prompt = f"""
Califica estas preguntas de DESARROLLO (abiertas) y proporciona retroalimentación detallada en formato JSON.

Datos del examen:
{json.dumps(exam_data, ensure_ascii=False, indent=2)}

Instrucciones:
1. Estas son todas preguntas de desarrollo (abiertas), no de múltiple opción
2. Califica cada respuesta del 0 al 100 basándote en:
   - Precisión del contenido
   - Comprensión del tema
   - Completitud de la respuesta
   - Uso correcto de terminología
3. Proporciona explicación detallada de la calificación
4. Indica si la respuesta es correcta (score >= 60) o incorrecta (score < 60)

Formato JSON requerido:
{{
  "results": [
    {{
      "questionId": 1,
      "userAnswer": "respuesta del usuario",
      "correctAnswer": "respuesta modelo esperada",
      "explanation": "Explicación detallada de la calificación y qué se esperaba",
      "isCorrect": true/false,
      "score": 85
    }}
  ]
}}
"""
            
            response = client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=3000
            )
            
            # Parsear respuesta de IA para preguntas de desarrollo
            try:
                raw_content = response.choices[0].message.content
                
                # Extraer JSON del markdown si está envuelto
                json_content = raw_content
                if "```json" in raw_content:
                    start_marker = "```json"
                    end_marker = "```"
                    start_idx = raw_content.find(start_marker)
                    if start_idx != -1:
                        start_idx += len(start_marker)
                        end_idx = raw_content.find(end_marker, start_idx)
                        if end_idx != -1:
                            json_content = raw_content[start_idx:end_idx].strip()
                
                ai_results = json.loads(json_content)
                
                # Convertir resultados de IA al formato ExamResult
                for ai_result in ai_results.get("results", []):
                    result = ExamResult(
                        questionId=ai_result["questionId"],
                        userAnswer=ai_result["userAnswer"],
                        correctAnswer=ai_result["correctAnswer"],
                        explanation=ai_result["explanation"],
                        isCorrect=ai_result["isCorrect"],
                        score=ai_result.get("score")
                    )
                    results.append(result)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI grading response: {e}")
                # Crear resultados de fallback para preguntas de desarrollo
                for question in development_questions:
                    user_answer = next((a for a in development_answers if a.questionId == question.id), None)
                    result = ExamResult(
                        questionId=question.id,
                        userAnswer=user_answer.get_answer() if user_answer else "",
                        correctAnswer="Error en la calificación automática",
                        explanation="Hubo un error al procesar la calificación. Por favor, revisa tu respuesta manualmente.",
                        isCorrect=False
                    )
                    results.append(result)
        
        # Ordenar resultados por questionId
        results.sort(key=lambda x: x.questionId)
        logger.info(f"Graded {len(results)} answers total")
        
        return {"results": results}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in grading: {e}")
        raise HTTPException(status_code=500, detail=f"Grading error: {str(e)}")

# Modelo para comentario literario
class LiteraryCommentaryRequest(BaseModel):
    text: str

@app.post("/generate-literary-commentary")
async def generate_literary_commentary(request: LiteraryCommentaryRequest):
    try:
        logger.info("Starting literary commentary generation")
        
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Preparar el prompt para el comentario literario
        system_prompt = """Eres un estudiante universitario de Literatura de Asia Oriental de entre 18-24 años, con conocimientos sólidos pero con un estilo de escritura fresco y accesible. Tu especialización incluye literatura china, japonesa, coreana y de otras culturas asiáticas.

Cuando analices textos, documentos, relatos e historias de literatura de Asia Oriental, debes:

1. **Análisis del contenido**: Identifica temas, filosofías orientales (confucianismo, budismo, taoísmo), valores culturales asiáticos, y el mensaje del autor
2. **Análisis de la forma**: Reconoce géneros literarios asiáticos (haiku, wuxia, novela histórica china, etc.), estructura narrativa, y técnicas estilísticas orientales
3. **Análisis del lenguaje**: Registro, uso de metáforas asiáticas, simbolismo cultural, y recursos retóricos típicos de Asia Oriental
4. **Interpretación cultural**: Contexto histórico asiático, influencias de dinastías, periodos, filosofías orientales, y valor estético en la tradición literaria asiática

Escribe como un universitario apasionado por la literatura asiática: usa un lenguaje académico pero natural, incluye observaciones personales, y conecta el texto con la rica tradición literaria de Asia Oriental. Sé específico sobre elementos culturales asiáticos cuando sea pertinente.

IMPORTANTE: Responde directamente con el análisis literario. NO incluyas etiquetas como <think>, procesos de pensamiento, ni explicaciones sobre cómo vas a estructurar tu respuesta."""

        user_prompt = f"""Como estudiante universitario especializado en Literatura de Asia Oriental, analiza este texto/relato/documento literario:

"{request.text}"

Proporciona un comentario literario académico pero accesible, enfocándote en elementos culturales, filosóficos y literarios típicos de Asia Oriental. Escribe con el entusiasmo y la perspectiva fresca de un universitario apasionado por la literatura asiática."""

        # Llamar a la API de Groq
        client = get_groq_client()
        response = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        
        commentary = response.choices[0].message.content.strip()
        
        # Limpiar cualquier etiqueta de pensamiento interno que pueda aparecer
        import re
        commentary = re.sub(r'<think>.*?</think>', '', commentary, flags=re.DOTALL)
        commentary = re.sub(r'<thinking>.*?</thinking>', '', commentary, flags=re.DOTALL)
        commentary = commentary.strip()
        
        logger.info("Literary commentary generated successfully")
        
        return {
            "commentary": commentary,
            "word_count": len(commentary.split()),
            "original_text_length": len(request.text)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating literary commentary: {e}")
        raise HTTPException(status_code=500, detail=f"Commentary generation error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Usar el puerto proporcionado por Railway o 8000 por defecto para desarrollo local
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(app, host="0.0.0.0", port=port)
