module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  testMatch: [
    '**/__tests__/**/*.(test|spec).ts',
    '**/tests/**/*.(test|spec).ts'
  ],
  transform: {
    '^.+\.ts$': 'ts-jest'
  }
}
