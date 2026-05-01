import { createContext, useContext, useState, useEffect } from 'react'
import { authService } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for existing token on mount
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    
    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
    }
    setIsLoading(false)
  }, [])

  const login = async (username, password) => {
    try {
      const response = await authService.login(username, password)
      const { access_token, user: userData } = response.data
      
      localStorage.removeItem('guestMode')
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
      
      setToken(access_token)
      setUser(userData)
      
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      }
    }
  }

  const register = async (email, username, password, fullName) => {
    try {
      const response = await authService.register(email, username, password, fullName)
      const { access_token, user: userData } = response.data
      
      localStorage.removeItem('guestMode')
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
      
      setToken(access_token)
      setUser(userData)
      
      return { success: true }
    } catch (error) {
      console.error('Register error:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      }
    }
  }

  const googleLogin = async (credential) => {
    try {
      const response = await authService.googleAuth(credential)
      const { access_token, user: userData } = response.data
      
      localStorage.removeItem('guestMode')
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
      
      setToken(access_token)
      setUser(userData)
      
      return { success: true }
    } catch (error) {
      console.error('Google login error:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Google login failed' 
      }
    }
  }

  const guestLogin = () => {
    const guestUser = {
      id: 1,
      email: 'guest@example.com',
      username: 'guest',
      full_name: 'Guest User',
      is_active: true
    }
    const guestToken = 'guest-bypass-token'

    localStorage.setItem('guestMode', 'true')
    localStorage.setItem('token', guestToken)
    localStorage.setItem('user', JSON.stringify(guestUser))

    setToken(guestToken)
    setUser(guestUser)

    return { success: true }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('guestMode')
    setToken(null)
    setUser(null)
  }

  const updateUser = (userData) => {
    const updated = { ...user, ...userData }
    localStorage.setItem('user', JSON.stringify(updated))
    setUser(updated)
  }

  const value = {
    user,
    token,
    isLoading,
    isAuthenticated: !!token,
    login,
    register,
    googleLogin,
    guestLogin,
    logout,
    updateUser
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
