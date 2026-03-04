import { DeleteConfirmation } from '@/components/DeleteConfirmation';
import { ErrorMessage } from '@/components/ErrorMessage';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { Modal } from '@/components/Modal';
import { useInstitutionStore } from '@/store/institutionStore';
import type { Institution, InstitutionCreate } from '@/types/models';
import { formatDate } from '@/utils/formatters';
import React, { useEffect, useState } from 'react';

export const InstitutionsPage: React.FC = () => {
  const {
    institutions,
    loading,
    error,
    fetchInstitutions,
    createInstitution,
    updateInstitution,
    deleteInstitution,
  } = useInstitutionStore();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [editingInstitution, setEditingInstitution] = useState<Institution | null>(null);
  const [deletingInstitution, setDeletingInstitution] = useState<Institution | null>(null);

  const [formData, setFormData] = useState<InstitutionCreate>({
    name: '',
    identifier: '',
  });

  useEffect(() => {
    fetchInstitutions();
  }, [fetchInstitutions]);

  const handleOpenModal = (institution?: Institution) => {
    if (institution) {
      setEditingInstitution(institution);
      setFormData({
        name: institution.name,
        identifier: institution.identifier,
      });
    } else {
      setEditingInstitution(null);
      setFormData({ name: '', identifier: '' });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingInstitution(null);
    setFormData({ name: '', identifier: '' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingInstitution) {
        await updateInstitution(editingInstitution.id, formData);
      } else {
        await createInstitution(formData);
      }
      handleCloseModal();
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (_) {
      // Error is handled by the store
    }
  };

  const handleDelete = (institution: Institution) => {
    setDeletingInstitution(institution);
    setIsDeleteOpen(true);
  };

  const confirmDelete = async () => {
    if (deletingInstitution) {
      try {
        await deleteInstitution(deletingInstitution.id);
        setIsDeleteOpen(false);
        setDeletingInstitution(null);
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
      } catch (_) {
        // Error is handled by the store
      }
    }
  };

  if (loading && institutions.length === 0) {
    return <LoadingSpinner className="mt-8" />;
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Institutions</h1>
          <p className="mt-2 text-sm text-gray-700">
            A list of all financial institutions in your account.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button type="button" className="btn-primary" onClick={() => handleOpenModal()}>
            Add Institution
          </button>
        </div>
      </div>

      {error && <ErrorMessage message={error} onRetry={fetchInstitutions} />}

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
                      Identifier
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                      Created At
                    </th>
                    <th className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {institutions.map((institution) => (
                    <tr key={institution.id}>
                      <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                        {institution.name}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        {institution.identifier}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                        {formatDate(institution.created_at)}
                      </td>
                      <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                        <button
                          onClick={() => handleOpenModal(institution)}
                          className="text-primary-600 hover:text-primary-900 mr-4"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(institution)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {institutions.length === 0 && !loading && (
                <div className="text-center py-12 text-gray-500">
                  No institutions found. Add your first institution to get started.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingInstitution ? 'Edit Institution' : 'Add Institution'}
      >
        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Name
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
              <label htmlFor="identifier" className="block text-sm font-medium text-gray-700">
                Identifier
              </label>
              <input
                type="text"
                id="identifier"
                className="input-field mt-1"
                value={formData.identifier}
                onChange={(e) => setFormData({ ...formData, identifier: e.target.value })}
                required
              />
            </div>
          </div>
          <div className="mt-5 sm:mt-6 sm:flex sm:flex-row-reverse">
            <button type="submit" className="btn-primary w-full sm:w-auto sm:ml-3">
              {editingInstitution ? 'Update' : 'Create'}
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
          setDeletingInstitution(null);
        }}
        itemName="Institution"
      />
    </div>
  );
};
