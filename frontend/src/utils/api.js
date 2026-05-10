import axios from 'axios'

const api = axios.create({
  baseURL: '',
  timeout: 10000,
  withCredentials: true,
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      import('@/router').then(mod => {
        const router = mod.default
        if (router.currentRoute.value.name !== 'Login') {
          router.push('/login')
        }
      }).catch(() => {
        window.location.href = '/login'
      })
    }
    return Promise.reject(err)
  },
)

export default api
