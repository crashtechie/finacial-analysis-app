import type {
    PaginatedResponse,
    Transaction,
    TransactionCreate,
    TransactionFilters,
} from '@/types/models';
import { apiClient } from './client';

export const transactionsAPI = {
    list: async (filters?: TransactionFilters): Promise<PaginatedResponse<Transaction>> => {
        return apiClient.get<PaginatedResponse<Transaction>>('/transactions/', filters);
    },

    get: async (id: number): Promise<Transaction> => {
        return apiClient.get<Transaction>(`/transactions/${id}/`);
    },

    create: async (data: TransactionCreate): Promise<Transaction> => {
        return apiClient.post<Transaction>('/transactions/', data);
    },

    update: async (id: number, data: Partial<TransactionCreate>): Promise<Transaction> => {
        return apiClient.patch<Transaction>(`/transactions/${id}/`, data);
    },

    delete: async (id: number): Promise<void> => {
        return apiClient.delete<void>(`/transactions/${id}/`);
    },
};
