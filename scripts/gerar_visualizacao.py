import os
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Configura backend não interativo para evitar abertura de janelas GUI
import matplotlib.pyplot as plt

def main():
    # 1. Definição de caminhos do projeto (Pasta output/analise e output/visualizacao)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'sensores_simulados.csv')
    json_path = os.path.join(base_dir, 'output', 'analise', 'detecoes.json')
    output_dir = os.path.join(base_dir, 'output', 'visualizacao')
    
    print("=================================================================")
    print(" FEUP Predictive Maintenance - Gerador de Visualização Gráfica")
    print("=================================================================")
    
    # 2. Verificação de arquivos necessários
    if not os.path.exists(data_path):
        print(f"[ERRO] Dataset não encontrado em: {data_path}")
        return
    if not os.path.exists(json_path):
        print(f"[ERRO] Ficheiro de deteções não encontrado em: {json_path}")
        print("Por favor, execute primeiro o script de análise (scripts/analise_preditiva.py)")
        return
        
    # 3. Carregar dados e deteções
    print("[INFO] A carregar os dados dos sensores e o relatório de deteções...")
    df = pd.read_csv(data_path, encoding='utf-8-sig')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    with open(json_path, 'r', encoding='utf-8') as f:
        anomalies_data = json.load(f)
        
    equipamentos = df['equipamento'].unique()
    
    for equip in equipamentos:
        df_equip = df[df['equipamento'] == equip]
        anomalies_data_equip = anomalies_data.get(equip, [])
        
        # Criar um DataFrame a partir do JSON de anomalias
        if len(anomalies_data_equip) > 0:
            df_anomalies = pd.DataFrame(anomalies_data_equip)
            df_anomalies['timestamp'] = pd.to_datetime(df_anomalies['timestamp'])
        else:
            df_anomalies = pd.DataFrame(columns=['timestamp', 'temperatura', 'vibracao'])
            
        print(f"[INFO] [{equip}] Dados gerais: {len(df_equip)} pontos. Anomalias: {len(df_anomalies)} pontos.")
        
        # 4. Configurar e desenhar os gráficos (Subplots para Temperatura e Vibração)
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        fig.suptitle(f'FEUP - Monitorização Preditiva: {equip}\nTelemetria de Sensores (24 Horas)', 
                     fontsize=16, fontweight='bold', color='#1a365d')
        
        # --- GRÁFICO 1: TEMPERATURA ---
        ax1.plot(df_equip['timestamp'], df_equip['temperatura'], color='#2b6cb0', label='Temperatura (°C)', linewidth=1.5, alpha=0.85)
        
        # Marcar anomalias de temperatura
        if not df_anomalies.empty:
            ax1.scatter(df_anomalies['timestamp'], df_anomalies['temperatura'], 
                        color='#e53e3e', label='Anomalias Detetadas (I-Forest)', 
                        edgecolors='black', s=45, zorder=5)
            
        # Adicionar limites críticos e de alerta definidos no README
        ax1.axhline(85, color='#d69e2e', linestyle='--', linewidth=1.2, label='Limiar de Alerta (Warning > 85°C)', alpha=0.8)
        ax1.axhline(105, color='#e53e3e', linestyle='-.', linewidth=1.2, label='Limiar Crítico (Fault > 105°C)', alpha=0.8)
        
        ax1.set_ylabel('Temperatura (°C)', fontsize=12, fontweight='bold', color='#2d3748')
        ax1.title.set_text('Sensor de Temperatura do Motor')
        ax1.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
        ax1.grid(True, linestyle=':', alpha=0.6)
        
        # --- GRÁFICO 2: VIBRAÇÃO ---
        ax2.plot(df_equip['timestamp'], df_equip['vibracao'], color='#2c5282', label='Vibração RMS (mm/s)', linewidth=1.5, alpha=0.85)
        
        # Marcar anomalias de vibração
        if not df_anomalies.empty:
            ax2.scatter(df_anomalies['timestamp'], df_anomalies['vibracao'], 
                        color='#e53e3e', label='Anomalias Detetadas (I-Forest)', 
                        edgecolors='black', s=45, zorder=5)
            
        # Adicionar limites críticos e de alerta de vibração (ISO 10816-3)
        ax2.axhline(2.8, color='#d69e2e', linestyle='--', linewidth=1.2, label='Limiar de Alerta (Warning > 2.8 mm/s)', alpha=0.8)
        ax2.axhline(4.5, color='#e53e3e', linestyle='-.', linewidth=1.2, label='Limiar Crítico (Fault > 4.5 mm/s)', alpha=0.8)
        
        ax2.set_ylabel('Vibração RMS (mm/s)', fontsize=12, fontweight='bold', color='#2d3748')
        ax2.set_xlabel('Timestamp (Hora de Leitura)', fontsize=12, fontweight='bold', color='#2d3748')
        ax2.title.set_text('Sensor de Vibração Global (Severidade RMS)')
        ax2.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
        ax2.grid(True, linestyle=':', alpha=0.6)
        
        # Formatação do eixo X (tempo)
        fig.autofmt_xdate()
        
        # Ajustar layout para evitar sobreposições
        plt.tight_layout()
        
        # 5. Guardar o gráfico como imagem estática de alta definição e libertar recursos
        os.makedirs(output_dir, exist_ok=True)
        # Sanitizar nome da máquina para nome do ficheiro (ex: remover espaços ou não)
        safe_equip_name = equip.replace(' ', '_').replace('/', '-')
        output_img_path = os.path.join(output_dir, f'grafico_sensores_{safe_equip_name}.png')
        plt.savefig(output_img_path, dpi=300, bbox_inches='tight')
        plt.close(fig)  # Liberta a memória RAM do gráfico e evita a abertura de qualquer janela GUI
        
        print(f"[SUCESSO] [{equip}] Gráfico analítico exportado silenciosamente para: {output_img_path}")
    print("=================================================================")

if __name__ == '__main__':
    main()
