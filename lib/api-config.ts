// API Configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export const API_ENDPOINTS = {
  generateQuestions: `${API_BASE_URL}/generate-questions`,
  gradeExam: `${API_BASE_URL}/grade-exam`,
  health: `${API_BASE_URL}/health`
}

// Helper function to check if we're using the new Python API
export const isUsingPythonAPI = () => {
  return API_BASE_URL !== window.location.origin
}
