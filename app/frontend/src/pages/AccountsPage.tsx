import { DeleteConfirmation } from '@/components/DeleteConfirmation';
import { ErrorMessage } from '@/components/ErrorMessage';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { Modal } from '@/components/Modal';
import { useAccountStore } from '@/store/accountStore';
import { useInstitutionStore } from '@/store/institutionStore';
import type { Account, AccountCreate, AccountType } from '@/types/models';
import { formatAccountType, formatCurrency } from '@/utils/formatters';
import React, { useEffect, useState } from 'react';

export const AccountsPage: React.FC = () => {
    const { accounts, loading, error, fetchAccounts, createAccount, updateAccount, deleteAccount } = useAccountStore();
    const { institutions, fetchInstitutions } = useInstitutionStore();

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isDeleteOpen, setIsDeleteOpen] = useState(false);
    const [editingAccount, setEditingAccount] = useState<Account | null>(null);
    const [deletingAccount, setDeletingAccount] = useState<Account | null>(null);

    const [formData, setFormData] = useState<AccountCreate>({
        institution: 0,
        name: '',
        account_number: '',
        account_type: 'checking',
    });

    useEffect(() => {
        fetchAccounts();
        fetchInstitutions();
    }, []);

    const handleOpenModal = (account?: Account) => {
        if (account) {
            setEditingAccount(account);
            setFormData({
                institution: account.institution,
                name: account.name,
                account_number: account.account_number,
                account_type: account.account_type,
            });
        } else {
            setEditingAccount(null);
            setFormData({
                institution: institutions[0]?.id || 0,
                name: '',
                account_number: '',
                account_type: 'checking',
            });
        }
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setEditingAccount(null);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            if (editingAccount) {
                await updateAccount(editingAccount.id, formData);
            } else {
                await createAccount(formData);
            }
            handleCloseModal();
        } catch (err) {
            // Error is handled by the store
        }
    };

    const handleDelete = (account: Account) => {
        setDeletingAccount(account);
        setIsDeleteOpen(true);
    };

    const confirmDelete = async () => {
        if (deletingAccount) {
            try {
                await deleteAccount(deletingAccount.id);
                setIsDeleteOpen(false);
                setDeletingAccount(null);
            } catch (err) {
                // Error is handled by the store
            }
        }
    };

    if (loading && accounts.length === 0) {
        return <LoadingSpinner className="mt-8" />;
    }

    return (
        <div className="px-4 sm:px-6 lg:px-8">
            <div className="sm:flex sm:items-center">
                <div className="sm:flex-auto">
                    <h1 className="text-2xl font-semibold text-gray-900">Accounts</h1>
                    <p className="mt-2 text-sm text-gray-700">
                        A list of all your financial accounts with current balances.
                    </p>
                </div>
                <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
                    <button
                        type="button"
                        className="btn-primary"
                        onClick={() => handleOpenModal()}
                        disabled={institutions.length === 0}
                    >
                        Add Account
                    </button>
                </div>
            </div>

            {institutions.length === 0 && (
                <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-md p-4">
                    <p className="text-sm text-yellow-700">
                        Please add an institution first before creating accounts.
                    </p>
                </div>
            )}

            {error && <ErrorMessage message={error} onRetry={fetchAccounts} />}

            <div className="mt-8 flex flex-col">
                <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
                    <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
                        <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                            <table className="min-w-full divide-y divide-gray-300">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                                            Name
                                        </th>
                                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                                            Institution
                                        </th>
                                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                                            Type
                                        </th>
                                        <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                                            Account Number
                                        </th>
                                        <th className="px-3 py-3.5 text-right text-sm font-semibold text-gray-900">
                                            Balance
                                        </th>
                                        <th className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                                            <span className="sr-only">Actions</span>
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200 bg-white">
                                    {accounts.map((account) => (
                                        <tr key={account.id}>
                                            <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                                                {account.name}
                                            </td>
                                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                                {account.institution_name}
                                            </td>
                                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                                {formatAccountType(account.account_type)}
                                            </td>
                                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                                                {account.account_number}
                                            </td>
                                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-900 text-right font-medium">
                                                {formatCurrency(account.balance)}
                                            </td>
                                            <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                                                <button
                                                    onClick={() => handleOpenModal(account)}
                                                    className="text-primary-600 hover:text-primary-900 mr-4"
                                                >
                                                    Edit
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(account)}
                                                    className="text-red-600 hover:text-red-900"
                                                >
                                                    Delete
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {accounts.length === 0 && !loading && (
                                <div className="text-center py-12 text-gray-500">
                                    No accounts found. Add your first account to get started.
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <Modal
                isOpen={isModalOpen}
                onClose={handleCloseModal}
                title={editingAccount ? 'Edit Account' : 'Add Account'}
            >
                <form onSubmit={handleSubmit}>
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="institution" className="block text-sm font-medium text-gray-700">
                                Institution
                            </label>
                            <select
                                id="institution"
                                className="input-field mt-1"
                                value={formData.institution}
                                onChange={(e) => setFormData({ ...formData, institution: Number(e.target.value) })}
                                required
                            >
                                <option value="">Select an institution</option>
                                {institutions.map((inst) => (
                                    <option key={inst.id} value={inst.id}>
                                        {inst.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                                Account Name
                            </label>
                            <input
                                type="text"
                                id="name"
                                className="input-field mt-1"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                required
                            />
                        </div>
                        <div>
                            <label htmlFor="account_type" className="block text-sm font-medium text-gray-700">
                                Account Type
                            </label>
                            <select
                                id="account_type"
                                className="input-field mt-1"
                                value={formData.account_type}
                                onChange={(e) => setFormData({ ...formData, account_type: e.target.value as AccountType })}
                                required
                            >
                                <option value="checking">Checking</option>
                                <option value="savings">Savings</option>
                                <option value="credit">Credit</option>
                                <option value="investment">Investment</option>
                            </select>
                        </div>
                        <div>
                            <label htmlFor="account_number" className="block text-sm font-medium text-gray-700">
                                Account Number
                            </label>
                            <input
                                type="text"
                                id="account_number"
                                className="input-field mt-1"
                                value={formData.account_number}
                                onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                                required
                            />
                        </div>
                    </div>
                    <div className="mt-5 sm:mt-6 sm:flex sm:flex-row-reverse">
                        <button type="submit" className="btn-primary w-full sm:w-auto sm:ml-3">
                            {editingAccount ? 'Update' : 'Create'}
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
                    setDeletingAccount(null);
                }}
                itemName="Account"
            />
        </div>
    );
};
