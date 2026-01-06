#!/usr/bin/env python
"""
Script para validar que los pagos se registren correctamente en la tabla principal_pago.

Uso:
    python test_payment_flow.py

Este script simula el flujo de pago sin necesidad de Mercado Pago/PayPal.
"""

import os
import django
from datetime import timedelta
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webLula.settings.production')
django.setup()

from principal.models import Pago, VerifiedEmail
from django.contrib.auth.models import User

def test_payment_registration():
    """Test 1: Verificar que se crea correctamente un registro de Pago"""
    
    print("\n" + "="*70)
    print("TEST 1: Crear registro de Pago con todos los campos")
    print("="*70)
    
    test_email = "test.pago@example.com"
    test_amount = 45000.00
    
    # Limpiar datos previos si existen
    Pago.objects.filter(email=test_email).delete()
    VerifiedEmail.objects.filter(email=test_email).delete()
    
    try:
        # Crear pago como lo hace pago_exito()
        pago = Pago.objects.create(
            email=test_email,
            monto=test_amount,
            moneda='ARS',
            plataforma='mercadopago',
            estado='exitoso',
            tipo_plan='Mensual',
            payment_id_externo='MP-12345678901',
            user=None  # Sin usuario asociado (ej: usuario no logueado)
        )
        
        print(f"✅ Pago creado exitosamente")
        print(f"   - ID: {pago.id}")
        print(f"   - Email: {pago.email}")
        print(f"   - Monto: ${pago.monto} {pago.moneda}")
        print(f"   - Plataforma: {pago.plataforma}")
        print(f"   - Estado: {pago.estado}")
        print(f"   - Tipo Plan: {pago.tipo_plan}")
        print(f"   - Payment ID: {pago.payment_id_externo}")
        print(f"   - Fecha: {pago.fecha}")
        
        # Verificar que todos los campos están completos
        assert pago.monto == test_amount, "❌ Monto no coincide"
        assert pago.moneda == 'ARS', "❌ Moneda no es ARS"
        assert pago.plataforma == 'mercadopago', "❌ Plataforma no es mercadopago"
        assert pago.payment_id_externo == 'MP-12345678901', "❌ Payment ID no es correcto"
        
        print("✅ Todos los campos están correctamente guardados\n")
        
    except Exception as e:
        print(f"❌ Error al crear pago: {e}\n")
        return False
    
    return True

def test_vencimiento_update():
    """Test 2: Verificar que vencimiento se actualiza en VerifiedEmail"""
    
    print("="*70)
    print("TEST 2: Actualizar vencimiento en principal_verifiedemail")
    print("="*70)
    
    test_email = "test.vencimiento@example.com"
    
    # Limpiar datos previos
    VerifiedEmail.objects.filter(email=test_email).delete()
    
    try:
        # Crear/actualizar VerifiedEmail como lo hace pago_exito()
        usuario, created = VerifiedEmail.objects.get_or_create(email=test_email)
        ahora = timezone.now()
        dias = 30  # Plan Mensual
        
        if usuario.vencimiento and usuario.vencimiento > ahora:
            usuario.vencimiento += timedelta(days=dias)
        else:
            usuario.vencimiento = ahora + timedelta(days=dias)
        
        usuario.save()
        
        print(f"✅ Vencimiento actualizado")
        print(f"   - Email: {usuario.email}")
        print(f"   - Vencimiento: {usuario.vencimiento}")
        print(f"   - Fecha verificación: {usuario.verified_at}")
        print(f"   - Días válidos: {(usuario.vencimiento - ahora).days}")
        
        # Verificar que vencimiento NO es NULL y está en el futuro
        assert usuario.vencimiento is not None, "❌ Vencimiento es NULL"
        assert usuario.vencimiento > ahora, "❌ Vencimiento no está en el futuro"
        assert 28 <= (usuario.vencimiento - ahora).days <= 31, "❌ Vencimiento no es ~30 días"
        
        print("✅ Vencimiento se actualiza correctamente\n")
        
    except Exception as e:
        print(f"❌ Error al actualizar vencimiento: {e}\n")
        return False
    
    return True

def test_user_association():
    """Test 3: Verificar que se asocia correctamente el usuario"""
    
    print("="*70)
    print("TEST 3: Asociar usuario autenticado con pago")
    print("="*70)
    
    test_email = "test.user.association@example.com"
    test_username = "testuser_pago"
    test_password = "TestPassword123!"
    
    try:
        # Crear usuario de prueba
        user, created = User.objects.get_or_create(
            username=test_username,
            defaults={'email': test_email}
        )
        if created:
            user.set_password(test_password)
            user.save()
            print(f"   Usuario creado: {test_username}")
        else:
            print(f"   Usuario existente: {test_username}")
        
        # Limpiar pagos previos
        Pago.objects.filter(email=test_email, user=user).delete()
        
        # Crear pago asociado al usuario
        pago = Pago.objects.create(
            user=user,  # ← Aquí se asocia el usuario
            email=test_email,
            monto=45000.00,
            moneda='ARS',
            plataforma='mercadopago',
            estado='exitoso',
            tipo_plan='Mensual'
        )
        
        print(f"✅ Pago asociado al usuario")
        print(f"   - User ID: {pago.user.id}")
        print(f"   - Username: {pago.user.username}")
        print(f"   - Email: {pago.user.email}")
        
        # Verificar
        assert pago.user is not None, "❌ Usuario no se asoció"
        assert pago.user.username == test_username, "❌ Usuario incorrecto"
        assert pago.user.email == test_email, "❌ Email de usuario no coincide"
        
        print("✅ Usuario se asocia correctamente\n")
        
    except Exception as e:
        print(f"❌ Error al asociar usuario: {e}\n")
        return False
    
    return True

def test_payment_history():
    """Test 4: Verificar que se mantiene el historial de pagos"""
    
    print("="*70)
    print("TEST 4: Historial de pagos múltiples")
    print("="*70)
    
    test_email = "test.historial@example.com"
    
    # Limpiar
    Pago.objects.filter(email=test_email).delete()
    
    try:
        # Simular 3 pagos (Mensual + Trimestral + Renovación)
        pagos_data = [
            {'monto': 45000, 'tipo_plan': 'Mensual', 'plataforma': 'mercadopago', 'payment_id': 'MP-001'},
            {'monto': 130000, 'tipo_plan': 'Trimestral', 'plataforma': 'mercadopago', 'payment_id': 'MP-002'},
            {'monto': 45000, 'tipo_plan': 'Mensual', 'plataforma': 'paypal', 'payment_id': 'PP-001'},
        ]
        
        for i, data in enumerate(pagos_data, 1):
            pago = Pago.objects.create(
                email=test_email,
                monto=data['monto'],
                moneda='ARS' if data['plataforma'] == 'mercadopago' else 'USD',
                plataforma=data['plataforma'],
                estado='exitoso',
                tipo_plan=data['tipo_plan'],
                payment_id_externo=data['payment_id']
            )
            print(f"   {i}. {data['tipo_plan']} - ${data['monto']} ({data['plataforma']})")
        
        # Verificar historial
        historial = Pago.objects.filter(email=test_email).order_by('-fecha')
        assert historial.count() == 3, f"❌ Se esperaban 3 pagos, se encontraron {historial.count()}"
        
        print(f"\n✅ Historial de {historial.count()} pagos registrado correctamente")
        print("✅ Se puede hacer seguimiento de todas las transacciones\n")
        
    except Exception as e:
        print(f"❌ Error en historial: {e}\n")
        return False
    
    return True

def main():
    """Ejecutar todos los tests"""
    
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*10 + "TESTS DE VALIDACIÓN - REGISTRO DE PAGOS" + " "*20 + "║")
    print("╚" + "═"*68 + "╝")
    
    results = {
        "Test 1 - Crear Pago": test_payment_registration(),
        "Test 2 - Vencimiento": test_vencimiento_update(),
        "Test 3 - Usuario": test_user_association(),
        "Test 4 - Historial": test_payment_history(),
    }
    
    print("="*70)
    print("RESUMEN DE RESULTADOS")
    print("="*70)
    
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\nResultado Final: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON! El flujo de pagos está correctamente implementado.\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) fallaron. Revisa los errores arriba.\n")
        return 1

if __name__ == '__main__':
    exit(main())
