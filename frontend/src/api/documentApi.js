// documentApi.js
import apiClient from "./apiClient";

const documentApi = {
  async uploadDocument(file, onUploadProgress) {
    const formData = new FormData();
    formData.append("file", file);

    return apiClient.post("/api/documents/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    });
  },

  async getDocuments() {
    return apiClient.get("/api/documents");
  },

  async getDocument(documentId) {
    return apiClient.get(`/api/documents/${documentId}`);
  },

  async deleteDocument(documentId) {
    return apiClient.delete(`/api/documents/${documentId}`);
  },

  async processDocument(documentId) {
    return apiClient.post(`/api/documents/${documentId}/process`);
  },
};

export default documentApi;