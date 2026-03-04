// Core domain models matching backend Django models

export interface Institution {
  id: number;
  name: string;
  identifier: string;
  created_at: string;
}

export interface InstitutionCreate {
  name: string;
  identifier: string;
}

export type AccountType = 'checking' | 'savings' | 'credit' | 'investment';

export interface Account {
  id: number;
  institution: number;
  institution_name?: string;
  name: string;
  account_number: string;
  account_type: AccountType;
  balance: string;
  created_at: string;
  updated_at: string;
}

export interface AccountCreate {
  institution: number;
  name: string;
  account_number: string;
  account_type: AccountType;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  parent: number | null;
  parent_name?: string;
  transaction_count?: number;
  created_at: string;
}

export interface CategoryCreate {
  name: string;
  parent?: number | null;
}

export type TransactionStatus = 'pending' | 'posted' | 'cleared';

export interface Transaction {
  id: number;
  account: number;
  account_name?: string;
  date: string;
  description: string;
  original_description: string;
  amount: string;
  category: number | null;
  category_name?: string;
  status: TransactionStatus;
  is_expense: boolean;
  is_income: boolean;
  merchant?: string;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  account: number;
  date: string;
  description: string;
  original_description?: string;
  amount: string;
  category?: number | null;
  status: TransactionStatus;
}

export type ImportStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface ImportLog {
  id: number;
  account: number;
  account_name?: string;
  file_name: string;
  file_path: string;
  format_type: string;
  status: ImportStatus;
  records_processed: number;
  records_imported: number;
  records_skipped: number;
  started_at: string;
  completed_at: string | null;
  error_message: string | null;
}

// API Response types with pagination
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Filter and query parameters
export interface TransactionFilters {
  account?: number;
  category?: number;
  start_date?: string;
  end_date?: string;
  search?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface ApiError {
  detail?: string;
  [key: string]: string | undefined;
}
