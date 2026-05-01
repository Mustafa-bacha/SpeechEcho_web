import axios from 'axios'

const normalizeApiBase = (raw) => {
  const value = (raw || '').trim()
  if (!value) return '/api'
  return value.endsWith('/') ? value.slice(0, -1) : value
}

const envBase = normalizeApiBase(import.meta.env.VITE_API_BASE_URL)
const runtimeOrigin = typeof window !== 'undefined' ? window.location.origin : ''
const sameOriginBase = runtimeOrigin ? `${runtimeOrigin}/api` : '/api'
const isPinggyHost = runtimeOrigin.includes('pinggy-free.link')
const API_BASE = isPinggyHost ? sameOriginBase : (envBase || sameOriginBase)

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const isGuest = localStorage.getItem('guestMode') === 'true'
      const token = localStorage.getItem('token')
      if (isGuest || token === 'guest-bypass-token') {
        return Promise.reject(error)
      }
      // Token expired or invalid
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth services
export const authService = {
  login: (username, password) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },
  register: (email, username, password, fullName) => 
    api.post('/auth/register', { email, username, password, full_name: fullName }),
  googleAuth: (credential) => 
    api.post('/auth/google', { credential }),
  getGoogleClientId: () => 
    api.get('/auth/google/client-id'),
  getMe: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
  getStats: () => api.get('/auth/stats'),
  updateProfile: (data) => api.put('/auth/profile', data),
  changePassword: (data) => api.put('/auth/password', data),
  deleteAccount: () => api.delete('/auth/account'),
  uploadAvatar: (formData) => api.post('/auth/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
}

// Voice services
export const voiceService = {
  getVoices: () => api.get('/voices/'),
  getPredefinedVoices: () => api.get('/voices/predefined'),
  getVoice: (id) => api.get(`/voices/${id}`),
  cloneVoice: (name, description, audioFile) => {
    const formData = new FormData()
    formData.append('name', name)
    if (description) formData.append('description', description)
    formData.append('audio_file', audioFile)
    return api.post('/voices/clone', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  updateVoice: (id, data) => api.patch(`/voices/${id}`, data),
  deleteVoice: (id) => api.delete(`/voices/${id}`),
}

// TTS services with Chatterbox support
export const ttsService = {
  // Get TTS engine status
  getStatus: () => api.get('/tts/status'),
  
  // Generate speech with Chatterbox parameters
  generateSpeech: (text, voiceId, options = {}) => {
    const payload = { 
      text, 
      exaggeration: options.exaggeration ?? 0.5,
      cfg_weight: options.cfgWeight ?? 0.5,
      temperature: options.temperature ?? 0.8
    }
    // Only include voice_id if it's a valid value
    if (voiceId !== null && voiceId !== undefined) {
      payload.voice_id = voiceId
    }
    return api.post('/tts/generate', payload)
  },
  
  // Generate speech with streaming
  generateSpeechStream: async (text, voiceId, options = {}) => {
    const payload = {
      text,
      exaggeration: options.exaggeration ?? 0.5,
      cfg_weight: options.cfgWeight ?? 0.5,
      temperature: options.temperature ?? 0.8
    }
    if (voiceId !== null && voiceId !== undefined) {
      payload.voice_id = voiceId
    }
    const response = await api.post('/tts/generate/stream', payload, {
      responseType: 'blob'
    })
    return response.data
  },
  
  // Generate speech with real-time streaming chunks (SSE)
  // Starts playback immediately as each chunk is generated
  // Returns an abort function to cancel the stream
  generateSpeechStreamChunks: async (text, voiceId, options = {}, onChunk, onComplete, onError, abortSignal = null) => {
    const token = localStorage.getItem('token')
    const payload = {
      text,
      exaggeration: options.exaggeration ?? 0.5,
      cfg_weight: options.cfgWeight ?? 0.5,
      temperature: options.temperature ?? 0.8
    }
    if (voiceId !== null && voiceId !== undefined) {
      payload.voice_id = voiceId
    }
    
    try {
  const response = await fetch(`${API_BASE}/tts/generate/stream-chunks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload),
        signal: abortSignal // Support aborting the request
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Streaming request failed')
      }
      
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      
      while (true) {
        // Check if aborted
        if (abortSignal?.aborted) {
          reader.cancel()
          console.log('[TTS] Stream aborted by user')
          return
        }
        
        const { done, value } = await reader.read()
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        
        // Process complete SSE messages
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || '' // Keep incomplete message in buffer
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.error) {
                onError?.(new Error(data.error))
                return
              }
              
              if (data.is_final) {
                onComplete?.({
                  totalChunks: data.total_chunks,
                  totalDuration: data.total_duration
                })
              } else {
                // Decode base64 audio and pass to callback
                const audioData = Uint8Array.from(atob(data.audio_base64), c => c.charCodeAt(0))
                onChunk?.({
                  index: data.chunk_index,
                  audioData: audioData,
                  duration: data.duration,
                  text: data.text,
                  totalDuration: data.total_duration
                })
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e)
            }
          }
        }
      }
    } catch (error) {
      // Don't report abort errors as real errors
      if (error.name === 'AbortError') {
        console.log('[TTS] Stream fetch aborted')
        return
      }
      onError?.(error)
    }
  },
  
  // Voice conversion
  convertVoice: (sourceAudioUrl, targetVoiceId) =>
    api.post('/tts/voice-conversion', {
      source_audio_url: sourceAudioUrl,
      target_voice_id: targetVoiceId
    }),
  
  // Preview a voice
  previewVoice: (voiceId) => 
    api.post(`/tts/preview?voice_id=${voiceId}`),
}

// Document services (supports PDF, DOCX, PPTX, TXT up to 100MB)
export const documentService = {
  // Upload document with optional NLP preprocessing
  uploadDocument: (file, applyNlp = true, removeStopwords = true, optimizeTts = true) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('apply_nlp', applyNlp)
    formData.append('remove_stopwords', removeStopwords)
    formData.append('optimize_for_tts', optimizeTts)
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  // Legacy method for backward compatibility
  uploadPdf: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  convertToAudio: (text, voiceId) => 
    api.post('/documents/convert', null, {
      params: { text, voice_id: voiceId }
    }),
  // Get supported file formats
  getSupportedFormats: () => api.get('/documents/supported-formats'),
}

// Voice Chat services (real-time voice-to-voice conversation)
export const voiceChatService = {
  // Send voice message and get voice response
  sendVoiceMessage: async (audioBlob, sessionId = null, voiceId = null) => {
    const formData = new FormData()
    // Backend expects 'audio' field name
    formData.append('audio', audioBlob, 'recording.webm')
    
    // Build query params for session_id and voice_id since they're Query params not Form
    let url = '/voice-chat/message'
    const params = new URLSearchParams()
    if (sessionId) params.append('session_id', sessionId)
    if (voiceId) params.append('voice_id', voiceId)
    if (params.toString()) url += '?' + params.toString()
    
    return api.post(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'json'
    })
  },
  
  // Get voice chat service status
  getStatus: () => api.get('/voice-chat/status'),
  
  // Clear a voice chat session
  clearSession: (sessionId) => api.delete(`/voice-chat/session/${sessionId}`),
}

// Chat services
export const chatService = {
  sendMessage: (message, sessionId, documentContext = null) =>
    api.post('/chat/message', { 
      message, 
      session_id: sessionId,
      document_context: documentContext 
    }),
  
  // Streaming message for real-time response
  sendMessageStream: async (message, sessionId, documentContext, onChunk, onComplete, onError) => {
    const token = localStorage.getItem('token')
    
    try {
  const response = await fetch(`${API_BASE}/chat/message/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message,
          session_id: sessionId,
          document_context: documentContext
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let streamSessionId = sessionId
      let hasDocument = false
      
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.type === 'start') {
                streamSessionId = data.session_id
                hasDocument = data.has_document
              } else if (data.type === 'chunk') {
                onChunk(data.content)
              } else if (data.type === 'end') {
                onComplete({
                  sessionId: streamSessionId,
                  timestamp: data.timestamp,
                  hasDocument
                })
              } else if (data.type === 'error') {
                onError(new Error(data.message))
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e)
            }
          }
        }
      }
    } catch (error) {
      onError(error)
    }
  },
  
  uploadDocument: (file, sessionId = null) => {
    const formData = new FormData()
    formData.append('file', file)
    if (sessionId) {
      formData.append('session_id', sessionId)
    }
    return api.post('/chat/upload-document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  removeDocument: (sessionId) => api.delete(`/chat/document/${sessionId}`),
  getHistory: (sessionId) => api.get(`/chat/history/${sessionId}`),
  getSessions: () => api.get('/chat/sessions'),
}

export default api
