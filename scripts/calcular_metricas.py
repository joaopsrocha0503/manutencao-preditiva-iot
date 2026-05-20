import os
import json
import pandas as pd

def main():
    # 1. Definição de caminhos do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'sensores_simulados.csv')
    json_path = os.path.join(base_dir, 'output', 'analise', 'detecoes.json')
    output_dir = os.path.join(base_dir, 'output', 'analise')
    metrics_path = os.path.join(output_dir, 'metricas_gestao.json')
    
    print("=================================================================")
    print(" FEUP Industrial Management - Motor de Cálculo de KPIs (OEE/MTBF)")
    print("=================================================================")
    
    # 2. Verificação de arquivos necessários
    if not os.path.exists(data_path):
        print(f"[ERRO] Dataset não encontrado em: {data_path}")
        return
    if not os.path.exists(json_path):
        print(f"[ERRO] Ficheiro de deteções não encontrado em: {json_path}")
        return
        
    # 3. Carregar os dados
    df_raw = pd.read_csv(data_path, encoding='utf-8-sig')
    df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'])
    
    with open(json_path, 'r', encoding='utf-8') as f:
        detecoes_por_maquina = json.load(f)
        
    print("[INFO] Dados de telemetria e deteções carregados com sucesso.")
    
    kpis_totais = {}
    
    equipamentos = df_raw['equipamento'].unique()
    for equip in equipamentos:
        df_equip = df_raw[df_raw['equipamento'] == equip]
        anomalies = detecoes_por_maquina.get(equip, [])
        
        downtime_df = df_equip[df_equip['estado_operacional'].str.contains('Parado', na=False)]
    
        # Como a amostragem é a cada 5 minutos, cada registo equivale a 5 minutos de paragem
        sampling_interval_min = 5
        downtime_total_min = len(downtime_df) * sampling_interval_min
        downtime_total_hours = downtime_total_min / 60.0
        
        # --- CÁLCULO DO PERÍODO OPERACIONAL TOTAL ---
        total_time_delta = df_equip['timestamp'].max() - df_equip['timestamp'].min()
        total_time_hours = total_time_delta.total_seconds() / 3600.0
        
        # --- CÁLCULO DE UPTIME (Tempo de Funcionamento) ---
        uptime_hours = total_time_hours - downtime_total_hours
        uptime_min = uptime_hours * 60.0
        
        # --- CÁLCULO DO NÚMERO DE FALHAS E MTBF ---
        # Em termos industriais, uma falha preditiva é um "evento" de anomalia contígua,
        # e não apenas leituras isoladas a cada 5 minutos.
        num_failures = 0
        failure_events = []
        
        if len(anomalies) > 0:
            # Criar DataFrame temporário das deteções ordenado por tempo
            df_anom = pd.DataFrame(anomalies)
            df_anom['timestamp'] = pd.to_datetime(df_anom['timestamp'])
            df_anom = df_anom.sort_values(by='timestamp')
            
            # Identificar eventos contíguos
            current_event = [df_anom.iloc[0]]
            
            for idx in range(1, len(df_anom)):
                diff = (df_anom.iloc[idx]['timestamp'] - df_anom.iloc[idx-1]['timestamp']).total_seconds() / 60.0
                if diff <= 15:  # Pertence ao mesmo evento de falha (intervalo <= 15 min)
                    current_event.append(df_anom.iloc[idx])
                else:
                    # Gravar evento anterior e iniciar novo
                    failure_events.append(current_event)
                    current_event = [df_anom.iloc[idx]]
            # Adicionar o último evento
            failure_events.append(current_event)
            
            num_failures = len(failure_events)
        
        # Cálculo do MTBF (Mean Time Between Failures)
        if num_failures > 0:
            mtbf_hours = uptime_hours / num_failures
        else:
            mtbf_hours = uptime_hours  # Se não houver falhas, o MTBF é o tempo total
            
        # --- CÁLCULO DE DISPONIBILIDADE (Availability KPI) ---
        availability_pct = (uptime_hours / total_time_hours) * 100.0 if total_time_hours > 0 else 0.0
        
        # --- CÁLCULO ADICIONAL: MTTR (Mean Time To Repair) ---
        # Identificamos paragens contíguas usando a mesma lógica com o downtime_df robusto
        num_interventions = 0
        if len(downtime_df) > 0:
            downtime_sorted = downtime_df.sort_values(by='timestamp')
            interventions = 1
            for idx in range(1, len(downtime_sorted)):
                diff = (downtime_sorted.iloc[idx]['timestamp'] - downtime_sorted.iloc[idx-1]['timestamp']).total_seconds() / 60.0
                if diff > 15:
                    interventions += 1
            num_interventions = interventions
            
        if num_interventions > 0:
            mttr_hours = downtime_total_hours / num_interventions
        else:
            mttr_hours = 0.0
            
        # 4. Apresentar os resultados no terminal
        print(f"\n>>> INDICADORES DE GESTÃO DA MANUTENÇÃO (KPIs) - {equip} <<<")
        print(f"  * Período de Análise Total : {total_time_hours:.2f} horas")
        print(f"  * Tempo de Inatividade (Downtime) : {downtime_total_hours:.2f} horas ({downtime_total_min} minutos)")
        print(f"  * Tempo Ativo (Uptime)       : {uptime_hours:.2f} horas ({uptime_min:.1f} minutos)")
        print(f"  * Disponibilidade do Ativo   : {availability_pct:.2f}%")
        print(f"  * Eventos de Falha Detetados : {num_failures} eventos contíguos")
        if num_failures > 0:
            print(f"  * MTBF (Tempo Médio Entre Falhas)  : {mtbf_hours:.2f} horas")
        else:
            print(f"  * MTBF (Tempo Médio Entre Falhas)  : N/A (Sem falhas detetadas)")
        print(f"  * MTTR (Tempo Médio de Reparação)   : {mttr_hours:.2f} horas ({mttr_hours*60:.1f} minutos)")
    
        # 5. Guardar os KPIs estruturados
        kpis_totais[equip] = {
            "kpis_gestao": {
                "periodo_analise_horas": round(total_time_hours, 2),
                "downtime_total_minutos": int(downtime_total_min),
                "downtime_total_horas": round(downtime_total_hours, 2),
                "uptime_total_horas": round(uptime_hours, 2),
                "disponibilidade_percentagem": round(availability_pct, 2),
                "numero_falhas_eventos": int(num_failures),
                "mtbf_horas": round(mtbf_hours, 2) if num_failures > 0 else None,
                "mttr_horas": round(mttr_hours, 2),
                "mttr_minutos": round(mttr_hours * 60, 1)
            },
            "detalhes_eventos_falha": [
                {
                    "evento_id": idx + 1,
                    "inicio": ev[0]['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    "fim": ev[-1]['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    "duracao_minutos": len(ev) * sampling_interval_min,
                    "estado_inicial": ev[0]['estado_operacional_simulado']
                } for idx, ev in enumerate(failure_events)
            ]
        }
    
    os.makedirs(output_dir, exist_ok=True)
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(kpis_totais, f, indent=4, ensure_ascii=False)
        
    print(f"\n[SUCESSO] KPIs industriais exportados para: {metrics_path}")
    print("=================================================================")

if __name__ == '__main__':
    main()
