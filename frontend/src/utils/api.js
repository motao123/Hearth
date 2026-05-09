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
      window.location.href = import.meta.env.BASE_URL + 'login'
    }
    return Promise.reject(err)
  },
)

export default api
