// chatApi.js
import apiClient from "./apiClient";

const chatApi = {
  async sendMessage(data) {
    return apiClient.post("/api/interaction/chat", data);
  },

  async askQuestion(data) {
    return apiClient.post("/api/interaction/question", data);
  },

  async submitAnswer(data) {
    return apiClient.post("/api/interaction/answer", data);
  },

  async getFeedback(data) {
    return apiClient.post("/api/interaction/feedback", data);
  },

  async getConversation(lessonId) {
    return apiClient.get(`/api/interaction/conversation/${lessonId}`);
  },

  async clearConversation(lessonId) {
    return apiClient.delete(`/api/interaction/conversation/${lessonId}`);
  },
};

export default chatApi;