"""
Constantes de configuración para planes y precios.
Esto centraliza la información de planes para fácil mantenimiento.
"""

# Mapeo de planes: {monto_ars: (nombre_plan, dias_vigencia)}
PLAN_MAPPING = {
    45000: ('Mensual', 30),      # Plan Mensual: $45.000 ARS por 30 días
    130000: ('Trimestral', 90),  # Plan Trimestral: $130.000 ARS por 90 días
}

# Información completa de planes (opcional, para futuros usos)
PLANS = {
    'Mensual': {
        'precio_ars': 45000,
        'precio_usd': 30,  # Aproximado
        'duracion_dias': 30,
        'descripcion': 'Accedé a todas las clases en vivo y rutinas personalizadas.'
    },
    'Trimestral': {
        'precio_ars': 130000,
        'precio_usd': 90,  # Aproximado
        'duracion_dias': 90,
        'descripcion': 'Ahorro especial con acceso completo durante 3 meses.'
    }
}

def get_plan_by_amount(amount):
    """
    Obtiene el nombre del plan y duración basado en el monto.
    
    Args:
        amount (float): El monto pagado
        
    Returns:
        tuple: (nombre_plan, dias_vigencia) o None si no coincide
        
    Ejemplo:
        >>> get_plan_by_amount(45000)
        ('Mensual', 30)
    """
    return PLAN_MAPPING.get(float(amount))

def get_plan_duration(plan_name):
    """
    Obtiene la duración en días de un plan por su nombre.
    
    Args:
        plan_name (str): Nombre del plan ('Mensual' o 'Trimestral')
        
    Returns:
        int: Número de días de vigencia
    """
    for amount, (name, days) in PLAN_MAPPING.items():
        if name.lower() == plan_name.lower():
            return days
    return 30  # Fallback a 30 días

def get_plan_price(plan_name, currency='ARS'):
    """
    Obtiene el precio de un plan.
    
    Args:
        plan_name (str): Nombre del plan
        currency (str): 'ARS' o 'USD'
        
    Returns:
        float: Precio del plan
    """
    plan = PLANS.get(plan_name)
    if not plan:
        return None
    
    if currency.upper() == 'ARS':
        return plan.get('precio_ars')
    elif currency.upper() == 'USD':
        return plan.get('precio_usd')
    return None
