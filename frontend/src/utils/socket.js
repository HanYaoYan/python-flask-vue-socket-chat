import { io } from 'socket.io-client'
import { useAuthStore } from '@/store/auth'

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:9000'

let socketInstance = null

export function initSocket(token, callbacks = {}) {
  if (socketInstance && socketInstance.connected) {
    return socketInstance
  }

  console.log('='.repeat(50))
  console.log('初始化 Socket.IO 连接')
  console.log('Socket URL:', SOCKET_URL)
  console.log('Token 存在:', !!token)
  console.log('Token 长度:', token ? token.length : 0)
  console.log('Token 前30字符:', token ? token.substring(0, 30) + '...' : '未提供')
  console.log('='.repeat(50))

  // 同时使用 auth 和 query 参数传递 token，确保后端能收到
  const socketOptions = {
    auth: { token },
    query: { token },  // 添加查询参数，这是最可靠的方式
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: Infinity,
    timeout: 20000,
    transports: ['websocket', 'polling'],
    // 添加额外的调试信息
    forceNew: false,
    autoConnect: true
  }

  console.log('Socket.IO 连接配置:', {
    url: SOCKET_URL,
    hasAuth: !!socketOptions.auth.token,
    hasQuery: !!socketOptions.query.token,
    transports: socketOptions.transports
  })

  socketInstance = io(SOCKET_URL, socketOptions)

  // 添加连接尝试日志
  socketInstance.on('connect_attempt', () => {
    console.log('🔄 Socket.IO 正在尝试连接...')
  })

  socketInstance.on('connecting', () => {
    console.log('🔄 Socket.IO 正在连接...')
  })

  // 连接成功
  socketInstance.on('connect', () => {
    console.log('✅ Socket.IO 连接成功')
    console.log('Socket ID:', socketInstance.id)
    if (callbacks.onConnect) {
      callbacks.onConnect()
    }
  })

  // 连接失败
  socketInstance.on('connect_error', (error) => {
    console.error('❌ Socket.IO 连接失败')
    console.error('错误对象:', error)
    console.error('错误消息:', error.message)
    console.error('错误类型:', error.type)
    console.error('错误描述:', error.description)
    console.error('错误数据:', error.data)
    console.error('完整错误信息:', JSON.stringify(error, Object.getOwnPropertyNames(error), 2))
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

  // 新消息 - 已移至 Chat.vue 中直接监听，避免重复处理
  // socketInstance.on('new_message', (data) => {
  //   if (callbacks.onMessage) {
  //     callbacks.onMessage(data)
  //   }
  // })

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

