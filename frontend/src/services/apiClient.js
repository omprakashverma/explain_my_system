import axios from 'axios';
import { API_BASE } from '../utils/constants';

export const apiClient = axios.create({
  baseURL: API_BASE
});
