<template>
  <Pie :data="chartData" :options="chartOptions" />
</template>

<script setup lang="ts">
import { Pie } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  CategoryScale,
} from 'chart.js'
import { ref } from 'vue'

ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale)

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
  },
})

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
})
</script>
