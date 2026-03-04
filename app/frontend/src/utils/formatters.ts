// Format currency values
export const formatCurrency = (amount: string | number): string => {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(num);
};

// Format date strings
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date);
};

// Format date for input field (YYYY-MM-DD)
export const formatDateForInput = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toISOString().split('T')[0];
};

// Get today's date in YYYY-MM-DD format
export const getTodayDate = (): string => {
  return new Date().toISOString().split('T')[0];
};

// Parse and validate amount
export const parseAmount = (value: string): number => {
  const cleaned = value.replace(/[^0-9.-]/g, '');
  return parseFloat(cleaned) || 0;
};

// Format account type for display
export const formatAccountType = (type: string): string => {
  return type.charAt(0).toUpperCase() + type.slice(1);
};

// Format transaction status for display
export const formatStatus = (status: string): string => {
  return status.charAt(0).toUpperCase() + status.slice(1);
};

// Get color class for transaction amount
export const getAmountColorClass = (amount: string | number): string => {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (num < 0) return 'text-red-600';
  if (num > 0) return 'text-green-600';
  return 'text-gray-600';
};
