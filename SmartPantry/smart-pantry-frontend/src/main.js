// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import './assets/theme.css' // 暖调物理张量

const app = createApp(App)

app.use(ElementPlus)
app.mount('#app')