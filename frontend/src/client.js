import axios from 'axios';

let axiosInstance = axios.create({
  baseURL: 'api',
  /* other custom settings */
});

export default axiosInstance;
