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
          <span v-if="totalRoomUnread > 0" class="tab-badge">{{ totalRoomUnread > 99 ? '99+' : totalRoomUnread }}</span>
        </button>
        <button
          :class="['tab', { active: activeTab === 'users' }]"
          @click="activeTab = 'users'"
        >
          用户
        </button>
        <button
          :class="['tab', { active: activeTab === 'friends' }]"
          @click="activeTab = 'friends'"
        >
          好友
          <span v-if="totalFriendUnread > 0" class="tab-badge">{{ totalFriendUnread > 99 ? '99+' : totalFriendUnread }}</span>
        </button>
      </div>

      <!-- 房间列表 -->
      <div v-if="activeTab === 'rooms'" class="sidebar-content">
        <div class="section-header">
          <h3>房间列表</h3>
          <div class="header-actions">
            <button @click="showJoinRoom = true" class="btn-join">+ 加入</button>
            <button @click="showCreateRoom = true" class="btn-add">+ 创建</button>
          </div>
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
              <span v-if="chatStore.unreadRooms[room.id] > 0" class="badge">
                {{ chatStore.unreadRooms[room.id] }}
              </span>
            </div>
          </div>
          <div v-if="chatStore.rooms.length === 0" class="empty-state">
            暂无房间，点击上方"创建"或"加入"按钮
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
            <span v-if="chatStore.unreadUsers[user.id] > 0" class="badge">
              {{ chatStore.unreadUsers[user.id] }}
            </span>
          </div>
        </div>
      </div>

      <!-- 好友面板 -->
      <div v-if="activeTab === 'friends'" class="sidebar-content">
        <FriendsPanel ref="friendsPanelRef" @start-chat="handleFriendChat" />
      </div>
    </div>

    <!-- 主聊天区域 -->
    <div class="chat-main">
      <div v-if="!chatStore.currentRoom && !currentPrivateChat" class="chat-empty">
        <div class="empty-message">
          <h2>选择一个房间或用户开始聊天</h2>
          <p>或创建一个新房间</p>
        </div>
      </div>

      <!-- 群聊内容 -->
      <div v-else-if="chatStore.currentRoom" class="chat-content">
        <!-- 聊天头部 -->
        <div class="chat-header">
          <div class="room-info">
            <h2>{{ chatStore.currentRoom.name }}</h2>
            <div class="room-meta">
              <span class="room-id">房间ID: {{ chatStore.currentRoom.room_code }}</span>
              <span class="member-count">{{ chatStore.currentRoom.member_count }} 人在线</span>
            </div>
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

      <!-- 私聊内容 -->
      <div v-else-if="currentPrivateChat" class="chat-content">
        <!-- 聊天头部 -->
        <div class="chat-header">
          <div class="room-info">
            <h2>{{ currentPrivateChat.username }}</h2>
            <span class="member-count">私聊</span>
          </div>
        </div>

        <!-- 消息列表 -->
        <div class="messages-container" ref="privateMessagesContainer">
          <div
            v-for="message in privateMessages"
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
            v-model="privateMessageText"
            @keyup.enter="sendPrivateMessage"
            type="text"
            placeholder="输入消息..."
            class="message-input"
          />
          <button @click="sendPrivateMessage" class="btn-send">发送</button>
        </div>
      </div>
    </div>

    <!-- 创建房间对话框 -->
    <CreateRoomModal
      v-if="showCreateRoom"
      @close="showCreateRoom = false"
      @created="handleRoomCreated"
    />

    <!-- 加入房间对话框 -->
    <JoinRoomModal
      v-if="showJoinRoom"
      @close="showJoinRoom = false"
      @joined="handleRoomJoined"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useChatStore } from '@/store/chat'
import { sendMessage as sendSocketMessage } from '@/utils/socket'
import CreateRoomModal from '@/components/CreateRoomModal.vue'
import JoinRoomModal from '@/components/JoinRoomModal.vue'
import FriendsPanel from '@/components/FriendsPanel.vue'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

const activeTab = ref('rooms')
const showCreateRoom = ref(false)
const showJoinRoom = ref(false)
const messageText = ref('')
const privateMessageText = ref('')
const messagesContainer = ref(null)
const privateMessagesContainer = ref(null)
const currentPrivateChat = ref(null)
const privateMessages = ref([])
const friendsPanelRef = ref(null)
const intervalRef = ref(null)

// 计算所有房间的未读总数
const totalRoomUnread = computed(() => {
  return Object.values(chatStore.unreadRooms).reduce((sum, count) => sum + (count || 0), 0)
})

// 计算所有好友的未读总数
const totalFriendUnread = computed(() => {
  return Object.values(chatStore.unreadUsers).reduce((sum, count) => sum + (count || 0), 0)
})

// 将 onBeforeUnmount 移到 onMounted 之前，确保在 setup 的同步部分注册
onBeforeUnmount(() => {
  if (intervalRef.value) {
    clearInterval(intervalRef.value)
    intervalRef.value = null
  }
  chatStore.disconnectSocketConnection()
})

onMounted(async () => {
  // 验证 token
  const isValid = await authStore.verifyToken()
  if (!isValid) {
    router.push('/login')
    return
  }

  // 初始化 Socket.IO
  chatStore.initSocketConnection(authStore.token)

  // 监听所有消息（包括群聊和私聊）
  // 先移除旧的监听器，避免重复注册
  if (chatStore.socket) {
    chatStore.socket.off('new_message')

    chatStore.socket.on('new_message', (data) => {
      console.log('收到新消息:', data)
      const message = data.message

        // 如果是私聊消息
      if (!message.room_id && message.receiver_id) {
        console.log('收到私聊消息:', message)
          // 计算会话对端 ID（对方）
          const otherUserId = message.sender_id === authStore.user?.id
            ? message.receiver_id
            : message.sender_id

          // 写入全局私聊缓存
          chatStore.addPrivateMessage(otherUserId, message)

          // 如果正在当前会话，刷新列表并滚动；否则记未读
          if (currentPrivateChat.value &&
              (message.sender_id === currentPrivateChat.value.id ||
               message.receiver_id === currentPrivateChat.value.id)) {
            privateMessages.value = chatStore.getPrivateMessagesByUser(currentPrivateChat.value.id)
            chatStore.clearUserUnread(currentPrivateChat.value.id)
            scrollToBottomPrivate()
          } else {
            chatStore.incrementUserUnread(otherUserId)
            console.log('收到其他用户的私聊消息，当前私聊对象:', currentPrivateChat.value?.id,
                        '消息发送者:', message.sender_id, '消息接收者:', message.receiver_id)
          }
      } else if (message.room_id) {
        // 群聊消息：如果当前正在查看该房间，则添加到消息列表
        if (chatStore.currentRoom && message.room_id === chatStore.currentRoom.id) {
          // 先检查消息是否已存在（双重保护）
          const exists = chatStore.messages.some(m => m.id === message.id)
          if (!exists) {
            console.log('收到群聊消息，ID:', message.id, '内容:', message.content?.substring(0, 20))
            chatStore.addMessage(message)
            // 等待下一个 tick 确保消息已添加，然后滚动
            nextTick(() => {
              scrollToBottom()
            })
          } else {
            console.log('⚠️ 群聊消息已存在，跳过处理，ID:', message.id)
          }
        } else {
            // 未在当前房间，增加未读计数
            chatStore.incrementRoomUnread(message.room_id)
            console.log('收到其他房间的消息，当前房间:', chatStore.currentRoom?.id, '消息房间:', message.room_id)
        }
      }
    })

    // 监听错误事件
    chatStore.socket.on('error', (data) => {
      console.error('Socket 错误:', data)
      if (data.message) {
        alert('错误: ' + data.message)
      }
    })

    // 监听好友请求接受事件
    chatStore.socket.on('friend_request_accepted', (data) => {
      // 刷新好友列表和好友请求列表
      if (friendsPanelRef.value) {
        friendsPanelRef.value.loadFriends()
        friendsPanelRef.value.loadFriendRequests()
      }
    })
  }

  // 加载数据
  await chatStore.loadRooms()
  await chatStore.loadOnlineUsers()

  // 定时刷新在线用户
  intervalRef.value = setInterval(() => {
    chatStore.loadOnlineUsers()
  }, 5000)
})

function selectRoom(room) {
  chatStore.selectRoom(room)
  currentPrivateChat.value = null
  scrollToBottom()
}

async function handleRoomCreated(room) {
  showCreateRoom.value = false
  await chatStore.loadRooms()
  selectRoom(room)
}

async function handleRoomJoined(room) {
  showJoinRoom.value = false
  await chatStore.loadRooms()
  selectRoom(room)
}

function startPrivateChat(user) {
  currentPrivateChat.value = user
  chatStore.currentRoom = null
  chatStore.clearUserUnread(user.id)
  // 加载历史私聊消息
  chatStore.loadPrivateMessages(user.id).then(() => {
    privateMessages.value = chatStore.getPrivateMessagesByUser(user.id)
    scrollToBottomPrivate()
  }).catch((err) => {
    console.error('加载私聊消息失败:', err)
    privateMessages.value = chatStore.getPrivateMessagesByUser(user.id)
  })
}

function handleFriendChat(friend) {
  startPrivateChat(friend)
  // 切换到主聊天区域（如果侧边栏遮挡）
  activeTab.value = 'rooms' // 可选：保持当前标签页或切换到其他标签页
}

function sendMessage() {
  if (!messageText.value.trim() || !chatStore.currentRoom) {
    console.warn('无法发送消息：', {
      hasText: !!messageText.value.trim(),
      hasRoom: !!chatStore.currentRoom,
      socketConnected: chatStore.socket?.connected
    })
    return
  }

  if (!chatStore.socket || !chatStore.socket.connected) {
    console.error('Socket 未连接')
    alert('连接已断开，请刷新页面重试')
    return
  }

  const content = messageText.value.trim()
  messageText.value = ''

  try {
    console.log('发送消息:', {
      content,
      roomId: chatStore.currentRoom.id,
      socketConnected: chatStore.socket.connected
    })

    sendSocketMessage(
      chatStore.socket,
      content,
      chatStore.currentRoom.id,
      null
    )
    // 消息发送后，等待服务器确认，服务器会通过Socket发送回来
    // 这里不需要立即添加到列表，因为服务器会广播消息
  } catch (error) {
    console.error('发送消息失败:', error)
    // 如果发送失败，恢复输入框内容
    messageText.value = content
    alert('发送消息失败: ' + error.message)
  }
}

function sendPrivateMessage() {
  if (!privateMessageText.value.trim() || !currentPrivateChat.value) {
    console.warn('无法发送私聊消息：', {
      hasText: !!privateMessageText.value.trim(),
      hasChatTarget: !!currentPrivateChat.value,
      socketConnected: chatStore.socket?.connected
    })
    return
  }

  if (!chatStore.socket || !chatStore.socket.connected) {
    console.error('Socket 未连接')
    alert('连接已断开，请刷新页面重试')
    return
  }

  const content = privateMessageText.value.trim()
  privateMessageText.value = ''

  try {
    console.log('发送私聊消息:', {
      content,
      receiverId: currentPrivateChat.value.id,
      receiverName: currentPrivateChat.value.username,
      socketConnected: chatStore.socket.connected
    })

    sendSocketMessage(
      chatStore.socket,
      content,
      null,
      currentPrivateChat.value.id
    )
    // 消息发送后，等待服务器确认，服务器会通过Socket发送回来
  } catch (error) {
    console.error('发送私聊消息失败:', error)
    // 如果发送失败，恢复输入框内容
    privateMessageText.value = content
    alert('发送私聊消息失败: ' + error.message)
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

function scrollToBottomPrivate() {
  nextTick(() => {
    if (privateMessagesContainer.value) {
      privateMessagesContainer.value.scrollTop = privateMessagesContainer.value.scrollHeight
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

.tab {
  position: relative;
}

.tab-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  min-width: 18px;
  height: 18px;
  padding: 0 6px;
  background: #f44336;
  color: white;
  border-radius: 9px;
  font-size: 11px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
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

.header-actions {
  display: flex;
  gap: 5px;
}

.section-header h3 {
  font-size: 14px;
  color: #666;
}

.btn-add, .btn-join {
  padding: 4px 8px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-join {
  background: #4caf50;
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

.badge {
  min-width: 18px;
  padding: 2px 6px;
  background: #f44336;
  color: white;
  border-radius: 12px;
  font-size: 12px;
  text-align: center;
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
  display: flex;
  align-items: center;
  gap: 6px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 8px;
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
  min-height: 0; /* 确保可以收缩 */
  overflow: hidden; /* 防止内容溢出 */
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
  min-height: 0; /* 确保可以收缩 */
  max-height: 100%; /* 限制最大高度 */
  overflow: hidden;
  position: relative; /* 为固定定位提供上下文 */
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0; /* 防止头部被压缩 */
}

.room-info h2 {
  font-size: 20px;
  margin-bottom: 8px;
}

.room-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.room-id {
  font-size: 13px;
  color: #667eea;
  font-weight: 500;
  background: #e3e8ff;
  padding: 4px 10px;
  border-radius: 4px;
}

.member-count {
  font-size: 12px;
  color: #666;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 20px;
  min-height: 0; /* 确保 flex 子元素可以收缩 */
  max-height: 100%; /* 限制最大高度，防止挤压输入框 */
  /* 自定义滚动条样式 */
  scrollbar-width: thin; /* Firefox */
  scrollbar-color: #c0c0c0 #f0f0f0; /* Firefox */
}

/* Webkit浏览器（Chrome, Safari）滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f0f0f0;
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c0c0c0;
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #a0a0a0;
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
  flex-shrink: 0; /* 防止输入框被压缩 */
  flex-grow: 0; /* 防止输入框扩展 */
  background: white;
  z-index: 100; /* 提高层级，确保在最上层 */
  position: sticky; /* 使用 sticky 定位，固定在底部 */
  bottom: 0; /* 固定在底部 */
  width: 100%; /* 确保宽度 */
  box-sizing: border-box; /* 包含padding在宽度内 */
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

