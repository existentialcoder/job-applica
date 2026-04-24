import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '@/router'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

interface UserProfile {
  id?: number
  first_name: string
  last_name: string
  user_name: string
  email: string | null
  avatar_url: string | null
}

interface SignupPayload {
  first_name: string
  last_name: string
  user_name: string
  email?: string
  password: string
  signup_key: 'USER_NAME' | 'EMAIL'
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<UserProfile | null>(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!accessToken.value)

  const displayName = computed(() => {
    if (!user.value) return ''
    return `${user.value.first_name} ${user.value.last_name}`.trim()
  })

  function setTokens(token: string, refreshToken?: string) {
    accessToken.value = token
    localStorage.setItem('access_token', token)
    if (refreshToken) localStorage.setItem('refresh_token', refreshToken)
    window.dispatchEvent(new CustomEvent('ja:auth', { detail: { token } }))
  }

  function setUser(userData: UserProfile | null) {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  function clearAuth() {
    accessToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    window.dispatchEvent(new CustomEvent('ja:auth', { detail: { token: null } }))
  }

  async function fetchMe(): Promise<void> {
    if (!accessToken.value) return
    const response = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${accessToken.value}` },
    })
    if (response.ok) {
      const data = await response.json()
      setUser({
        id: data.id,
        first_name: data.first_name,
        last_name: data.last_name,
        user_name: data.user_name,
        email: data.email ?? null,
        avatar_url: data.avatar_url ?? null,
      })
    } else {
      clearAuth()
    }
  }

  async function login(username: string, password: string): Promise<{ ok: boolean; error?: string }> {
    const body = new URLSearchParams()
    body.append('username', username)
    body.append('password', password)

    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
      credentials: 'include',
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      return { ok: false, error: err.detail || 'Login failed' }
    }

    const data = await response.json()
    setTokens(data.access_token, data.refresh_token)
    await fetchMe()
    return { ok: true }
  }

  async function signup(payload: SignupPayload): Promise<{ ok: boolean; error?: string }> {
    const response = await fetch(`${API_BASE}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      return { ok: false, error: err.detail || 'Signup failed' }
    }

    return { ok: true }
  }

  async function logout() {
    clearAuth()
    router.replace('/login')
  }

  function getAuthHeaders(): Record<string, string> {
    if (!accessToken.value) return {}
    return { Authorization: `Bearer ${accessToken.value}` }
  }

  return {
    accessToken, user, isAuthenticated, displayName,
    login, signup, logout, fetchMe,
    setTokens, setUser, getAuthHeaders,
  }
})
