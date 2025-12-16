import request from './request'

export function getRooms() {
  return request.get('/rooms/')
}

export function createRoom(name, description, roomType = 'group') {
  return request.post('/rooms/', { name, description, room_type: roomType })
}

export function joinRoom(roomId) {
  return request.post(`/rooms/${roomId}/join`)
}

export function getMessages(roomId, page = 1, perPage = 50) {
  return request.get(`/rooms/${roomId}/messages`, {
    params: { page, per_page: perPage }
  })
}

