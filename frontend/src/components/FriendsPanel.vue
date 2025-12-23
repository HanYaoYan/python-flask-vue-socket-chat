<template>
  <div class="friends-panel">
    <div class="panel-header">
      <h3>好友管理</h3>
      <div class="header-actions">
        <button @click="showSearch = true" class="btn-add-friend">+ 添加好友</button>
      </div>
    </div>

    <div class="panel-tabs">
      <button
        :class="['tab', { active: activeSubTab === 'friends' }]"
        @click="activeSubTab = 'friends'"
      >
        好友列表
      </button>
      <button
        :class="['tab', { active: activeSubTab === 'requests' }]"
        @click="activeSubTab = 'requests'"
      >
        好友请求
        <span v-if="friendRequests.length > 0" class="badge">{{ friendRequests.length }}</span>
      </button>
    </div>

    <!-- 好友列表 -->
    <div v-if="activeSubTab === 'friends'" class="panel-content">
      <div v-if="friends.length === 0" class="empty-state">
        暂无好友，点击上方"添加好友"按钮添加
      </div>
      <div v-else class="friends-list">
        <div
          v-for="friend in friends"
          :key="friend.id"
          class="friend-item"
        >
          <div class="friend-info" @click="handleStartChat(friend.friend)">
            <span class="status-dot online"></span>
            <span class="friend-name clickable">{{ friend.friend.username }}</span>
            <span v-if="chatStore.unreadUsers[friend.friend.id] > 0" class="badge">
              {{ chatStore.unreadUsers[friend.friend.id] }}
            </span>
          </div>
          <button @click.stop="handleDeleteFriend(friend.friend.id)" class="btn-delete">删除</button>
        </div>
      </div>
    </div>

    <!-- 好友请求列表 -->
    <div v-if="activeSubTab === 'requests'" class="panel-content">
      <div v-if="friendRequests.length === 0" class="empty-state">
        暂无好友请求
      </div>
      <div v-else class="requests-list">
        <div
          v-for="request in friendRequests"
          :key="request.id"
          class="request-item"
        >
          <div class="request-info">
            <span class="requester-name">{{ request.requester.username }}</span>
            <span class="request-time">{{ formatTime(request.created_at) }}</span>
          </div>
          <div class="request-actions">
            <button @click="handleAcceptRequest(request.requester.id)" class="btn-accept">接受</button>
            <button @click="handleRejectRequest(request.requester.id)" class="btn-reject">拒绝</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索用户对话框 -->
    <div v-if="showSearch" class="search-overlay" @click.self="showSearch = false">
      <div class="search-modal">
        <div class="search-header">
          <h3>搜索用户</h3>
          <button @click="showSearch = false" class="btn-close">×</button>
        </div>
        <div class="search-body">
          <input
            v-model="searchKeyword"
            @keyup.enter="handleSearch"
            type="text"
            placeholder="输入用户名或邮箱搜索"
            class="search-input"
          />
          <button @click="handleSearch" class="btn-search">搜索</button>
        </div>
        <div v-if="searchResults.length > 0" class="search-results">
          <div
            v-for="user in searchResults"
            :key="user.id"
            class="search-result-item"
          >
            <span class="result-name">{{ user.username }}</span>
            <span class="result-email">{{ user.email }}</span>
            <button @click="handleAddFriend(user.id)" class="btn-add">添加</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getFriends, getFriendRequests, addFriend, acceptFriendRequest, deleteFriend, searchUsers } from '@/api/users'
import { useChatStore } from '@/store/chat'

const emit = defineEmits(['start-chat'])
const chatStore = useChatStore()

const activeSubTab = ref('friends')
const friends = ref([])
const friendRequests = ref([])
const showSearch = ref(false)
const searchKeyword = ref('')
const searchResults = ref([])

async function loadFriends() {
  try {
    const response = await getFriends()
    friends.value = response.friends || []
  } catch (error) {
    console.error('加载好友列表失败:', error)
  }
}

async function loadFriendRequests() {
  try {
    const response = await getFriendRequests()
    friendRequests.value = response.requests || []
  } catch (error) {
    console.error('加载好友请求失败:', error)
  }
}

async function handleSearch() {
  if (!searchKeyword.value.trim()) {
    return
  }
  try {
    const response = await searchUsers(searchKeyword.value)
    searchResults.value = response.users || []
  } catch (error) {
    console.error('搜索用户失败:', error)
    searchResults.value = []
  }
}

async function handleAddFriend(userId) {
  try {
    await addFriend(userId)
    alert('好友请求已发送')
    showSearch.value = false
    searchKeyword.value = ''
    searchResults.value = []
    await loadFriendRequests()
  } catch (error) {
    alert(error.response?.data?.error || '添加好友失败')
  }
}

async function handleAcceptRequest(friendId) {
  try {
    await acceptFriendRequest(friendId)
    await loadFriendRequests()
    await loadFriends()
  } catch (error) {
    alert(error.response?.data?.error || '接受好友请求失败')
  }
}

async function handleRejectRequest(friendId) {
  try {
    await deleteFriend(friendId)
    await loadFriendRequests()
  } catch (error) {
    alert(error.response?.data?.error || '拒绝好友请求失败')
  }
}

function handleStartChat(friend) {
  emit('start-chat', friend)
}

async function handleDeleteFriend(friendId) {
  if (!confirm('确定要删除该好友吗？')) {
    return
  }
  try {
    await deleteFriend(friendId)
    await loadFriends()
  } catch (error) {
    alert(error.response?.data?.error || '删除好友失败')
  }
}

function formatTime(timeString) {
  if (!timeString) return ''
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadFriends()
  loadFriendRequests()

  // 监听好友请求接受事件（通过Socket.IO）
  // 注意：这里需要从Chat.vue传递socket实例，或者通过store获取
  // 暂时通过定时刷新来处理，后续可以优化为Socket事件
})

defineExpose({
  loadFriends,
  loadFriendRequests
})
</script>

<style scoped>
.friends-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-add-friend {
  padding: 6px 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.panel-tabs {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
}

.tab {
  flex: 1;
  padding: 10px;
  background: none;
  border: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  position: relative;
}

.tab.active {
  border-bottom-color: #667eea;
  color: #667eea;
  font-weight: bold;
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  background: #f44336;
  color: white;
  border-radius: 9px;
  padding: 0 6px;
  font-size: 11px;
  font-weight: bold;
  margin-left: auto;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  line-height: 1;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 40px 20px;
  font-size: 14px;
}

.friends-list, .requests-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.friend-item, .request-item {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.friend-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.friend-name, .requester-name {
  font-weight: 500;
}

.friend-name.clickable {
  cursor: pointer;
  color: #667eea;
}

.friend-name.clickable:hover {
  text-decoration: underline;
}

.friend-info {
  cursor: pointer;
}

.request-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.request-time {
  font-size: 12px;
  color: #999;
}

.request-actions {
  display: flex;
  gap: 8px;
}

.btn-delete, .btn-accept, .btn-reject {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-delete {
  background: #f44336;
  color: white;
}

.btn-accept {
  background: #4caf50;
  color: white;
}

.btn-reject {
  background: #f44336;
  color: white;
}

.search-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.search-modal {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90vw;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.search-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-header h3 {
  margin: 0;
  font-size: 18px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #666;
  line-height: 1;
}

.search-body {
  padding: 20px;
  display: flex;
  gap: 10px;
}

.search-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn-search {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-results {
  padding: 0 20px 20px;
  max-height: 300px;
  overflow-y: auto;
}

.search-result-item {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-name {
  font-weight: 500;
}

.result-email {
  font-size: 12px;
  color: #999;
  margin-left: 10px;
}

.btn-add {
  padding: 6px 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
</style>

