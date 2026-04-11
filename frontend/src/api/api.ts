import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios'

// 定义API响应类型
interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

// 创建API客户端
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: '/api/v1',
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // 请求拦截器
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // 响应拦截器
  client.interceptors.response.use(
    (response: AxiosResponse<ApiResponse<any>>) => {
      // 直接返回响应数据中的data字段
      return response
    },
    (error: AxiosError<ApiResponse<any>>) => {
      // 统一错误处理
      if (error.response) {
        // 服务器返回错误
        const errorMessage = error.response.data?.message || '请求失败'
        console.error('API Error:', errorMessage)
        return Promise.reject(new Error(errorMessage))
      } else if (error.request) {
        // 请求已发出但没有收到响应
        console.error('Network Error:', '服务器无响应')
        return Promise.reject(new Error('网络错误，请检查网络连接'))
      } else {
        // 请求配置出错
        console.error('Request Error:', error.message)
        return Promise.reject(new Error('请求配置错误'))
      }
    }
  )

  return client
}

// 导出API客户端
export const apiClient = createApiClient()

// 导出类型
export type { ApiResponse }
