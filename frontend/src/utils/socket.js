import { io } from 'socket.io-client'
import { useAuthStore } from '@/store/auth'

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:9000'

let socketInstance = null

export function initSocket(token, callbacks = {}) {
  if (socketInstance && socketInstance.connected) {
    return socketInstance
  }
  
  socketInstance = io(SOCKET_URL, {
    auth: { token },
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: Infinity,
    timeout: 20000,
    transports: ['websocket', 'polling']
  })
  
  // 连接成功
  socketInstance.on('connect', () => {
    console.log('Socket.IO 连接成功')
    if (callbacks.onConnect) {
      callbacks.onConnect()
    }
  })
  
  // 连接失败
  socketInstance.on('connect_error', (error) => {
    console.error('Socket.IO 连接失败:', error)
    if (callbacks.onError) {
      callbacks.onError(error)
    }
  })
  
  // 断开连接
  socketInstance.on('disconnect', (reason) => {
    console.log('Socket.IO 断开连接:', reason)
    if (callbacks.onDisconnect) {
      callbacks.onDisconnect(reason)
    }
  })
  
  // 重新连接
  socketInstance.on('reconnect', (attemptNumber) => {
    console.log('Socket.IO 重连成功，尝试次数:', attemptNumber)
    if (callbacks.onReconnect) {
      callbacks.onReconnect(attemptNumber)
    }
  })
  
  // 重连尝试
  socketInstance.on('reconnect_attempt', (attemptNumber) => {
    console.log('Socket.IO 重连尝试:', attemptNumber)
  })
  
  // 新消息
  socketInstance.on('new_message', (data) => {
    if (callbacks.onMessage) {
      callbacks.onMessage(data)
    }
  })
  
  // 用户上线
  socketInstance.on('user_online', (data) => {
    if (callbacks.onUserOnline) {
      callbacks.onUserOnline(data)
    }
  })
  
  // 用户下线
  socketInstance.on('user_offline', (data) => {
    if (callbacks.onUserOffline) {
      callbacks.onUserOffline(data)
    }
  })
  
  // 加入房间成功
  socketInstance.on('joined_room', (data) => {
    console.log('加入房间成功:', data)
    if (callbacks.onJoinedRoom) {
      callbacks.onJoinedRoom(data)
    }
  })
  
  // 错误
  socketInstance.on('error', (data) => {
    console.error('Socket.IO 错误:', data)
    if (callbacks.onError) {
      callbacks.onError(data)
    }
  })
  
  return socketInstance
}

export function disconnectSocket(socket) {
  if (socket) {
    socket.disconnect()
    socketInstance = null
  }
}

export function getSocket() {
  return socketInstance
}

export function sendMessage(socket, content, roomId = null, receiverId = null) {
  if (!socket || !socket.connected) {
    throw new Error('Socket 未连接')
  }
  
  socket.emit('send_message', {
    content,
    room_id: roomId,
    receiver_id: receiverId
  })
}

