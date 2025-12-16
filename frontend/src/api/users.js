import request from './request'

export function getOnlineUsers() {
  return request.get('/users/online')
}

export function searchUsers(keyword) {
  return request.get('/users/search', {
    params: { keyword }
  })
}

