import request from './request'

export function getRooms() {
  return request.get('/rooms/')
}

export function createRoom(name, description, roomCode, roomType = 'group') {
  return request.post('/rooms/', { name, description, room_code: roomCode, room_type: roomType })
}

export function joinRoomByCode(roomCode) {
  return request.post('/rooms/join', { room_code: roomCode })
}

export function joinRoom(roomId, password = null) {
  // 不再需要密码参数，保留兼容性
  return request.post('/rooms/join', { room_id: roomId })
}

export function getMessages(roomId, page = 1, perPage = 50) {
  return request.get(`/rooms/${roomId}/messages`, {
    params: { page, per_page: perPage }
  })
}

