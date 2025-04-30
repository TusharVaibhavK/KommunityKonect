import axios from 'axios';

// Define the API client
const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Needed for session cookies
});

// Auth services
export const authService = {
  login: (credentials) => apiClient.post('/auth/login', credentials),
  logout: () => apiClient.post('/auth/logout'),
  register: (userData) => apiClient.post('/auth/register', userData),
};

// Service request services
export const requestService = {
  getAllRequests: () => apiClient.get('/requests'),
  getRequest: (id) => apiClient.get(`/requests/${id}`),
  createRequest: (requestData) => apiClient.post('/requests', requestData),
  updateRequest: (id, requestData) => apiClient.put(`/requests/${id}`, requestData),
  deleteRequest: (id) => apiClient.delete(`/requests/${id}`),
};

// Schedule services
export const scheduleService = {
  getAllSchedules: () => apiClient.get('/schedule'),
  createSchedule: (scheduleData) => apiClient.post('/schedule', scheduleData),
};

// User services
export const userService = {
  getAllUsers: () => apiClient.get('/users'),
};

export default {
  auth: authService,
  requests: requestService,
  schedules: scheduleService,
  users: userService,
};