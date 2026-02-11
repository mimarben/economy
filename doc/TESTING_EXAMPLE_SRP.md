"""
Example: Testing with SRP - Much easier & cleaner

Muestra cómo el código refactorizado es 10x más fácil de testear.
"""

# ============================================================================
# ❌ ANTES: Testing casi imposible (dependencias globales, BD real, etc)
# ============================================================================

from unittest import mock
import pytest

def test_create_income_old_way():
    """❌ Testing ANTES: Necesitamos TODO"""
    
    # Problema 1: Necesitamos una BD real
    db = create_test_db()  # 😅 Lenta, complicada
    
    # Problema 2: Necesitamos crear datos reales para validar FKs
    user = User(name="Test", dni="12345678Z", ...)
    source = Source(name="Salary", type=SourceTypeEnum.income)
    category = IncomesCategory(name="Salary")
    account = Account(name="Main", iban="...", ...)
    db.add_all([user, source, category, account])
    db.commit()
    
    # Problema 3: Necesitamos hacer un request HTTP simulado
    with app.test_client() as client:
        response = client.post('/api/incomes', json={
            'name': 'Monthly salary',
            'amount': 3000,
            'date': '2024-01-15',
            'user_id': user.id,
            'source_id': source.id,
            'category_id': category.id,
            'account_id': account.id,
            'currency': 'EUR'
        })
    
    # Problema 4: Muchas afirmaciones para poco código
    assert response.status_code == 201
    assert response.json['response']['name'] == 'Monthly salary'
    # ... etc
    
    # 😭 Test: 50 líneas, lento, frágil, difícil de entender


# ============================================================================
# ✅ DESPUÉS: Testing limpio, rápido, enfocado
# ============================================================================

import unittest
from unittest.mock import Mock, MagicMock, patch

class TestIncomeRepository(unittest.TestCase):
    """Test Repository - Data access layer"""
    
    def setUp(self):
        self.mock_db = Mock()
        self.repository = IncomeRepository(self.mock_db)
    
    def test_validate_foreign_keys_all_exist(self):
        """✅ Test FK validation when all FKs exist"""
        
        # Arrange: Mock que todas las FKs existen
        self.mock_db.query.return_value.filter.return_value.first.return_value = Mock()
        
        # Act
        is_valid, error = self.repository.validate_foreign_keys(
            user_id=1,
            source_id=1,
            category_id=1,
            account_id=1
        )
        
        # Assert
        assert is_valid is True
        assert error is None
    
    def test_validate_foreign_keys_user_not_found(self):
        """✅ Test FK validation when user doesn't exist"""
        
        # Arrange: Mock que User no existe pero otros sí
        def side_effect(model):
            if model == User:
                return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None))))
            return Mock(filter=Mock(return_value=Mock(first=Mock(return_value=Mock()))))
        
        self.mock_db.query.side_effect = side_effect
        
        # Act
        is_valid, error = self.repository.validate_foreign_keys(1, 1, 1, 1)
        
        # Assert
        assert is_valid is False
        assert error == "USER_NOT_FOUND"
    
    def test_get_by_user(self):
        """✅ Test get incomes by user"""
        
        # Arrange
        mock_incomes = [Mock(id=1), Mock(id=2)]
        self.mock_db.query.return_value.filter.return_value.all.return_value = mock_incomes
        
        # Act
        result = self.repository.get_by_user(user_id=1)
        
        # Assert
        assert result == mock_incomes


class TestIncomeService(unittest.TestCase):
    """Test Service - Business logic layer"""
    
    def setUp(self):
        self.mock_db = Mock()
        self.service = IncomeService(self.mock_db)
        # Mock el repository
        self.service.repository = Mock()
    
    def test_create_income_success(self):
        """✅ Test income creation with valid data"""
        
        # Arrange
        income_data = IncomeCreate(
            name='Salary',
            amount=3000,
            date=datetime(2024, 1, 15),
            currency='€',
            user_id=1,
            source_id=1,
            category_id=1,
            account_id=1
        )
        
        # Mock que FKs son válidas
        self.service.repository.validate_foreign_keys.return_value = (True, None)
        
        # Mock que se crea el income
        mock_income = Mock(id=1, name='Salary', amount=3000)
        self.service.repository.create.return_value = mock_income
        
        # Act
        result = self.service.create_income(income_data)
        
        # Assert
        assert result.id == 1
        self.service.repository.validate_foreign_keys.assert_called_once()
        self.service.repository.create.assert_called_once()
    
    def test_create_income_user_not_found(self):
        """✅ Test income creation when user doesn't exist"""
        
        # Arrange
        income_data = IncomeCreate(
            name='Salary',
            amount=3000,
            date=datetime(2024, 1, 15),
            currency='€',
            user_id=999,
            source_id=1,
            category_id=1,
            account_id=1
        )
        
        # Mock que FKs NO son válidas
        self.service.repository.validate_foreign_keys.return_value = (False, "USER_NOT_FOUND")
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.service.create_income(income_data)
        
        assert "USER_NOT_FOUND" in str(exc_info.value)
        self.service.repository.create.assert_not_called()
    
    def test_calculate_total_income(self):
        """✅ Test calculating total income for user"""
        
        # Arrange
        mock_incomes = [
            Mock(amount=1000),
            Mock(amount=2000),
            Mock(amount=500),
        ]
        self.service.repository.get_by_user.return_value = mock_incomes
        
        # Act
        total = self.service.calculate_total_income(user_id=1)
        
        # Assert
        assert total == 3500.0


class TestIncomeRouter(unittest.TestCase):
    """Test Router - HTTP handling"""
    
    def setUp(self):
        self.app = app.test_client()
        # Inyectar un mock del service
        self.mock_service = Mock()
    
    @patch('routers.income_router.IncomeService')
    def test_create_income_http_success(self, mock_service_class):
        """✅ Test HTTP POST /incomes"""
        
        # Arrange
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_result = IncomeRead(
            id=1,
            name='Salary',
            amount=3000,
            date=datetime(2024, 1, 15),
            currency='€',
            user_id=1,
            source_id=1,
            category_id=1,
            account_id=1
        )
        mock_service.create_income.return_value = mock_result
        
        # Act
        response = self.app.post('/api/incomes', json={
            'name': 'Salary',
            'amount': 3000,
            'date': '2024-01-15T00:00:00',
            'currency': '€',
            'user_id': 1,
            'source_id': 1,
            'category_id': 1,
            'account_id': 1
        })
        
        # Assert
        assert response.status_code == 201
        assert response.json['response']['id'] == 1
        mock_service.create_income.assert_called_once()
    
    @patch('routers.income_router.IncomeService')
    def test_create_income_http_validation_error(self, mock_service_class):
        """✅ Test HTTP POST /incomes with invalid format"""
        
        # Act: Enviar amount negativo
        response = self.app.post('/api/incomes', json={
            'name': 'Salary',
            'amount': -3000,  # ❌ Invalid
            'date': '2024-01-15T00:00:00',
            'currency': '€',
            'user_id': 1,
            'source_id': 1,
            'category_id': 1,
            'account_id': 1
        })
        
        # Assert
        assert response.status_code == 400
        assert 'VALIDATION_ERROR' in response.json['response']


# ============================================================================
# Comparación: Líneas de código y velocidad
# ============================================================================

"""
Antes:
  - 1 test = ~50 líneas
  - Setup: BD real, datos reales, requests HTTP
  - Tiempo: 2-5 segundos por test ❌
  - Riesgo: Frágil, cambios en BD rompen tests
  - Cobertura: Difícil combinar todos los casos

Después:
  - 1 test = ~10-15 líneas
  - Setup: Mocks simples
  - Tiempo: 10-50ms por test ✅
  - Riesgo: Aislado, no depende de BD
  - Cobertura: Fácil cubrir casos edge

Ahorro: 5-10x FASTER, 3-5x SIMPLER
"""

# ============================================================================
# Ejecutar tests
# ============================================================================

if __name__ == '__main__':
    # Unit tests (rápidos, mocks)
    pytest.main(['-v', '--tb=short', __file__])
    
    # O con unittest
    # unittest.main()
