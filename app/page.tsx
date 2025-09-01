"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Textarea } from "@/components/ui/textarea"
import { Upload, FileText, CheckCircle, XCircle, Loader2, Brain, Zap, Award, BookOpen, Target } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"

interface Question {
  id: number
  question: string
  options?: string[]  // Opcional para preguntas de desarrollo
  correctAnswer?: number  // Opcional para preguntas de desarrollo
  explanation: string
  type: 'multiple-choice' | 'development'
  expectedAnswer?: string  // Para preguntas de desarrollo
}

interface UserAnswer {
  questionId: number
  selectedOption?: number  // Para multiple choice
  textAnswer?: string      // Para desarrollo
}

interface ExamResult {
  questionId: number
  isCorrect: boolean
  userAnswer: string
  correctAnswer: string
  explanation: string
  score?: number  // Para preguntas de desarrollo (0-100)
}

export default function PDFExamGenerator() {
  const [step, setStep] = useState<"upload" | "generating" | "exam" | "results">("upload")
  const [file, setFile] = useState<File | null>(null)
  const [examType, setExamType] = useState<"test" | "development">("test")
  const [questions, setQuestions] = useState<Question[]>([])
  const [userAnswers, setUserAnswers] = useState<UserAnswer[]>([])
  const [results, setResults] = useState<ExamResult[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile)
    }
  }

  const generateQuestions = async () => {
    if (!file) return

    setIsLoading(true)
    setStep("generating")

    try {
      const formData = new FormData()
      formData.append("pdf", file)
      formData.append("examType", examType)
      formData.append("randomSeed", Date.now().toString()) // Para variabilidad

      const response = await fetch("/api/generate-questions", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        // Intentar obtener más información del error
        let errorMessage = "Error generating questions"
        try {
          const errorData = await response.json()
          errorMessage = errorData.error || errorMessage
          if (errorData.instructions) {
            errorMessage += "\n\n" + errorData.instructions
          }
        } catch {
          // Si no se puede parsear el JSON, usar mensaje genérico
        }
        throw new Error(errorMessage)
      }

      const data = await response.json()
      setQuestions(data.questions)
      setStep("exam")
    } catch (error) {
      console.error("Error:", error)
      const errorMessage = error instanceof Error ? error.message : "Error al generar las preguntas. Inténtalo de nuevo."
      alert(errorMessage)
      setStep("upload")
    } finally {
      setIsLoading(false)
    }
  }

  const handleAnswerChange = (questionId: number, selectedOption?: number, textAnswer?: string) => {
    setUserAnswers((prev) => {
      const existing = prev.find((a) => a.questionId === questionId)
      if (existing) {
        return prev.map((a) => 
          a.questionId === questionId 
            ? { ...a, selectedOption, textAnswer } 
            : a
        )
      }
      return [...prev, { questionId, selectedOption, textAnswer }]
    })
  }

  const submitExam = async () => {
    setIsLoading(true)

    try {
      const response = await fetch("/api/grade-exam", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          questions,
          userAnswers,
        }),
      })

      if (!response.ok) throw new Error("Error grading exam")

      const data = await response.json()
      setResults(data.results)
      setStep("results")
    } catch (error) {
      console.error("Error:", error)
      alert("Error al corregir el examen. Inténtalo de nuevo.")
    } finally {
      setIsLoading(false)
    }
  }

  const resetApp = () => {
    setStep("upload")
    setFile(null)
    setExamType("test")
    setQuestions([])
    setUserAnswers([])
    setResults([])
  }

  const correctAnswers = results.filter((r) => r.isCorrect).length
  const totalQuestions = results.length
  const score = totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 0
  
  // Calcular progreso considerando ambos tipos de respuestas
  const answeredQuestions = userAnswers.filter(answer => 
    (answer.selectedOption !== undefined) || 
    (answer.textAnswer !== undefined && answer.textAnswer.trim().length > 0)
  ).length
  const progress = questions.length > 0 ? (answeredQuestions / questions.length) * 100 : 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header with animated background */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-pink-600/20 animate-pulse"></div>
        <div className="relative px-4 py-12">
          <div className="max-w-4xl mx-auto text-center">
            <div className="flex items-center justify-center mb-6">
              <div className="p-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full shadow-lg">
                <Brain className="h-12 w-12 text-white" />
              </div>
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
              ExamAI Generator
            </h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Transforma cualquier PDF en un examen inteligente con IA avanzada
            </p>

            {/* Feature badges */}
            <div className="flex flex-wrap justify-center gap-3 mt-8">
              <Badge variant="secondary" className="bg-blue-500/20 text-blue-300 border-blue-500/30 px-4 py-2">
                <Zap className="h-4 w-4 mr-2" />
                IA Avanzada
              </Badge>
              <Badge variant="secondary" className="bg-purple-500/20 text-purple-300 border-purple-500/30 px-4 py-2">
                <Target className="h-4 w-4 mr-2" />
                Corrección Automática
              </Badge>
              <Badge variant="secondary" className="bg-pink-500/20 text-pink-300 border-pink-500/30 px-4 py-2">
                <BookOpen className="h-4 w-4 mr-2" />
                Explicaciones Detalladas
              </Badge>
            </div>
          </div>
        </div>
      </div>

      <div className="pt-16">
        <div className="max-w-4xl mx-auto px-4 pb-12 -mt-8">
          {step === "upload" && (
            <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm shadow-2xl mt-8">
              <CardHeader className="text-center pb-8">
                <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4">
                  <Upload className="h-8 w-8 text-white" />
                </div>
                <CardTitle className="text-2xl text-white">Sube tu PDF</CardTitle>
                <CardDescription className="text-gray-400 text-lg">
                  Selecciona un archivo PDF y nuestra IA generará preguntas inteligentes
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-3">
                  <Label htmlFor="pdf-upload" className="text-white text-lg">
                    Archivo PDF
                  </Label>
                  <div className="relative">
                    <Input
                      id="pdf-upload"
                      type="file"
                      accept=".pdf"
                      onChange={handleFileUpload}
                      className="cursor-pointer bg-gray-700/50 border-gray-600 text-white file:bg-gradient-to-r file:from-blue-500 file:to-purple-600 file:text-white file:border-0 file:rounded-md file:px-4 file:py-2 file:mr-4 hover:bg-gray-700/70 transition-all"
                    />
                  </div>
                </div>

                {file && (
                  <div className="flex items-center gap-3 p-4 bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-lg border border-green-500/30 animate-in slide-in-from-bottom-2">
                    <div className="p-2 bg-green-500/20 rounded-full">
                      <FileText className="h-5 w-5 text-green-400" />
                    </div>
                    <div>
                      <p className="text-green-300 font-medium">{file.name}</p>
                      <p className="text-green-400/70 text-sm">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  </div>
                )}

                {file && (
                  <div className="space-y-4 animate-in slide-in-from-bottom-2">
                    <Label className="text-white text-lg">Tipo de Examen</Label>
                    <RadioGroup 
                      value={examType} 
                      onValueChange={(value: "test" | "development") => setExamType(value)}
                      className="grid grid-cols-1 md:grid-cols-2 gap-4"
                    >
                      <div className="flex items-center space-x-3 p-4 rounded-lg border border-gray-600 bg-gray-700/30 hover:bg-gray-700/50 transition-all cursor-pointer">
                        <RadioGroupItem value="test" id="test" />
                        <Label htmlFor="test" className="flex-1 cursor-pointer">
                          <div>
                            <div className="text-white font-medium">Test (20 preguntas)</div>
                            <div className="text-gray-400 text-sm">Preguntas de múltiple opción</div>
                          </div>
                        </Label>
                        <Target className="h-5 w-5 text-blue-400" />
                      </div>
                      <div className="flex items-center space-x-3 p-4 rounded-lg border border-gray-600 bg-gray-700/30 hover:bg-gray-700/50 transition-all cursor-pointer">
                        <RadioGroupItem value="development" id="development" />
                        <Label htmlFor="development" className="flex-1 cursor-pointer">
                          <div>
                            <div className="text-white font-medium">Desarrollo (5 preguntas)</div>
                            <div className="text-gray-400 text-sm">Preguntas abiertas con corrección IA</div>
                          </div>
                        </Label>
                        <BookOpen className="h-5 w-5 text-purple-400" />
                      </div>
                    </RadioGroup>
                  </div>
                )}

                <Button
                  onClick={generateQuestions}
                  disabled={!file || isLoading}
                  className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white py-6 text-lg font-semibold shadow-lg hover:shadow-xl transition-all transform hover:scale-[1.02]"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-3 h-5 w-5 animate-spin" />
                      Generando Preguntas...
                    </>
                  ) : (
                    <>
                      <Brain className="mr-3 h-5 w-5" />
                      Generar Examen con IA
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          )}

          {step === "generating" && (
            <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm shadow-2xl">
              <CardContent className="pt-12 pb-12">
                <div className="text-center space-y-6">
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full animate-ping opacity-20"></div>
                    <div className="relative p-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full">
                      <Brain className="h-12 w-12 text-white animate-pulse" />
                    </div>
                  </div>
                  <h3 className="text-2xl font-bold text-white">IA Procesando Contenido</h3>
                  <p className="text-gray-300 text-lg max-w-md mx-auto">
                    Analizando tu PDF y generando preguntas inteligentes basadas en el contenido
                  </p>
                  <div className="flex justify-center space-x-2">
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce"></div>
                    <div
                      className="w-3 h-3 bg-purple-500 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-3 h-3 bg-pink-500 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {step === "exam" && (
            <div className="space-y-8">
              {/* Progress header */}
              <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                      <Target className="h-6 w-6 text-blue-400" />
                      Examen en Progreso
                    </h2>
                    <Badge variant="outline" className="border-blue-500/50 text-blue-300 px-4 py-2">
                      {userAnswers.length}/{questions.length} respondidas
                    </Badge>
                  </div>
                  <Progress value={progress} className="h-3 bg-gray-700" />
                  <p className="text-gray-400 mt-2">Progreso: {Math.round(progress)}%</p>
                </CardContent>
              </Card>

              {questions.map((question, index) => (
                <Card
                  key={question.id}
                  className="bg-gray-800/50 border-gray-700 backdrop-blur-sm shadow-xl hover:shadow-2xl transition-all"
                >
                  <CardHeader className="pb-4">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-xl text-white mb-2">Pregunta {index + 1}</CardTitle>
                        <CardDescription className="text-lg text-gray-200 leading-relaxed">
                          {question.question}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {question.type === 'multiple-choice' && question.options ? (
                      <RadioGroup
                        value={userAnswers.find((a) => a.questionId === question.id)?.selectedOption?.toString()}
                        onValueChange={(value) => handleAnswerChange(question.id, Number.parseInt(value))}
                        className="space-y-3"
                      >
                        {question.options.map((option, optionIndex) => (
                          <div
                            key={optionIndex}
                            className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700/30 transition-colors"
                          >
                            <RadioGroupItem
                              value={optionIndex.toString()}
                              id={`q${question.id}-${optionIndex}`}
                              className="border-gray-500 text-blue-400"
                            />
                            <Label
                              htmlFor={`q${question.id}-${optionIndex}`}
                              className="cursor-pointer text-gray-200 text-base leading-relaxed flex-1"
                            >
                              {option}
                            </Label>
                          </div>
                        ))}
                      </RadioGroup>
                    ) : (
                      <div className="space-y-3">
                        <Label htmlFor={`q${question.id}-text`} className="text-gray-300">
                          Desarrolla tu respuesta:
                        </Label>
                        <Textarea
                          id={`q${question.id}-text`}
                          placeholder="Escribe tu respuesta aquí..."
                          value={userAnswers.find((a) => a.questionId === question.id)?.textAnswer || ''}
                          onChange={(e) => handleAnswerChange(question.id, undefined, e.target.value)}
                          className="min-h-[120px] bg-gray-700/50 border-gray-600 text-white placeholder-gray-400 resize-none"
                        />
                        <p className="text-sm text-gray-400">
                          Tip: Desarrolla tu respuesta de forma completa y fundamentada para obtener mejor puntuación.
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}

              <div className="text-center pt-8">
                <Button
                  onClick={submitExam}
                  disabled={userAnswers.length !== questions.length || isLoading}
                  className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white px-12 py-6 text-lg font-semibold shadow-lg hover:shadow-xl transition-all transform hover:scale-[1.02]"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-3 h-5 w-5 animate-spin" />
                      Corrigiendo Examen...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="mr-3 h-5 w-5" />
                      Enviar y Corregir Examen
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}

          {step === "results" && (
            <div className="space-y-8">
              {/* Results header */}
              <Card className="bg-gradient-to-r from-gray-800/80 to-gray-700/80 border-gray-600 backdrop-blur-sm shadow-2xl">
                <CardHeader className="text-center pb-8">
                  <div className="mx-auto w-20 h-20 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center mb-6">
                    <Award className="h-10 w-10 text-white" />
                  </div>
                  <CardTitle className="text-3xl text-white mb-4">Resultados del Examen</CardTitle>
                  <div className="flex items-center justify-center gap-6">
                    <div className="text-center">
                      <div
                        className={`text-4xl font-bold ${score >= 70 ? "text-green-400" : score >= 50 ? "text-yellow-400" : "text-red-400"}`}
                      >
                        {score}%
                      </div>
                      <p className="text-gray-400">Puntuación</p>
                    </div>
                    <div className="text-center">
                      <div className="text-4xl font-bold text-blue-400">
                        {correctAnswers}/{totalQuestions}
                      </div>
                      <p className="text-gray-400">Correctas</p>
                    </div>
                  </div>
                  <Badge
                    variant={score >= 70 ? "default" : "destructive"}
                    className={`text-lg px-6 py-3 mt-4 ${
                      score >= 70
                        ? "bg-green-500/20 text-green-300 border-green-500/50"
                        : score >= 50
                          ? "bg-yellow-500/20 text-yellow-300 border-yellow-500/50"
                          : "bg-red-500/20 text-red-300 border-red-500/50"
                    }`}
                  >
                    {score >= 70 ? "¡Excelente!" : score >= 50 ? "Bien" : "Necesitas mejorar"}
                  </Badge>
                </CardHeader>
              </Card>

              {results.map((result, index) => (
                <Card key={result.questionId} className="bg-gray-800/50 border-gray-700 backdrop-blur-sm shadow-xl">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-xl">
                      <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                        {index + 1}
                      </div>
                      {result.isCorrect ? (
                        <CheckCircle className="h-6 w-6 text-green-400" />
                      ) : (
                        <XCircle className="h-6 w-6 text-red-400" />
                      )}
                      <span className="text-white">Pregunta {index + 1}</span>
                      <Badge
                        variant={result.isCorrect ? "default" : "destructive"}
                        className={
                          result.isCorrect
                            ? "bg-green-500/20 text-green-300 border-green-500/50"
                            : "bg-red-500/20 text-red-300 border-red-500/50"
                        }
                      >
                        {result.isCorrect ? "Correcta" : "Incorrecta"}
                      </Badge>
                    </CardTitle>
                    <CardDescription className="text-base text-gray-200 leading-relaxed ml-11">
                      {questions.find((q) => q.id === result.questionId)?.question}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4 ml-11">
                    <div className="p-4 rounded-lg bg-gray-700/30 border-l-4 border-blue-500">
                      <p className="text-sm font-medium text-blue-300 mb-1">Tu respuesta:</p>
                      <p className={`text-base ${result.isCorrect ? "text-green-300" : "text-red-300"}`}>
                        {result.userAnswer}
                      </p>
                    </div>
                    {!result.isCorrect && (
                      <div className="p-4 rounded-lg bg-gray-700/30 border-l-4 border-green-500">
                        <p className="text-sm font-medium text-green-300 mb-1">Respuesta correcta:</p>
                        <p className="text-green-300 text-base">{result.correctAnswer}</p>
                      </div>
                    )}
                    <div className="p-4 rounded-lg bg-gray-700/30 border-l-4 border-purple-500">
                      <p className="text-sm font-medium text-purple-300 mb-1">Explicación:</p>
                      <p className="text-gray-300 text-base leading-relaxed">{result.explanation}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}

              <div className="text-center pt-8">
                <Button
                  onClick={resetApp}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-12 py-6 text-lg font-semibold shadow-lg hover:shadow-xl transition-all transform hover:scale-[1.02]"
                >
                  <Brain className="mr-3 h-5 w-5" />
                  Generar Nuevo Examen
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="mt-16">
          <div className="relative overflow-hidden bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-pink-600/20 animate-pulse"></div>
            <div className="relative px-4 py-8">
              <div className="max-w-4xl mx-auto text-center">
                <div className="flex flex-col items-center space-y-4">
                  {/* Créditos */}
                  <p className="text-gray-300">
                    Realizado por <span className="font-bold text-white">FranJVJ</span>
                  </p>
                  
                  {/* Enlaces sociales */}
                  <div className="flex items-center space-x-6">
                    <a 
                      href="https://x.com/franjvj48" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="group flex items-center space-x-2 text-gray-300 hover:text-blue-400 transition-all duration-300"
                    >
                      <div className="p-2 bg-gray-800 group-hover:bg-blue-600 rounded-full transition-colors">
                        <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                        </svg>
                      </div>
                      <span className="text-sm">@franjvj48</span>
                    </a>
                    
                    <a 
                      href="https://instagram.com/franjvj48" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="group flex items-center space-x-2 text-gray-300 hover:text-pink-400 transition-all duration-300"
                    >
                      <div className="p-2 bg-gray-800 group-hover:bg-gradient-to-r group-hover:from-purple-500 group-hover:to-pink-500 rounded-full transition-all">
                        <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.40s-.644-1.44-1.439-1.44z"/>
                        </svg>
                      </div>
                      <span className="text-sm">franjvj48</span>
                    </a>
                  </div>
                  
                  {/* Copyright simplificado */}
                  <p className="text-gray-500 text-xs">
                    © 2025 - Creado con Next.js y Groq AI
                  </p>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}
