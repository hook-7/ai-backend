import axios from 'axios'
axios.defaults.headers['Content-Type'] = 'application/json;charset=utf-8'
const service = axios.create({
    // axios中请求配置有baseURL选项，表示请求URL公共部分
    baseURL: import.meta.env.VITE_API_BASE_URL
  })
  
export default service