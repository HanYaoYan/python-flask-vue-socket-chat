import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getRooms, createRoom, joinRoom, getMessages } from '@/api/rooms'
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
  
  async function createNewRoom(name, description) {
    try {
      const response = await createRoom(name, description)
      rooms.value.push(response.room)
      return response.room
    } catch (error) {
      console.error('创建房间失败:', error)
      throw error
    }
  }
  
  async function joinRoomById(roomId) {
    try {
      const response = await joinRoom(roomId)
      await loadRooms()
      return response.room
    } catch (error) {
      console.error('加入房间失败:', error)
      throw error
    }
  }
  
  function addMessage(message) {
    messages.value.push(message)
  }
  
  function initSocketConnection(token) {
    socket.value = initSocket(token, {
      onMessage: (message) => {
        if (currentRoom.value && message.message.room_id === currentRoom.value.id) {
          addMessage(message.message)
        }
      },
      onUserOnline: (data) => {
        loadOnlineUsers()
      },
      onUserOffline: (data) => {
        loadOnlineUsers()
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
    addMessage,
    initSocketConnection,
    disconnectSocketConnection
  }
})

