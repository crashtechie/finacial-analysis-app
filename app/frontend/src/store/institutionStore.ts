import { institutionsAPI } from '@/api';
import type { Institution, InstitutionCreate } from '@/types/models';
import { create } from 'zustand';

interface InstitutionState {
  institutions: Institution[];
  loading: boolean;
  error: string | null;

  fetchInstitutions: () => Promise<void>;
  createInstitution: (data: InstitutionCreate) => Promise<Institution>;
  updateInstitution: (id: number, data: Partial<InstitutionCreate>) => Promise<Institution>;
  deleteInstitution: (id: number) => Promise<void>;
}

export const useInstitutionStore = create<InstitutionState>((set) => ({
  institutions: [],
  loading: false,
  error: null,

  fetchInstitutions: async () => {
    set({ loading: true, error: null });
    try {
      const institutions = await institutionsAPI.list();
      set({ institutions, loading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch institutions',
        loading: false,
      });
    }
  },

  createInstitution: async (data: InstitutionCreate) => {
    set({ loading: true, error: null });
    try {
      const institution = await institutionsAPI.create(data);
      set((state) => ({
        institutions: [...state.institutions, institution],
        loading: false,
      }));
      return institution;
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create institution',
        loading: false,
      });
      throw error;
    }
  },

  updateInstitution: async (id: number, data: Partial<InstitutionCreate>) => {
    set({ loading: true, error: null });
    try {
      const updated = await institutionsAPI.update(id, data);
      set((state) => ({
        institutions: state.institutions.map((inst) => (inst.id === id ? updated : inst)),
        loading: false,
      }));
      return updated;
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to update institution',
        loading: false,
      });
      throw error;
    }
  },

  deleteInstitution: async (id: number) => {
    set({ loading: true, error: null });
    try {
      await institutionsAPI.delete(id);
      set((state) => ({
        institutions: state.institutions.filter((inst) => inst.id !== id),
        loading: false,
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete institution',
        loading: false,
      });
      throw error;
    }
  },
}));
