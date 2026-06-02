import { ref } from 'vue'
import api from '@/api/api'

export async function drawUserMap() {//async 
    const response = await api.get('routes/read/')



}