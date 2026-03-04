import { accountsAPI } from '@/api';
import type { Account, AccountCreate } from '@/types/models';
import { create } from 'zustand';

interface AccountState {
  accounts: Account[];
  loading: boolean;
  error: string | null;

  fetchAccounts: () => Promise<void>;
  createAccount: (data: AccountCreate) => Promise<Account>;
  updateAccount: (id: number, data: Partial<AccountCreate>) => Promise<Account>;
  deleteAccount: (id: number) => Promise<void>;
}

export const useAccountStore = create<AccountState>((set) => ({
  accounts: [],
  loading: false,
  error: null,

  fetchAccounts: async () => {
    set({ loading: true, error: null });
    try {
      const accounts = await accountsAPI.list();
      set({ accounts, loading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch accounts',
        loading: false,
      });
    }
  },

  createAccount: async (data: AccountCreate) => {
    set({ loading: true, error: null });
    try {
      const account = await accountsAPI.create(data);
      set((state) => ({
        accounts: [...state.accounts, account],
        loading: false,
      }));
      return account;
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create account',
        loading: false,
      });
      throw error;
    }
  },

  updateAccount: async (id: number, data: Partial<AccountCreate>) => {
    set({ loading: true, error: null });
    try {
      const updated = await accountsAPI.update(id, data);
      set((state) => ({
        accounts: state.accounts.map((acc) => (acc.id === id ? updated : acc)),
        loading: false,
      }));
      return updated;
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to update account',
        loading: false,
      });
      throw error;
    }
  },

  deleteAccount: async (id: number) => {
    set({ loading: true, error: null });
    try {
      await accountsAPI.delete(id);
      set((state) => ({
        accounts: state.accounts.filter((acc) => acc.id !== id),
        loading: false,
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete account',
        loading: false,
      });
      throw error;
    }
  },
}));
