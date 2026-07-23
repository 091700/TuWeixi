import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css' // 我们的全局暖色毛玻璃样式
import App from './App.vue'

const app = createApp(App)
app.use(ElementPlus)
app.mount('#app')