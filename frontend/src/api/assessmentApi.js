// assessmentApi.js
import apiClient from "./apiClient";

const assessmentApi = {
  async getAssessments(params = {}) {
    return apiClient.get("/api/assessment", {
      params,
    });
  },

  async getAssessment(assessmentId) {
    return apiClient.get(`/api/assessment/${assessmentId}`);
  },

  async generateAssessment(data) {
    return apiClient.post("/api/assessment/generate", data);
  },

  async submitAssessment(data) {
    return apiClient.post("/api/assessment/submit", data);
  },

  async getResult(assessmentId) {
    return apiClient.get(`/api/assessment/${assessmentId}/result`);
  },

  async getAssessmentHistory(studentId) {
    return apiClient.get(`/api/assessment/history/${studentId}`);
  },
};

export default assessmentApi;