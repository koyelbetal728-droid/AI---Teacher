// lessonApi.js
import apiClient from "./apiClient";

const lessonApi = {
  async getLessons(params = {}) {
    return apiClient.get("/api/lessons", {
      params,
    });
  },

  async getLesson(lessonId) {
    return apiClient.get(`/api/lessons/${lessonId}`);
  },

  async createLesson(data) {
    return apiClient.post("/api/lessons", data);
  },

  async updateLesson(lessonId, data) {
    return apiClient.put(`/api/lessons/${lessonId}`, data);
  },

  async deleteLesson(lessonId) {
    return apiClient.delete(`/api/lessons/${lessonId}`);
  },

  async generateLesson(data) {
    return apiClient.post("/api/lessons/generate", data);
  },

  async startLesson(lessonId) {
    return apiClient.post(`/api/lessons/${lessonId}/start`);
  },

  async completeLesson(lessonId) {
    return apiClient.post(`/api/lessons/${lessonId}/complete`);
  },
};

export default lessonApi;