<template>
  <div class="chat-container">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <div class="user-info">
          <div class="username">{{ authStore.user?.username }}</div>
          <div class="user-status">
            <span class="status-dot online"></span>
            <span>在线</span>
          </div>
        </div>
        <button @click="handleLogout" class="btn-logout">退出</button>
      </div>
      
      <div class="sidebar-tabs">
        <button
          :class="['tab', { active: activeTab === 'rooms' }]"
          @click="activeTab = 'rooms'"
        >
          房间
        </button>
        <button
          :class="['tab', { active: activeTab === 'users' }]"
          @click="activeTab = 'users'"
        >
          用户
        </button>
      </div>
      
      <!-- 房间列表 -->
      <div v-if="activeTab === 'rooms'" class="sidebar-content">
        <div class="section-header">
          <h3>房间列表</h3>
          <button @click="showCreateRoom = true" class="btn-add">+ 创建</button>
        </div>
        <div class="room-list">
          <div
            v-for="room in chatStore.rooms"
            :key="room.id"
            :class="['room-item', { active: chatStore.currentRoom?.id === room.id }]"
            @click="selectRoom(room)"
          >
            <div class="room-name">{{ room.name }}</div>
            <div class="room-info">
              <span>{{ room.member_count }} 人</span>
            </div>
          </div>
          <div v-if="chatStore.rooms.length === 0" class="empty-state">
            暂无房间，点击上方"创建"按钮创建房间
          </div>
        </div>
      </div>
      
      <!-- 在线用户列表 -->
      <div v-if="activeTab === 'users'" class="sidebar-content">
        <div class="section-header">
          <h3>在线用户 ({{ chatStore.onlineUsers.length }})</h3>
        </div>
        <div class="user-list">
          <div
            v-for="user in chatStore.onlineUsers"
            :key="user.id"
            class="user-item"
            @click="startPrivateChat(user)"
          >
            <span class="status-dot online"></span>
            <span class="user-name">{{ user.username }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 主聊天区域 -->
    <div class="chat-main">
      <div v-if="!chatStore.currentRoom" class="chat-empty">
        <div class="empty-message">
          <h2>选择一个房间开始聊天</h2>
          <p>或创建一个新房间</p>
        </div>
      </div>
      
      <div v-else class="chat-content">
        <!-- 聊天头部 -->
        <div class="chat-header">
          <div class="room-info">
            <h2>{{ chatStore.currentRoom.name }}</h2>
            <span class="member-count">{{ chatStore.currentRoom.member_count }} 人在线</span>
          </div>
        </div>
        
        <!-- 消息列表 -->
        <div class="messages-container" ref="messagesContainer">
          <div
            v-for="message in chatStore.messages"
            :key="message.id"
            :class="['message-item', { own: message.sender_id === authStore.user?.id }]"
          >
            <div class="message-header">
              <span class="sender-name">{{ message.sender?.username }}</span>
              <span class="message-time">{{ formatTime(message.created_at) }}</span>
            </div>
            <div class="message-content">{{ message.content }}</div>
          </div>
        </div>
        
        <!-- 消息输入框 -->
        <div class="message-input-container">
          <input
            v-model="messageText"
            @keyup.enter="sendMessage"
            type="text"
            placeholder="输入消息..."
            class="message-input"
          />
          <button @click="sendMessage" class="btn-send">发送</button>
        </div>
      </div>
    </div>
    
    <!-- 创建房间对话框 -->
    <CreateRoomModal
      v-if="showCreateRoom"
      @close="showCreateRoom = false"
      @created="handleRoomCreated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useChatStore } from '@/store/chat'
import { sendMessage as sendSocketMessage } from '@/utils/socket'
import CreateRoomModal from '@/components/CreateRoomModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

const activeTab = ref('rooms')
const showCreateRoom = ref(false)
const messageText = ref('')
const messagesContainer = ref(null)

onMounted(async () => {
  // 验证 token
  const isValid = await authStore.verifyToken()
  if (!isValid) {
    router.push('/login')
    return
  }
  
  // 初始化 Socket.IO
  chatStore.initSocketConnection(authStore.token)
  
  // 加载数据
  await chatStore.loadRooms()
  await chatStore.loadOnlineUsers()
  
  // 定时刷新在线用户
  const interval = setInterval(() => {
    chatStore.loadOnlineUsers()
  }, 5000)
  
  onUnmounted(() => {
    clearInterval(interval)
    chatStore.disconnectSocketConnection()
  })
})

function selectRoom(room) {
  chatStore.selectRoom(room)
  scrollToBottom()
}

async function handleRoomCreated(room) {
  showCreateRoom.value = false
  await chatStore.loadRooms()
  selectRoom(room)
}

function startPrivateChat(user) {
  // TODO: 实现私聊功能
  console.log('开始私聊:', user)
}

function sendMessage() {
  if (!messageText.value.trim() || !chatStore.currentRoom) {
    return
  }
  
  try {
    sendSocketMessage(
      chatStore.socket,
      messageText.value.trim(),
      chatStore.currentRoom.id,
      null
    )
    messageText.value = ''
  } catch (error) {
    console.error('发送消息失败:', error)
  }
}

function formatTime(timeString) {
  if (!timeString) return ''
  const date = new Date(timeString)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

function handleLogout() {
  chatStore.disconnectSocketConnection()
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  background: #f5f5f5;
}

/* 侧边栏 */
.sidebar {
  width: 300px;
  background: white;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  flex: 1;
}

.username {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 5px;
}

.user-status {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #666;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 5px;
}

.status-dot.online {
  background: #4caf50;
}

.btn-logout {
  padding: 6px 12px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.sidebar-tabs {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
}

.tab {
  flex: 1;
  padding: 12px;
  background: none;
  border: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
}

.tab.active {
  border-bottom-color: #667eea;
  color: #667eea;
  font-weight: bold;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-header h3 {
  font-size: 14px;
  color: #666;
}

.btn-add {
  padding: 4px 8px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.room-list, .user-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.room-item, .user-item {
  padding: 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.room-item:hover, .user-item:hover {
  background: #f0f0f0;
}

.room-item.active {
  background: #e3e8ff;
}

.room-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.room-info {
  font-size: 12px;
  color: #666;
}

.user-item {
  display: flex;
  align-items: center;
}

.user-name {
  margin-left: 8px;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 20px;
  font-size: 12px;
}

/* 主聊天区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
}

.chat-empty {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.empty-message {
  text-align: center;
  color: #999;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.room-info h2 {
  font-size: 20px;
  margin-bottom: 5px;
}

.member-count {
  font-size: 12px;
  color: #666;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message-item {
  margin-bottom: 20px;
  max-width: 70%;
}

.message-item.own {
  margin-left: auto;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
  font-size: 12px;
}

.sender-name {
  font-weight: bold;
  color: #667eea;
}

.message-item.own .sender-name {
  color: #4caf50;
}

.message-time {
  color: #999;
}

.message-content {
  background: #f0f0f0;
  padding: 10px 15px;
  border-radius: 8px;
  word-wrap: break-word;
}

.message-item.own .message-content {
  background: #667eea;
  color: white;
}

.message-input-container {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 10px;
}

.message-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.message-input:focus {
  outline: none;
  border-color: #667eea;
}

.btn-send {
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-send:hover {
  background: #5568d3;
}
</style>

