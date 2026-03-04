import { transactionsAPI } from '@/api';
import type { Transaction, TransactionCreate, TransactionFilters } from '@/types/models';
import { create } from 'zustand';

interface TransactionState {
    transactions: Transaction[];
    pagination: {
        count: number;
        next: string | null;
        previous: string | null;
    };
    loading: boolean;
    error: string | null;
    filters: TransactionFilters;

    fetchTransactions: (filters?: TransactionFilters) => Promise<void>;
    createTransaction: (data: TransactionCreate) => Promise<Transaction>;
    updateTransaction: (id: number, data: Partial<TransactionCreate>) => Promise<Transaction>;
    deleteTransaction: (id: number) => Promise<void>;
    setFilters: (filters: TransactionFilters) => void;
}

export const useTransactionStore = create<TransactionState>((set, get) => ({
    transactions: [],
    pagination: {
        count: 0,
        next: null,
        previous: null,
    },
    loading: false,
    error: null,
    filters: {},

    fetchTransactions: async (filters?: TransactionFilters) => {
        set({ loading: true, error: null });
        const currentFilters = filters || get().filters;

        try {
            const response = await transactionsAPI.list(currentFilters);
            set({
                transactions: response.results,
                pagination: {
                    count: response.count,
                    next: response.next,
                    previous: response.previous,
                },
                loading: false,
                filters: currentFilters,
            });
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : 'Failed to fetch transactions',
                loading: false
            });
        }
    },

    createTransaction: async (data: TransactionCreate) => {
        set({ loading: true, error: null });
        try {
            const transaction = await transactionsAPI.create(data);
            // Refresh the list to maintain consistency
            await get().fetchTransactions();
            return transaction;
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : 'Failed to create transaction',
                loading: false
            });
            throw error;
        }
    },

    updateTransaction: async (id: number, data: Partial<TransactionCreate>) => {
        set({ loading: true, error: null });
        try {
            const updated = await transactionsAPI.update(id, data);
            set(state => ({
                transactions: state.transactions.map(txn =>
                    txn.id === id ? updated : txn
                ),
                loading: false,
            }));
            return updated;
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : 'Failed to update transaction',
                loading: false
            });
            throw error;
        }
    },

    deleteTransaction: async (id: number) => {
        set({ loading: true, error: null });
        try {
            await transactionsAPI.delete(id);
            set(state => ({
                transactions: state.transactions.filter(txn => txn.id !== id),
                loading: false,
            }));
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : 'Failed to delete transaction',
                loading: false
            });
            throw error;
        }
    },

    setFilters: (filters: TransactionFilters) => {
        set({ filters });
    },
}));
