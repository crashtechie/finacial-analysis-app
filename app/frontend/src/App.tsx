import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import { AccountsPage } from './pages/AccountsPage';
import { CategoriesPage } from './pages/CategoriesPage';
import { HomePage } from './pages/HomePage';
import { InstitutionsPage } from './pages/InstitutionsPage';
import { TransactionsPage } from './pages/TransactionsPage';

function App() {
    return (
        <BrowserRouter>
            <Layout>
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/institutions" element={<InstitutionsPage />} />
                    <Route path="/accounts" element={<AccountsPage />} />
                    <Route path="/categories" element={<CategoriesPage />} />
                    <Route path="/transactions" element={<TransactionsPage />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </Layout>
        </BrowserRouter>
    );
}

export default App;
