import os
import json
import pandas as pd
from sklearn.linear_model import LinearRegression

def main():
    # 1. Definição de caminhos do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'sensores_simulados.csv')
    output_dir = os.path.join(base_dir, 'output', 'analise')
    rul_path = os.path.join(output_dir, 'previsao_rul.json')
    
    print("=================================================================")
    print(" FEUP Predictive Maintenance - Motor de Cálculo de RUL")
    print("=================================================================")
    
    if not os.path.exists(data_path):
        print(f"[ERRO] Dataset não encontrado em: {data_path}")
        return
        
    # 2. Carregar os dados
    print(f"[INFO] A carregar dados do sensor para projeção de RUL...")
    df = pd.read_csv(data_path, encoding='utf-8-sig')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 3. Processar por equipamento
    equipamentos = df['equipamento'].unique()
    rul_totais = {}
    
    for equip in equipamentos:
        df_equip = df[df['equipamento'] == equip]
        degradacao_df = df_equip[df_equip['estado_operacional'] == 'Alerta - Sobreaquecimento Incipiente'].copy()
        
        if degradacao_df.empty:
            print(f"[{equip}] Nenhum evento de 'Sobreaquecimento Incipiente' detetado.")
            continue
            
        print(f"\n[INFO] [{equip}] Evento de degradação isolado: {len(degradacao_df)} leituras encontradas.")
        
        start_time = degradacao_df['timestamp'].min()
        degradacao_df['minutos_passados'] = (degradacao_df['timestamp'] - start_time).dt.total_seconds() / 60.0
        
        X = degradacao_df[['minutos_passados']]
        y = degradacao_df['temperatura']
        
        model = LinearRegression()
        model.fit(X, y)
        
        m = model.coef_[0]
        b = model.intercept_
        
        print(f"[{equip}] Modelo treinado. Tendência: Temp = {m:.4f} * min + {b:.2f}")
        
        if m <= 0:
            print(f"[{equip}] A temperatura não está a subir. Não é possível calcular RUL para sobreaquecimento.")
            continue
            
        limite_falha = 105.0
        minutos_ate_falha = (limite_falha - b) / m
        
        hora_projetada = start_time + pd.Timedelta(minutes=minutos_ate_falha)
        ultima_leitura = degradacao_df['timestamp'].max()
        rul_timedelta = hora_projetada - ultima_leitura
        rul_horas = rul_timedelta.total_seconds() / 3600.0
        
        print(f"\n>>> PROJEÇÃO DE RUL - {equip} <<<")
        print(f"  * Última leitura do alerta : {ultima_leitura}")
        print(f"  * Limite Crítico           : {limite_falha}°C")
        print(f"  * Falha Projetada às       : {hora_projetada.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  * RUL Calculado            : {rul_horas:.2f} horas")
        
        rul_totais[equip] = {
            "ultima_leitura": ultima_leitura.strftime('%Y-%m-%d %H:%M:%S'),
            "limite_critico_temperatura": limite_falha,
            "timestamp_projetado_falha": hora_projetada.strftime('%Y-%m-%d %H:%M:%S'),
            "rul_horas": round(rul_horas, 2),
            "modelo": {
                "coeficiente_declinio_min": round(m, 4),
                "intersecao_base": round(b, 2)
            }
        }
    
    os.makedirs(output_dir, exist_ok=True)
    with open(rul_path, 'w', encoding='utf-8') as f:
        json.dump(rul_totais, f, indent=4, ensure_ascii=False)
        
    print(f"\n[SUCESSO] Previsão de RUL exportada para: {rul_path}")
    print("=================================================================")

if __name__ == '__main__':
    main()
