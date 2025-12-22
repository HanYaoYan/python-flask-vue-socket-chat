<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>加入房间</h2>
        <button @click="$emit('close')" class="btn-close">×</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>房间ID（6位数字）</label>
          <input
            v-model="form.roomCode"
            type="text"
            placeholder="请输入6位房间ID"
            maxlength="6"
            pattern="[0-9]{6}"
            required
          />
          <p class="form-hint">请输入6位数字房间ID</p>
        </div>
      </div>
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn-cancel">取消</button>
        <button @click="handleJoin" :disabled="loading" class="btn-confirm">
          {{ loading ? '加入中...' : '加入' }}
        </button>
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useChatStore } from '@/store/chat'

const chatStore = useChatStore()

const form = ref({
  roomCode: ''
})
const loading = ref(false)
const error = ref('')

const emit = defineEmits(['close', 'joined'])

async function handleJoin() {
  const roomCode = form.value.roomCode.trim()

  if (!roomCode) {
    error.value = '房间ID不能为空'
    return
  }

  // 验证是否为6位数字
  if (!/^\d{6}$/.test(roomCode)) {
    error.value = '房间ID必须是6位数字'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const room = await chatStore.joinRoomByCode(roomCode)
    emit('joined', room)
  } catch (err) {
    error.value = err.response?.data?.error || '加入房间失败'
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

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
  font-family: inherit;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

.form-hint {
  margin-top: 5px;
  font-size: 12px;
  color: #999;
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
</style>

