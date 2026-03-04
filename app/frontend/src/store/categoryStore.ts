import { categoriesAPI } from '@/api';
import type { Category, CategoryCreate } from '@/types/models';
import { create } from 'zustand';

interface CategoryState {
  categories: Category[];
  loading: boolean;
  error: string | null;

  fetchCategories: () => Promise<void>;
  createCategory: (data: CategoryCreate) => Promise<Category>;
  updateCategory: (id: number, data: Partial<CategoryCreate>) => Promise<Category>;
  deleteCategory: (id: number) => Promise<void>;
}

export const useCategoryStore = create<CategoryState>((set) => ({
  categories: [],
  loading: false,
  error: null,

  fetchCategories: async () => {
    set({ loading: true, error: null });
    try {
      const categories = await categoriesAPI.list();
      set({ categories, loading: false });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch categories',
        loading: false,
      });
    }
  },

  createCategory: async (data: CategoryCreate) => {
    set({ loading: true, error: null });
    try {
      const category = await categoriesAPI.create(data);
      set((state) => ({
        categories: [...state.categories, category],
        loading: false,
      }));
      return category;
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create category',
        loading: false,
      });
      throw error;
    }
  },

  updateCategory: async (id: number, data: Partial<CategoryCreate>) => {
    set({ loading: true, error: null });
    try {
      const updated = await categoriesAPI.update(id, data);
      set((state) => ({
        categories: state.categories.map((cat) => (cat.id === id ? updated : cat)),
        loading: false,
      }));
      return updated;
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to update category',
        loading: false,
      });
      throw error;
    }
  },

  deleteCategory: async (id: number) => {
    set({ loading: true, error: null });
    try {
      await categoriesAPI.delete(id);
      set((state) => ({
        categories: state.categories.filter((cat) => cat.id !== id),
        loading: false,
      }));
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete category',
        loading: false,
      });
      throw error;
    }
  },
}));
