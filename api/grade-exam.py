from http.server import BaseHTTPRequestHandler
import json
import os
from groq import Groq

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Verificar el Content-Type
            content_type = self.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                # Leer el cuerpo de la petición JSON
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Decodificar con manejo robusto de errores
                try:
                    decoded_data = post_data.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        decoded_data = post_data.decode('latin-1')
                    except UnicodeDecodeError:
                        decoded_data = post_data.decode('utf-8', errors='replace')
                
                request_data = json.loads(decoded_data)
                
                # Obtener preguntas y respuestas del usuario
                questions = request_data.get('questions', [])
                user_answers = request_data.get('userAnswers', [])
                
                if not questions or not user_answers:
                    self._send_error_response(400, "Questions and userAnswers are required")
                    return
                
                # Procesar cada pregunta
                results = []
                development_questions = []
                development_answers = []
                
                for question in questions:
                    # Buscar la respuesta del usuario para esta pregunta
                    user_answer = None
                    for answer in user_answers:
                        if answer.get('questionId') == question.get('id'):
                            user_answer = answer
                            break
                    
                    if not user_answer:
                        continue
                    
                    # Verificar si es pregunta de múltiple opción
                    if question.get('options'):  # Pregunta de múltiple opción
                        # Calificación local - no necesita IA
                        user_response = str(user_answer.get('answer', user_answer.get('textAnswer', ''))).strip().upper()
                        correct_answer = str(question.get('correct_answer', question.get('correctAnswer', ''))).strip().upper()
                        
                        # También verificar si es un índice numérico
                        if user_response.isdigit():
                            try:
                                option_index = int(user_response)
                                if 0 <= option_index < len(question['options']):
                                    # Convertir índice a letra (0=A, 1=B, etc.)
                                    user_response = chr(65 + option_index)  # 65 es 'A' en ASCII
                            except (ValueError, IndexError):
                                pass
                        
                        # También verificar si correct_answer es un índice
                        if correct_answer.isdigit():
                            try:
                                option_index = int(correct_answer)
                                if 0 <= option_index < len(question['options']):
                                    correct_answer = chr(65 + option_index)
                            except (ValueError, IndexError):
                                pass
                        
                        is_correct = user_response == correct_answer
                        
                        result = {
                            "questionId": question['id'],
                            "userAnswer": user_response,
                            "correctAnswer": correct_answer,
                            "explanation": question.get('explanation', ''),
                            "isCorrect": is_correct
                        }
                        results.append(result)
                        
                    else:  # Pregunta de desarrollo
                        development_questions.append(question)
                        development_answers.append(user_answer)
                
                # Si hay preguntas de desarrollo, calificarlas con IA
                if development_questions:
                    # Configurar Groq
                    groq_api_key = os.getenv("GROQ_API_KEY")
                    if not groq_api_key:
                        self._send_error_response(500, "GROQ_API_KEY not configured for development questions grading")
                        return
                    
                    try:
                        client = Groq(api_key=groq_api_key)
                    except Exception as groq_init_error:
                        self._send_error_response(500, f"Failed to initialize Groq client: {str(groq_init_error)}")
                        return
                    
                    # Preparar datos para IA
                    exam_data = {
                        "questions": development_questions,
                        "user_answers": [{"questionId": a.get('questionId'), "answer": a.get('answer', a.get('textAnswer', ''))} for a in development_answers]
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
                    
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.3,
                            max_tokens=3000
                        )
                        
                        raw_content = response.choices[0].message.content.strip()
                        
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
                        
                        # Agregar resultados de IA
                        for ai_result in ai_results.get("results", []):
                            results.append(ai_result)
                            
                    except Exception as ai_error:
                        # Crear resultados de fallback para preguntas de desarrollo
                        for i, question in enumerate(development_questions):
                            user_answer = development_answers[i] if i < len(development_answers) else {}
                            result = {
                                "questionId": question['id'],
                                "userAnswer": user_answer.get('answer', user_answer.get('textAnswer', '')),
                                "correctAnswer": "Error en la calificación automática",
                                "explanation": f"Hubo un error al procesar la calificación: {str(ai_error)}",
                                "isCorrect": False
                            }
                            results.append(result)
                
                # Ordenar resultados por questionId
                results.sort(key=lambda x: x.get('questionId', 0))
                
                # Enviar respuesta exitosa
                self._send_success_response({"results": results})
                
            else:
                self._send_error_response(400, "Content-Type must be application/json")
                
        except json.JSONDecodeError as json_error:
            self._send_error_response(400, f"Invalid JSON in request: {str(json_error)}")
        except Exception as e:
            self._send_error_response(500, f"Error grading exam: {str(e)}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_success_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())