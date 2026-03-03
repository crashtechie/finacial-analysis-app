"""
Factory classes for test data generation using factory_boy.
"""
import factory
from factory.django import DjangoModelFactory


class InstitutionFactory(DjangoModelFactory):
    """Factory for Institution model."""
    class Meta:
        model = 'api.Institution'

    name = factory.Faker('company')
    identifier = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-')[:50])


class AccountFactory(DjangoModelFactory):
    """Factory for Account model."""
    class Meta:
        model = 'api.Account'

    institution = factory.SubFactory(InstitutionFactory)
    name = factory.Faker('word')
    account_number = factory.Faker('numerify', text='####')
    account_type = 'checking'


class CategoryFactory(DjangoModelFactory):
    """Factory for Category model."""
    class Meta:
        model = 'api.Category'

    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: obj.name.lower())
    parent = None


class TransactionFactory(DjangoModelFactory):
    """Factory for Transaction model."""
    class Meta:
        model = 'api.Transaction'
    
    from datetime import date
    from decimal import Decimal
    
    account = factory.SubFactory(AccountFactory)
    date = factory.LazyFunction(date.today)
    description = factory.Faker('catch_phrase')
    amount = Decimal('100.00')
    status = 'posted'


class ImportLogFactory(DjangoModelFactory):
    """Factory for ImportLog model."""
    class Meta:
        model = 'api.ImportLog'

    file_name = factory.Faker('file_name')
    account = factory.SubFactory(AccountFactory)
    format_type = 'bank-1'
    status = 'success'
