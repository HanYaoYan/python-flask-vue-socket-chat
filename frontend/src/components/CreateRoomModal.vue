<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>创建房间</h2>
        <button @click="$emit('close')" class="btn-close">×</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>房间ID</label>
          <div class="room-code-display">
            <span class="room-code-value">{{ form.roomCode }}</span>
            <button @click="generateRoomCode" class="btn-refresh" type="button" title="重新生成">
              🔄
            </button>
          </div>
          <p class="form-hint">房间ID将用于其他用户加入此房间</p>
        </div>
        <div class="form-group">
          <label>房间名称</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="请输入房间名称"
            required
          />
        </div>
        <div class="form-group">
          <label>房间描述（可选）</label>
          <textarea
            v-model="form.description"
            placeholder="请输入房间描述"
            rows="3"
          ></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn-cancel">取消</button>
        <button @click="handleCreate" :disabled="loading" class="btn-confirm">
          {{ loading ? '创建中...' : '创建' }}
        </button>
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useChatStore } from '@/store/chat'

const chatStore = useChatStore()

const form = ref({
  roomCode: '',
  name: '',
  description: ''
})
const loading = ref(false)
const error = ref('')

const emit = defineEmits(['close', 'created'])

// 生成6位随机数字房间ID
function generateRoomCode() {
  form.value.roomCode = String(Math.floor(100000 + Math.random() * 900000))
}

// 组件挂载时生成房间ID
onMounted(() => {
  generateRoomCode()
})

async function handleCreate() {
  if (!form.value.name.trim()) {
    error.value = '房间名称不能为空'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const room = await chatStore.createNewRoom(form.value.name, form.value.description, form.value.roomCode)
    emit('created', room)
  } catch (err) {
    error.value = err.response?.data?.error || err.error || '创建房间失败'
    // 如果创建失败，重新生成房间ID
    generateRoomCode()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90vw;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #666;
  line-height: 1;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

input, textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
  font-family: inherit;
}

input:focus, textarea:focus {
  outline: none;
  border-color: #667eea;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-cancel, .btn-confirm {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-cancel {
  background: #f0f0f0;
  color: #333;
}

.btn-confirm {
  background: #667eea;
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  background: #5568d3;
}

.btn-confirm:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error-message {
  margin: 0 20px 20px;
  padding: 10px;
  background: #fee;
  color: #c33;
  border-radius: 4px;
  text-align: center;
}

.room-code-display {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
  border: 2px solid #667eea;
}

.room-code-value {
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
  font-family: 'Courier New', monospace;
  flex: 1;
  text-align: center;
  letter-spacing: 2px;
}

.btn-refresh {
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.2s;
}

.btn-refresh:hover {
  background: #5568d3;
}

.form-hint {
  margin-top: 5px;
  font-size: 12px;
  color: #999;
}

.success-message {
  margin: 0 20px 20px;
  padding: 15px;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 4px;
  text-align: center;
}

.success-message p {
  margin: 8px 0;
}

.room-id {
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
  display: inline-block;
  padding: 4px 12px;
  background: white;
  border-radius: 4px;
  margin: 0 5px;
}

.hint {
  font-size: 12px;
  color: #666;
  margin-top: 10px;
}
</style>

