<template>
  <div class="common-layout">
    <el-container>
      <el-header>
        <el-row :gutter="20" align="middle">
          <el-col :span="4">
            <h1>Chat bot</h1>
          </el-col>
          <el-col :span="1.5">
            <el-button type="info" @click="resetChat">新建聊天</el-button>
          </el-col>
          <el-col :span="2">
            <el-input v-model="username" title="username" placeholder="请输入用户名"></el-input>
          </el-col>
          <el-col :span="6">
            <div>今日聊天次数: {{ msgCount }}/20</div>
          </el-col>
        </el-row>

      </el-header>
      <el-container>
        <el-aside class="left_aside">
          <h3>历史消息</h3>
          <div v-for="historyMsg in historyMessages" :key="historyMsg._id" @click="handleClick(historyMsg);"
            :class="{ 'historyMsg': true, 'selected': historyMsg._id === selectedHistoryMsgId }">
            {{ historyMsg._id }}
          </div>


        </el-aside>
        <el-container class="main_footer">
          <el-main style="height: 84vh;">
            <div class="chat_box" ref="chatBox">
              <template v-for="message in state.messages" :key="message.id">
                <div class="message-header"
                  :class="{ 'sent-name': message.msgType === 'sent', 'received-name': message.msgType === 'received' }">
                  {{ message.role }}
                </div>
                <el-card class="box-card"
                  :class="{ 'sent-message': message.msgType === 'sent', 'received-message': message.msgType === 'received' }">
                  <div class="message-content">{{ message.content }}</div>
                </el-card>
              </template>
            </div>
          </el-main>


          <el-footer class="input_box">
            <el-row :gutter="24">
              <el-col :span="21">
                <el-input v-model="newMessage" type="textarea" placeholder="请输入消息" @keyup.enter="sendMessage"></el-input>
              </el-col>
              <el-col :span="3">
                <el-button type="primary" @click="sendMessage" style="width: 100%;height: 100%;">发送</el-button>
              </el-col>
            </el-row>
          </el-footer>

        </el-container>

      </el-container>
    </el-container>
  </div>
</template>

<script setup>

import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from '@/utils/request'

const chatBox = ref(null);
const newMessage = ref("");
const username = ref("user")
const historyMessages = ref([]);
const msgCount = ref(0)
const selectedHistoryMsgId = ref(0);
const _id = ref(null)

const state = reactive({
  messages: [],
  nextMessageId: 1,
});


watch(() => state.messages, () => {
  nextTick(() => {
    if (chatBox.value) {
      chatBox.value.scrollTop = chatBox.value.scrollHeight;
    }
  });
}, { deep: true });


function sendMessage() {
  if (newMessage.value.trim() === "") return;

  state.messages.push({
    id: state.nextMessageId++,
    content: newMessage.value,
    role: username.value,
    msgType: "sent",
  });

  get_ai_chat_response(state.messages);
  newMessage.value = "";


}
const get_user_chat_history = () => {

  axios.get("/get_user_chat_history/" + username.value + "/10")
    .then((response) => {

      historyMessages.value = response.data;
    })
    .catch((error) => {
      console.error("There was a problem with your fetch operation:", error);
    });
}

onMounted(() => {

  get_user_chat_history()
  get_chat_status_today()
});

const get_ai_chat_response = (message) => {

  let data = {
    id: _id.value,
    user_name: username.value,
    message: message
  }
  axios.post("/get_ai_chat_response", data)
    .then((response) => {
      const responseData = response.data;
      state.messages.push({
        id: state.nextMessageId++,
        content: responseData["choices"][0]["message"]["content"],
        role: responseData["choices"][0]["message"]["role"],
        msgType: "received",
      });
      _id.value = responseData["_id"];
      console.log(responseData);
    })
    .catch((error) => {
      console.error(error);
      ElMessage({
        message: error.message || "An error occurred",
        type: 'warning',
      });
    });
  get_chat_status_today()
};
const get_chat_status_today = () => {
  axios.get("/get_chat_status_today/" + username.value)
    .then((response) => {
      msgCount.value = response.data;
    })
    .catch((error) => {
      console.error("There was a problem with your fetch operation:", error);
    });
}
const resetChat = () => {
  _id.value = null;
  state.messages = [];
};
const handleClick = (historyMsg) => {
  selectedHistoryMsgId.value = historyMsg._id;
  _id.value = historyMsg._id;
  state.messages = historyMsg.message;
}

</script>


<style>
.sent-message,
.received-message {
  display: table;
  text-align: left;
  max-width: 60%;
  min-width: 0%;
  border-radius: 6px;
  margin-bottom: 4px;
}

.sent-message {
  background-color: #dcf8c6;
  margin-left: auto;

}

.received-message {
  background-color: #ececec;
  margin-right: auto;

}

.sent-name {
  margin-bottom: 5px;
  text-align: right;
}

.received-name {
  margin-bottom: 5px;
  text-align: left;
}

.message-header {
  margin-bottom: 3px;
}

.box-card {
  margin-bottom: 20px;

}

.selected {
  background-color: #546E7A; /* 深灰蓝色，增加深度 */
  color: #FFFFFF; /* 纯白色文本，保持不变以确保对比度 */
  border-radius: 8px;
  padding: 5px;
}

.historyMsg {
  margin-bottom: 5px;
  margin-top: 5px;
  cursor: pointer;
  transition: background-color 0.3s; /* 平滑过渡效果 */
}

.historyMsg:hover {
  background-color: #CFD8DC; /* 悬停时的浅灰色背景，提升交互性 */
}

.chat_box {
  max-height: 79vh;
  overflow-y: auto;
  padding-left: var(--padding-chat_box); /* 使用变量保持一致性 */
  padding-right: var(--padding-chat_box);
}

.input_box {
  max-height: 200px;
  height: 52px;
  overflow-y: hidden;
  padding-left: var(--padding-chat_box);
  padding-right: var(--padding-chat_box);

}

.left_aside {
  padding: 20px;
  background-color: #ECEFF1; /* 浅灰色背景，柔和而现代 */
  border-radius: 8px;
  border: 2px solid #B0BEC5; /* 淡蓝灰边框，提供细微的颜色对比 */
}

.el-main {
  padding: 0;
}

/* 滚动条样式 */
.chat_box::-webkit-scrollbar {
  width: 8px;
}

.chat_box::-webkit-scrollbar-track {
  background: transparent;
}

.chat_box::-webkit-scrollbar-thumb {
  background: #B0BEC5; /* 滑块颜色调整为与边框颜色一致 */
}

.chat_box::-webkit-scrollbar-thumb:hover {
  background: #90A4AE; /* 滑块悬停颜色，稍微亮一些以提供视觉反馈 */
}
</style>