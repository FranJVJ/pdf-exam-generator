from http.server import BaseHTTPRequestHandler
import json
import os
from groq import Groq

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Leer el cuerpo de la petición
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Decodificar con manejo robusto de errores
            try:
                decoded_data = post_data.decode('utf-8')
            except UnicodeDecodeError:
                # Intentar con otras codificaciones comunes
                try:
                    decoded_data = post_data.decode('latin-1')
                except UnicodeDecodeError:
                    try:
                        decoded_data = post_data.decode('utf-8', errors='replace')
                    except UnicodeDecodeError:
                        decoded_data = post_data.decode('ascii', errors='ignore')
            
            request_data = json.loads(decoded_data)
            
            # Obtener parámetros
            content = request_data.get('content', '')
            exam_type = request_data.get('examType', 'test')
            
            # Limpiar el contenido de caracteres problemáticos
            if content:
                # Asegurar que el contenido esté en UTF-8 limpio
                content = content.encode('utf-8', errors='ignore').decode('utf-8')
                # Remover caracteres de control y no imprimibles
                content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\r\t')
            
            if not content.strip():
                self._send_error_response(400, "Content is required")
                return
            
            # Configurar Groq
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                self._send_error_response(500, "GROQ_API_KEY not configured")
                return
            
            client = Groq(api_key=groq_api_key)
            
            # Generar prompt
            if exam_type == 'test':
                num_questions = 20
                prompt = f"""
Genera exactamente {num_questions} preguntas de opción múltiple basadas en el siguiente contenido.

CONTENIDO:
{content}

INSTRUCCIONES:
- Crear exactamente {num_questions} preguntas de opción múltiple
- Cada pregunta debe tener 4 opciones (A, B, C, D)
- Solo una opción debe ser correcta
- Las preguntas deben cubrir los puntos más importantes del contenido

FORMATO DE RESPUESTA (JSON):
{{
  "questions": [
    {{
      "id": 1,
      "question": "Pregunta aquí",
      "options": ["A) Opción 1", "B) Opción 2", "C) Opción 3", "D) Opción 4"],
      "correctAnswer": 0,
      "explanation": "Explicación de por qué esta es la respuesta correcta",
      "type": "multiple-choice"
    }}
  ]
}}

Responde SOLO con el JSON, sin texto adicional.
"""
            else:  # development
                num_questions = 5
                prompt = f"""
Genera exactamente {num_questions} preguntas de desarrollo basadas en el siguiente contenido.

CONTENIDO:
{content}

INSTRUCCIONES:
- Crear exactamente {num_questions} preguntas de desarrollo/ensayo
- Las preguntas deben requerir análisis, síntesis o explicación detallada

FORMATO DE RESPUESTA (JSON):
{{
  "questions": [
    {{
      "id": 1,
      "question": "Pregunta de desarrollo aquí",
      "correctAnswer": "",
      "explanation": "Puntos clave o respuesta esperada",
      "type": "development",
      "expectedAnswer": "Respuesta esperada detallada"
    }}
  ]
}}

Responde SOLO con el JSON, sin texto adicional.
"""
            
            # Llamar a Groq con manejo de errores mejorado
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=4000
                )
                
                response_text = response.choices[0].message.content.strip()
                
                # Limpiar la respuesta de caracteres problemáticos
                response_text = response_text.encode('utf-8', errors='ignore').decode('utf-8')
                
            except Exception as groq_error:
                self._send_error_response(500, f"Groq API error: {str(groq_error)}")
                return
            
            # Parsear respuesta JSON con manejo mejorado
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx == -1 or end_idx == 0:
                    raise ValueError("No JSON found in response")
                    
                json_text = response_text[start_idx:end_idx]
                
                # Limpiar el JSON de caracteres problemáticos
                json_text = json_text.replace('\x00', '').replace('\ufffd', '')
                
                response_data = json.loads(json_text)
                
            except json.JSONDecodeError as json_error:
                self._send_error_response(500, f"Invalid JSON response from AI: {str(json_error)}")
                return
            except Exception as parse_error:
                self._send_error_response(500, f"Error parsing AI response: {str(parse_error)}")
                return
            
            # Enviar respuesta exitosa
            self._send_success_response(response_data)
            
        except UnicodeDecodeError as unicode_error:
            self._send_error_response(400, f"Text encoding error: {str(unicode_error)}")
        except json.JSONDecodeError as json_error:
            self._send_error_response(400, f"Invalid JSON in request: {str(json_error)}")
        except Exception as e:
            self._send_error_response(500, f"Error generating questions: {str(e)}")
    
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
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()