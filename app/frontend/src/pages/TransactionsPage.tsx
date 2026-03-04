import { DeleteConfirmation } from '@/components/DeleteConfirmation';
import { ErrorMessage } from '@/components/ErrorMessage';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { Modal } from '@/components/Modal';
import { useAccountStore } from '@/store/accountStore';
import { useCategoryStore } from '@/store/categoryStore';
import { useTransactionStore } from '@/store/transactionStore';
import type { Transaction, TransactionCreate, TransactionStatus } from '@/types/models';
import { formatCurrency, formatDate, formatDateForInput, formatStatus, getAmountColorClass, getTodayDate } from '@/utils/formatters';
import React, { useEffect, useState } from 'react';

export const TransactionsPage: React.FC = () => {
    const {
        transactions,
        pagination,
        loading,
        error,
        filters,
        fetchTransactions,
        createTransaction,
        updateTransaction,
        deleteTransaction,
        setFilters
    } = useTransactionStore();

    const { accounts, fetchAccounts } = useAccountStore();
    const { categories, fetchCategories } = useCategoryStore();

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isDeleteOpen, setIsDeleteOpen] = useState(false);
    const [editingTransaction, setEditingTransaction] = useState<Transaction | null>(null);
    const [deletingTransaction, setDeletingTransaction] = useState<Transaction | null>(null);

    const [formData, setFormData] = useState<TransactionCreate>({
        account: 0,
        date: getTodayDate(),
        description: '',
        original_description: '',
        amount: '',
        category: null,
        status: 'posted',
    });

    const [searchTerm, setSearchTerm] = useState('');
    const [filterAccount, setFilterAccount] = useState<number | ''>('');
    const [filterCategory, setFilterCategory] = useState<number | ''>('');

    useEffect(() => {
        fetchTransactions();
        fetchAccounts();
        fetchCategories();
    }, []);

    const handleOpenModal = (transaction?: Transaction) => {
        if (transaction) {
            setEditingTransaction(transaction);
            setFormData({
                account: transaction.account,
                date: formatDateForInput(transaction.date),
                description: transaction.description,
                original_description: transaction.original_description,
                amount: transaction.amount,
                category: transaction.category,
                status: transaction.status,
            });
        } else {
            setEditingTransaction(null);
            setFormData({
                account: accounts[0]?.id || 0,
                date: getTodayDate(),
                description: '',
                original_description: '',
                amount: '',
                category: null,
                status: 'posted',
            });
        }
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setEditingTransaction(null);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            if (editingTransaction) {
                await updateTransaction(editingTransaction.id, formData);
            } else {
                await createTransaction(formData);
            }
            handleCloseModal();
        } catch (err) {
            // Error is handled by the store
        }
    };

    const handleDelete = (transaction: Transaction) => {
        setDeletingTransaction(transaction);
        setIsDeleteOpen(true);
    };

    const confirmDelete = async () => {
        if (deletingTransaction) {
            try {
                await deleteTransaction(deletingTransaction.id);
                setIsDeleteOpen(false);
                setDeletingTransaction(null);
            } catch (err) {
                // Error is handled by the store
            }
        }
    };

    const handleFilter = () => {
        const newFilters: any = {};
        if (searchTerm) newFilters.search = searchTerm;
        if (filterAccount) newFilters.account = filterAccount;
        if (filterCategory) newFilters.category = filterCategory;

        setFilters(newFilters);
        fetchTransactions(newFilters);
    };

    const handleClearFilters = () => {
        setSearchTerm('');
        setFilterAccount('');
        setFilterCategory('');
        setFilters({});
        fetchTransactions({});
    };

    const handlePageChange = (page: number) => {
        const newFilters = { ...filters, page };
        fetchTransactions(newFilters);
    };

    if (loading && transactions.length === 0) {
        return <LoadingSpinner className="mt-8" />;
    }

    const currentPage = filters.page || 1;
    const totalPages = Math.ceil(pagination.count / (filters.page_size || 50));

    return (
        <div className="px-4 sm:px-6 lg:px-8">
            <div className="sm:flex sm:items-center">
                <div className="sm:flex-auto">
                    <h1 className="text-2xl font-semibold text-gray-900">Transactions</h1>
                    <p className="mt-2 text-sm text-gray-700">
                        A list of all your financial transactions.
                    </p>
                </div>
                <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
                    <button
                        type="button"
                        className="btn-primary"
                        onClick={() => handleOpenModal()}
                        disabled={accounts.length === 0}
                    >
                        Add Transaction
                    </button>
                </div>
            </div>

            {accounts.length === 0 && (
                <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-md p-4">
                    <p className="text-sm text-yellow-700">
                        Please add an account first before creating transactions.
                    </p>
                </div>
            )}

            {/* Filters */}
            <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-4">
                <div>
                    <label htmlFor="search" className="block text-sm font-medium text-gray-700">
                        Search
                    </label>
                    <input
                        type="text"
                        id="search"
                        className="input-field mt-1"
                        placeholder="Description or merchant..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <div>
                    <label htmlFor="filterAccount" className="block text-sm font-medium text-gray-700">
                        Account
                    </label>
                    <select
                        id="filterAccount"
                        className="input-field mt-1"
                        value={filterAccount}
                        onChange={(e) => setFilterAccount(e.target.value ? Number(e.target.value) : '')}
                    >
                        <option value="">All Accounts</option>
                        {accounts.map((acc) => (
                            <option key={acc.id} value={acc.id}>
                                {acc.name}
                            </option>
                        ))}
                    </select>
                </div>
                <div>
                    <label htmlFor="filterCategory" className="block text-sm font-medium text-gray-700">
                        Category
                    </label>
                    <select
                        id="filterCategory"
                        className="input-field mt-1"
                        value={filterCategory}
                        onChange={(e) => setFilterCategory(e.target.value ? Number(e.target.value) : '')}
                    >
                        <option value="">All Categories</option>
                        {categories.map((cat) => (
                            <option key={cat.id} value={cat.id}>
                                {cat.name}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="flex items-end space-x-2">
                    <button
                        type="button"
                        className="btn-primary flex-1"
                        onClick={handleFilter}
                    >
                        Filter
                    </button>
                    <button
                        type="button"
                        className="btn-secondary flex-1"
                        onClick={handleClearFilters}
                    >
                        Clear
                    </button>
                </div>
            </div>

            {error && <ErrorMessage message={error} onRetry={() => fetchTransactions()} />}

            {/* Results count */}
            {pagination.count > 0 && (
                <div className="mt-4 text-sm text-gray-700">
                    Showing {transactions.length} of {pagination.count} transactions
                </div>
            )}

            <div className="mt-4 flex flex-col">
                <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
                    <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
                        <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                            <table className="min-w-full divide-y divide-gray-300">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                                            Date
                                        </th>
                                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                                            Description
                                        </th>
                                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                                            Account
                                        </th>
                                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                                            Category
                                        </th>
                                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                                            Status
                                        </th>
                                        <th className="px-3 py-3.5 text-right text-sm font-semibold text-gray-900">
                                            Amount
                                        </th>
                                        <th className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                                            <span className="sr-only">Actions</span>
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200 bg-white">
                                    {transactions.map((transaction) => (
                                        <tr key={transaction.id}>
                                            <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-900 sm:pl-6">
                                                {formatDate(transaction.date)}
                                            </td>
                                            <td className="px-3 py-4 text-sm text-gray-900">
                                                <div className="font-medium">{transaction.description}</div>
                                                {transaction.merchant && (
                                                    <div className="text-gray-500 text-xs">{transaction.merchant}</div>
                                                )}
                                            </td>
                                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                                {transaction.account_name}
                                            </td>
                                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                                {transaction.category_name || '-'}
                                            </td>
                                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                                {formatStatus(transaction.status)}
                                            </td>
                                            <td className={`whitespace-nowrap px-3 py-4 text-sm text-right font-medium ${getAmountColorClass(transaction.amount)}`}>
                                                {formatCurrency(transaction.amount)}
                                            </td>
                                            <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                                                <button
                                                    onClick={() => handleOpenModal(transaction)}
                                                    className="text-primary-600 hover:text-primary-900 mr-4"
                                                >
                                                    Edit
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(transaction)}
                                                    className="text-red-600 hover:text-red-900"
                                                >
                                                    Delete
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {transactions.length === 0 && !loading && (
                                <div className="text-center py-12 text-gray-500">
                                    No transactions found. Add your first transaction to get started.
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="mt-4 flex items-center justify-between">
                    <button
                        className="btn-secondary"
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                    >
                        Previous
                    </button>
                    <span className="text-sm text-gray-700">
                        Page {currentPage} of {totalPages}
                    </span>
                    <button
                        className="btn-secondary"
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === totalPages}
                    >
                        Next
                    </button>
                </div>
            )}

            <Modal
                isOpen={isModalOpen}
                onClose={handleCloseModal}
                title={editingTransaction ? 'Edit Transaction' : 'Add Transaction'}
            >
                <form onSubmit={handleSubmit}>
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="account" className="block text-sm font-medium text-gray-700">
                                Account
                            </label>
                            <select
                                id="account"
                                className="input-field mt-1"
                                value={formData.account}
                                onChange={(e) => setFormData({ ...formData, account: Number(e.target.value) })}
                                required
                            >
                                <option value="">Select an account</option>
                                {accounts.map((acc) => (
                                    <option key={acc.id} value={acc.id}>
                                        {acc.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="date" className="block text-sm font-medium text-gray-700">
                                Date
                            </label>
                            <input
                                type="date"
                                id="date"
                                className="input-field mt-1"
                                value={formData.date}
                                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                                required
                            />
                        </div>
                        <div>
                            <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                                Description
                            </label>
                            <input
                                type="text"
                                id="description"
                                className="input-field mt-1"
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                required
                            />
                        </div>
                        <div>
                            <label htmlFor="amount" className="block text-sm font-medium text-gray-700">
                                Amount (negative for expenses, positive for income)
                            </label>
                            <input
                                type="number"
                                step="0.01"
                                id="amount"
                                className="input-field mt-1"
                                value={formData.amount}
                                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                                required
                            />
                        </div>
                        <div>
                            <label htmlFor="category" className="block text-sm font-medium text-gray-700">
                                Category
                            </label>
                            <select
                                id="category"
                                className="input-field mt-1"
                                value={formData.category || ''}
                                onChange={(e) => setFormData({ ...formData, category: e.target.value ? Number(e.target.value) : null })}
                            >
                                <option value="">Uncategorized</option>
                                {categories.map((cat) => (
                                    <option key={cat.id} value={cat.id}>
                                        {cat.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="status" className="block text-sm font-medium text-gray-700">
                                Status
                            </label>
                            <select
                                id="status"
                                className="input-field mt-1"
                                value={formData.status}
                                onChange={(e) => setFormData({ ...formData, status: e.target.value as TransactionStatus })}
                                required
                            >
                                <option value="pending">Pending</option>
                                <option value="posted">Posted</option>
                                <option value="cleared">Cleared</option>
                            </select>
                        </div>
                    </div>
                    <div className="mt-5 sm:mt-6 sm:flex sm:flex-row-reverse">
                        <button type="submit" className="btn-primary w-full sm:w-auto sm:ml-3">
                            {editingTransaction ? 'Update' : 'Create'}
                        </button>
                        <button
                            type="button"
                            className="btn-secondary mt-3 w-full sm:mt-0 sm:w-auto"
                            onClick={handleCloseModal}
                        >
                            Cancel
                        </button>
                    </div>
                </form>
            </Modal>

            <DeleteConfirmation
                isOpen={isDeleteOpen}
                onConfirm={confirmDelete}
                onCancel={() => {
                    setIsDeleteOpen(false);
                    setDeletingTransaction(null);
                }}
                itemName="Transaction"
            />
        </div>
    );
};
