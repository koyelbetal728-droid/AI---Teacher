// profileApi.js
import apiClient from "./apiClient";

const profileApi = {
  async getProfile() {
    return apiClient.get("/api/profile");
  },

  async updateProfile(data) {
    return apiClient.put("/api/profile", data);
  },

  async getProgress() {
    return apiClient.get("/api/progress");
  },

  async getStudentProgress(studentId) {
    return apiClient.get(`/api/progress/${studentId}`);
  },
};

export default profileApi;