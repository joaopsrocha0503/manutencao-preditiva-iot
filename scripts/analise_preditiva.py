import os
import json
import pandas as pd
from sklearn.ensemble import IsolationForest

def main():
    # 1. Definição de caminhos do projeto (Pasta output/analise)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'sensores_simulados.csv')
    report_dir = os.path.join(base_dir, 'output', 'analise')
    report_path = os.path.join(report_dir, 'detecoes.json')
    
    print("=================================================================")
    print(" FEUP Predictive Maintenance - Motor de Análise de Anomalias")
    print("=================================================================")
    
    # 2. Verificação da existência do dataset
    if not os.path.exists(data_path):
        print(f"\n[ERRO] Dataset não encontrado em: {data_path}")
        print("Por favor, execute primeiro o script de geração (scripts/generate_data.ps1)")
        return
    
    # 3. Carregar e estruturar os dados dos sensores
    print(f"\n[INFO] A carregar dados do sensor de: {data_path}...")
    df = pd.read_csv(data_path, encoding='utf-8-sig')
    
    # Limpeza básica: Converter timestamp para datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Seleção de features (Temperatura e Vibração) para o modelo Isolation Forest
    features = ['temperatura', 'vibracao']
    
    contamination_rate = 0.15
    print(f"[INFO] A configurar o Isolation Forest...")
    print(f"       -> Contaminação (Proporção Anomalias): {contamination_rate * 100}%")
    
    # 4. Processar por equipamento
    equipamentos = df['equipamento'].unique()
    
    detecoes_por_maquina = {}
    total_anomalias = 0
    
    for equip in equipamentos:
        df_equip = df[df['equipamento'] == equip].copy()
        X = df_equip[features]
        
        model = IsolationForest(
            n_estimators=100,
            contamination=contamination_rate,
            random_state=42
        )
        
        df_equip['anomaly_prediction'] = model.fit_predict(X)
        df_equip['anomaly_score'] = model.decision_function(X)
        
        anomalies = df_equip[df_equip['anomaly_prediction'] == -1].copy()
        total_anomalias += len(anomalies)
        
        anomalies_list = []
        for _, row in anomalies.iterrows():
            anomaly_entry = {
                "timestamp": row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                "temperatura": float(row['temperatura']),
                "vibracao": float(row['vibracao']),
                "estado_operacional_simulado": row['estado_operacional'],
                "score_anomalia": round(float(row['anomaly_score']), 4)
            }
            anomalies_list.append(anomaly_entry)
            
        detecoes_por_maquina[equip] = anomalies_list
    
    print(f"[SUCESSO] Treino e classificação concluídos para {len(equipamentos)} equipamentos!")
    print(f"[SUCESSO] Detetadas {total_anomalias} leituras anómalas totais.")
    
    # Criar pasta output/analise se não existir
    os.makedirs(report_dir, exist_ok=True)
    
    # Gravar o ficheiro JSON de relatórios
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(detecoes_por_maquina, f, indent=4, ensure_ascii=False)
        
    print(f"[SUCESSO] Deteções preditivas exportadas para: {report_path}")
    print("\n-----------------------------------------------------------------")
    print("  Resumo do Diagnóstico de Anomalias (Amostra Inicial)")
    print("-----------------------------------------------------------------")
    
    for equip in equipamentos:
        anoms = detecoes_por_maquina[equip]
        print(f"\n[{equip}] {len(anoms)} anomalias encontradas.")
        if len(anoms) > 0:
            amostra_size = min(3, len(anoms))
            for entry in anoms[:amostra_size]:
                print(f"  - [{entry['timestamp']}] Temp: {entry['temperatura']}°C | Vib: {entry['vibracao']} mm/s | Est: {entry['estado_operacional_simulado']}")
    print("=================================================================")

if __name__ == '__main__':
    main()
