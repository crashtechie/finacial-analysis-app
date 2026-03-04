import React from 'react';
import { Link } from 'react-router-dom';

export const HomePage: React.FC = () => {
    return (
        <div className="px-4 sm:px-6 lg:px-8">
            <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                    Welcome to Financial Analysis
                </h1>
                <p className="text-lg text-gray-600 mb-8">
                    Manage your financial accounts, transactions, and gain insights into your spending.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-12">
                    <Link to="/institutions" className="card hover:shadow-lg transition-shadow">
                        <div className="flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white mx-auto mb-4">
                            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                            </svg>
                        </div>
                        <h3 className="text-lg font-medium text-gray-900">Institutions</h3>
                        <p className="mt-2 text-sm text-gray-500">Manage your financial institutions</p>
                    </Link>

                    <Link to="/accounts" className="card hover:shadow-lg transition-shadow">
                        <div className="flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white mx-auto mb-4">
                            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                            </svg>
                        </div>
                        <h3 className="text-lg font-medium text-gray-900">Accounts</h3>
                        <p className="mt-2 text-sm text-gray-500">Track your bank accounts and balances</p>
                    </Link>

                    <Link to="/categories" className="card hover:shadow-lg transition-shadow">
                        <div className="flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white mx-auto mb-4">
                            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                            </svg>
                        </div>
                        <h3 className="text-lg font-medium text-gray-900">Categories</h3>
                        <p className="mt-2 text-sm text-gray-500">Organize transactions by category</p>
                    </Link>

                    <Link to="/transactions" className="card hover:shadow-lg transition-shadow">
                        <div className="flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white mx-auto mb-4">
                            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                            </svg>
                        </div>
                        <h3 className="text-lg font-medium text-gray-900">Transactions</h3>
                        <p className="mt-2 text-sm text-gray-500">View and manage all transactions</p>
                    </Link>
                </div>

                <div className="mt-12 text-sm text-gray-500">
                    <p>Start by adding an institution, then create accounts and track your transactions.</p>
                </div>
            </div>
        </div>
    );
};
