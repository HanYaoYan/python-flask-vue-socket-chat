import axios from 'axios'
import { useAuthStore } from '@/store/auth'

// 以下是服务器的地址，使用环境变量或者本地地址
// 下面这行代码声明的 API_BASE_URL 变量，是用来定义前端与后端交互的基础 API 地址，所有和服务器的通讯都会以它为前缀。
// axios 实例（如 request 变量）是通过 axios.create 创建的一个带有统一配置的请求对象。
// 前端通过 request 发送 API 请求时，这些请求都会由 axios 负责与后端 API 通讯，并自动加上基础地址、请求头、超时时间等参数。
// 这样可以规范化每一次网络请求，避免重复书写配置，让数据的传输变得简洁、轻便且安全，所有的请求和返回都经过统一处理，提升开发效率。

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:9000/api'

const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error.response?.data || error)
  }
)

export default request

