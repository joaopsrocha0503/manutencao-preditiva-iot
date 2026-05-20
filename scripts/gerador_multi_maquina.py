import os
import csv
import random
from datetime import datetime, timedelta

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    csv_path = os.path.join(data_dir, 'sensores_simulados.csv')
    
    os.makedirs(data_dir, exist_ok=True)
    
    # Parâmetros base
    start_time = datetime(2026, 5, 20, 0, 0, 0)
    interval_minutes = 5
    num_readings = 24 * (60 // interval_minutes) # 288 readings
    
    equipamentos = ["Motor de Indução A", "Motor de Indução B", "Torno CNC"]
    
    print("=================================================================")
    print(" FEUP Data Generator - Multi-Máquina (Fleet Management)")
    print("=================================================================")
    print(f"[INFO] A gerar {num_readings} leituras por equipamento...")
    
    rows = []
    
    for i in range(num_readings):
        current_time = start_time + timedelta(minutes=i*interval_minutes)
        timestamp_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # 1. Motor de Indução A (Degradação Térmica Progressiva)
        if i < 160: # Até às ~13:20
            temp_A = round(random.uniform(50.0, 55.0), 2)
            vib_A = round(random.uniform(0.5, 1.2), 2)
            estado_A = "Operacional"
        elif i < 190: # 13:20 a 15:50 (Pequena anomalia)
            temp_A = round(random.uniform(58.0, 65.0), 2)
            vib_A = round(random.uniform(1.5, 2.0), 2)
            estado_A = "Operacional" # Ainda não crítico, mas a subir
        elif i < 220: # 15:50 a 18:20 (Degradação Severa)
            # Aumenta de 65 até 80
            temp_A = round(65.0 + (i - 190) * 0.5 + random.uniform(0, 2), 2)
            vib_A = round(random.uniform(2.0, 3.5), 2)
            estado_A = "Alerta - Sobreaquecimento Incipiente"
        else: # 18:20 em diante (Parado)
            temp_A = round(random.uniform(25.0, 35.0), 2) # A arrefecer
            vib_A = 0.0
            estado_A = "Parado - Intervenção de Manutenção"
            
        rows.append([timestamp_str, "Motor de Indução A", temp_A, vib_A, estado_A])
        
        # 2. Motor de Indução B (100% Saudável)
        temp_B = round(random.uniform(48.0, 56.0), 2)
        vib_B = round(random.uniform(0.4, 1.0), 2)
        estado_B = "Operacional"
        rows.append([timestamp_str, "Motor de Indução B", temp_B, vib_B, estado_B])
        
        # 3. Torno CNC (Picos aleatórios de vibração, mas sem falha crítica)
        if random.random() < 0.05: # 5% chance de pico de vibração
            temp_C = round(random.uniform(40.0, 45.0), 2)
            vib_C = round(random.uniform(4.5, 6.0), 2)
            estado_C = "Alerta - Vibração Anómala"
        else:
            temp_C = round(random.uniform(38.0, 43.0), 2)
            vib_C = round(random.uniform(0.8, 1.8), 2)
            estado_C = "Operacional"
        rows.append([timestamp_str, "Torno CNC", temp_C, vib_C, estado_C])
        
    # Guardar no CSV (com encoding utf-8-sig para garantir leitura robusta do português)
    with open(csv_path, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "equipamento", "temperatura", "vibracao", "estado_operacional"])
        writer.writerows(rows)
        
    print(f"[SUCESSO] Base de dados gerada com sucesso: {len(rows)} registos totais.")
    print(f"[SUCESSO] Guardado em: {csv_path}")
    print("=================================================================")

if __name__ == '__main__':
    main()
