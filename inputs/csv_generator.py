import csv
import random
from datetime import datetime, timedelta

def generate_insurance_data(num_records=1):
    """Genera datos de seguros para testing"""
    
    # Arrays de datos para generar valores aleatorios
    tipos_producto = ['Vitalicio', 'Temporal']
    sexos = ['Male', 'Female']
    paises = ['Argentina', 'Chile', 'Colombia', 'Mexico', 'Peru', 'Uruguay', 'Brasil', 'Ecuador']
    reaseguradoras = ['Munich Re', 'Swiss Re', 'Hannover Re', 'SCOR', 'Lloyds', 'Berkshire Re', 'Partner Re', 'Everest Re']
    frecuencias_prima = ['Mensual', 'Trimestral', 'Semestral', 'Anual']
    
    def random_date(start_date, end_date):
        """Genera fecha aleatoria entre dos fechas"""
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        return start_date + timedelta(days=random_days)
    
    # Crear archivo CSV
    with open(f'data_{int(num_records/1000)}k.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'ID', 'tipo_producto', 'temp_idx', 'Sex', 'inception_date', 
            'birth_date', 'sum_insured', 'tariff_grp', 'country', 
            'reins_name', 'annual_prem', 'prem_frecuency', 'comission_precentage'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Generar registros
        for i in range(1, num_records + 1):
            tipo_producto = random.choice(tipos_producto)
            temp_idx = random.randint(1, 5) if tipo_producto == 'Temporal' else ''
            sexo = random.choice(sexos)
            
            # Fechas
            birth_date = random_date(datetime(1950, 1, 1), datetime(1990, 12, 31))
            inception_date = random_date(datetime(2020, 1, 1), datetime(2024, 12, 31))
            
            # Otros campos
            suma_asegurada = random.randint(10000, 1000000)
            grupo_tarifario = random.randint(1, 10)
            pais = random.choice(paises)
            reaseguradora = random.choice(reaseguradoras)
            prima_anual = round(random.uniform(500, 50000), 2)
            frecuencia = random.choice(frecuencias_prima)
            comision = round(random.uniform(5, 25), 1)
            
            # Escribir registro
            writer.writerow({
                'ID': i,
                'tipo_producto': tipo_producto,
                'temp_idx': temp_idx,
                'Sex': sexo,
                'inception_date': inception_date.strftime('%d/%m/%Y'),
                'birth_date': birth_date.strftime('%d/%m/%Y'),
                'sum_insured': suma_asegurada,
                'tariff_grp': grupo_tarifario,
                'country': pais,
                'reins_name': reaseguradora,
                'annual_prem': prima_anual,
                'prem_frecuency': frecuencia,
                'comission_precentage': comision
            })
            
            # Mostrar progreso cada 1000 registros
            if i % int(num_records/1000) == 0:
                print(f"Generados {i} registros...")
    
    print(f"✅ Archivo 'data_{int(num_records/1000)}k.csv' creado exitosamente con {num_records} registros!")
    
    # Mostrar preview de las primeras 5 líneas
    print("\n📋 Preview de las primeras 5 líneas:")
    with open(f'data_{int(num_records/1000)}k.csv', 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 6:  # Header + 5 líneas
                print(line.strip())
            else:
                break

if __name__ == "__main__":
    generate_insurance_data(2000000)