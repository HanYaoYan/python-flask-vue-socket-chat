import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getRooms, createRoom, joinRoom, joinRoomByCode as apiJoinRoomByCode, getMessages } from '@/api/rooms'
import { getOnlineUsers } from '@/api/users'
import { initSocket, disconnectSocket } from '@/utils/socket'

export const useChatStore = defineStore('chat', () => {
  const rooms = ref([])
  const currentRoom = ref(null)
  const messages = ref([])
  const onlineUsers = ref([])
  const socket = ref(null)

  async function loadRooms() {
    try {
      const response = await getRooms()
      rooms.value = response.rooms
    } catch (error) {
      console.error('加载房间失败:', error)
    }
  }

  async function loadOnlineUsers() {
    try {
      const response = await getOnlineUsers()
      onlineUsers.value = response.online_users
    } catch (error) {
      console.error('加载在线用户失败:', error)
    }
  }

  async function selectRoom(room) {
    currentRoom.value = room

    // 加入 Socket.IO 房间
    if (socket.value) {
      socket.value.emit('join_room', { room_id: room.id })
    }

    // 加载消息
    await loadMessages(room.id)
  }

  async function loadMessages(roomId, page = 1) {
    try {
      const response = await getMessages(roomId, page)
      if (page === 1) {
        messages.value = response.messages
      } else {
        messages.value = [...response.messages, ...messages.value]
      }
    } catch (error) {
      console.error('加载消息失败:', error)
    }
  }

  async function createNewRoom(name, description, roomCode) {
    try {
      const response = await createRoom(name, description, roomCode)
      rooms.value.push(response.room)
      return response.room
    } catch (error) {
      console.error('创建房间失败:', error)
      throw error
    }
  }

  async function joinRoomById(roomId, password = null) {
    try {
      const response = await joinRoom(roomId, password)
      await loadRooms()
      return response.room
    } catch (error) {
      console.error('加入房间失败:', error)
      throw error
    }
  }

  async function joinRoomByCode(roomCode) {
    try {
      const response = await apiJoinRoomByCode(roomCode)
      await loadRooms()
      return response.room
    } catch (error) {
      console.error('加入房间失败:', error)
      throw error
    }
  }

  function addMessage(message) {
    // 检查消息是否已存在（避免重复添加）
    if (!message || !message.id) {
      console.warn('消息格式错误，缺少 ID:', message)
      return
    }

    // 使用消息 ID 进行精确匹配
    const exists = messages.value.some(m => {
      if (m.id && message.id) {
        return m.id === message.id
      }
      // 备用方案：如果没有 ID，使用内容、发送者、时间戳组合
      return m.content === message.content &&
             m.sender_id === message.sender_id &&
             m.room_id === message.room_id &&
             m.created_at === message.created_at
    })

    if (!exists) {
      messages.value.push(message)
      console.log('✅ 添加消息成功，ID:', message.id, '内容:', message.content?.substring(0, 20))
    } else {
      console.log('⚠️ 消息已存在，跳过添加，ID:', message.id, '内容:', message.content?.substring(0, 20))
    }
  }

  function initSocketConnection(token) {
    socket.value = initSocket(token, {
      onConnect: () => {
        console.log('Socket 连接成功')
      },
      onMessage: (data) => {
        // 消息处理已移至 Chat.vue，这里不再处理以避免重复
        // 保留此回调以防将来需要统一处理消息
      },
      onUserOnline: (data) => {
        loadOnlineUsers()
      },
      onUserOffline: (data) => {
        loadOnlineUsers()
      },
      onError: (error) => {
        console.error('Socket 连接错误:', error)
      }
    })
  }

  function disconnectSocketConnection() {
    if (socket.value) {
      disconnectSocket(socket.value)
      socket.value = null
    }
  }

  return {
    rooms,
    currentRoom,
    messages,
    onlineUsers,
    socket,
    loadRooms,
    loadOnlineUsers,
    selectRoom,
    loadMessages,
    createNewRoom,
    joinRoomById,
    joinRoomByCode,
    addMessage,
    initSocketConnection,
    disconnectSocketConnection
  }
})

