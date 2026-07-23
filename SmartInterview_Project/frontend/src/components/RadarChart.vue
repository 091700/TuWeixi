<template>
  <div ref="chartRef" style="width: 100%; height: 250px; margin-top: 20px;"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  radarData: Object
})

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    radar: {
      indicator: [
        { name: '技术深度', max: 100 },
        { name: '逻辑严谨', max: 100 },
        { name: '自信表现', max: 100 },
        { name: '发音清晰', max: 100 },
        { name: '抗压松弛', max: 100 }
      ],
      axisName: { color: '#8B6B5D', fontWeight: 'bold' },
      splitArea: { areaStyle: { color: ['rgba(255,255,255,0.1)', 'rgba(255,255,255,0.4)'] } },
      splitLine: { lineStyle: { color: 'rgba(255, 235, 216, 0.5)' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: [0, 0, 0, 0, 0], // 初始值
        name: '能力图谱',
        itemStyle: { color: '#FF9B85' },
        areaStyle: { color: 'rgba(255, 155, 133, 0.4)' }
      }]
    }]
  }
  chartInstance.setOption(option)
}

watch(() => props.radarData, (newData) => {
  if (newData && chartInstance) {
    chartInstance.setOption({
      series: [{
        data: [{
          value: [newData.tech, newData.logic, newData.confidence, newData.clarity, newData.relax]
        }]
      }]
    })
  }
}, { deep: true })

onMounted(() => {
  initChart()
})
</script>