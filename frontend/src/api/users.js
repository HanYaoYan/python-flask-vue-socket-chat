import request from './request'

export function getOnlineUsers() {
  return request.get('/users/online')
}

export function searchUsers(keyword) {
  return request.get('/users/search', {
    params: { keyword }
  })
}

export function getFriends() {
  return request.get('/users/friends')
}

export function getFriendRequests() {
  return request.get('/users/friends/requests')
}

export function addFriend(friendId) {
  return request.post(`/users/friends/${friendId}`)
}

export function acceptFriendRequest(friendId) {
  return request.post(`/users/friends/${friendId}/accept`)
}

export function deleteFriend(friendId) {
  return request.delete(`/users/friends/${friendId}`)
}

export function getPrivateMessages(targetId, perPage = 50) {
  return request.get(`/users/private/${targetId}/messages`, {
    params: { per_page: perPage }
  })
}

