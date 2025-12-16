import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, verify } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  
  async function loginUser(username, password) {
    try {
      const response = await login(username, password)
      token.value = response.token
      user.value = response.user
      localStorage.setItem('token', response.token)
      localStorage.setItem('user', JSON.stringify(response.user))
      return response
    } catch (error) {
      throw error
    }
  }
  
  async function registerUser(username, email, password) {
    try {
      const response = await register(username, email, password)
      token.value = response.token
      user.value = response.user
      localStorage.setItem('token', response.token)
      localStorage.setItem('user', JSON.stringify(response.user))
      return response
    } catch (error) {
      throw error
    }
  }
  
  async function verifyToken() {
    try {
      if (!token.value) return false
      const response = await verify()
      if (response.valid) {
        user.value = response.user
        localStorage.setItem('user', JSON.stringify(response.user))
        return true
      }
      return false
    } catch (error) {
      logout()
      return false
    }
  }
  
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
  
  return {
    token,
    user,
    isAuthenticated,
    loginUser,
    registerUser,
    verifyToken,
    logout
  }
})

