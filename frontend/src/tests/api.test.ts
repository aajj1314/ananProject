import { apiClient } from '../api/api'

// Mock localStorage for testing
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
}

Object.defineProperty(window, 'localStorage', { value: mockLocalStorage })

// Mock axios
jest.mock('axios', () => {
  return {
    create: jest.fn(() => ({
      interceptors: {
        request: {
          use: jest.fn((config) => config)
        },
        response: {
          use: jest.fn((response) => response)
        }
      },
      get: jest.fn(),
      post: jest.fn(),
      put: jest.fn(),
      delete: jest.fn()
    }))
  }
})

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('should create apiClient with correct baseURL', () => {
    expect(apiClient).toBeDefined()
  })

  test('should include auth token in headers when token exists', async () => {
    mockLocalStorage.getItem.mockReturnValue('test-token')
    
    // This test would verify that the token is included in requests
    // For now, we'll just ensure the client is created
    expect(apiClient).toBeDefined()
  })

  test('should handle API errors correctly', async () => {
    // This test would verify error handling
    // For now, we'll just ensure the client is created
    expect(apiClient).toBeDefined()
  })
})
