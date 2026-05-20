import os
import json
from datetime import datetime

def main():
    # Caminhos do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    analise_dir = os.path.join(base_dir, 'output', 'analise')
    rul_path = os.path.join(analise_dir, 'previsao_rul.json')
    
    print("=================================================================")
    print(" FEUP Predictive Maintenance - Gestor de Ordens de Serviço (CMMS)")
    print("=================================================================")
    
    if not os.path.exists(rul_path):
        print(f"[ERRO] Ficheiro de previsão RUL não encontrado: {rul_path}")
        return
        
    with open(rul_path, 'r', encoding='utf-8') as f:
        rul_data_total = json.load(f)
        
    for equip, rul_data in rul_data_total.items():
        ordem_servico_path = os.path.join(analise_dir, f'ordem_servico_urgente_{equip}.txt')
        rul_horas = rul_data.get('rul_horas', 999)
        
        # Limpar qualquer ordem de serviço antiga se o RUL for seguro
        if rul_horas >= 5.0:
            if os.path.exists(ordem_servico_path):
                os.remove(ordem_servico_path)
                print(f"[INFO] [{equip}] RUL seguro. Ordem de Serviço anterior cancelada.")
            else:
                print(f"[INFO] [{equip}] RUL seguro. Nenhuma intervenção requerida.")
            continue
            
        # Gerar a Ordem de Serviço Urgente
        print(f"[ALERTA] [{equip}] RUL Crítico detetado ({rul_horas}h). A gerar Ordem de Serviço...")
        
        data_emissao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ticket_id = f"TICKET-AUT-{equip[:3].upper()}-{datetime.now().strftime('%Y%m%d%H%M')}"
        
        ordem_conteudo = f"""==================================================
ORDEM DE SERVIÇO URGENTE (WORK ORDER)
==================================================
TICKET ID: {ticket_id}
EMISSÃO:   {data_emissao}
NÍVEL:     CRÍTICO
--------------------------------------------------
EQUIPAMENTO: 
{equip}

CAUSA DETETADA:
Risco de Falha Térmica Iminente. 
Tempo de Vida Útil Restante (RUL) estimado em apenas {rul_horas} horas.
Limiar Crítico: {rul_data.get('limite_critico_temperatura', 105)}°C.
Projeção de Falha: {rul_data.get('timestamp_projetado_falha', 'N/A')}.

AÇÃO RECOMENDADA:
1. Proceder à paragem controlada da linha no final do lote atual.
2. Efetuar substituição de rolamentos (possível fadiga mecânica causadora de atrito térmico).
3. Verificação do sistema de ventilação do cárter.
4. Registo de intervenção no CMMS após conclusão.
=================================================="""
    
        os.makedirs(analise_dir, exist_ok=True)
        with open(ordem_servico_path, 'w', encoding='utf-8-sig') as f:
            f.write(ordem_conteudo)
            
        print(f"[SUCESSO] Ordem de Serviço Urgente exportada para:")
        print(f"          -> {ordem_servico_path}")
        
    print("=================================================================")

if __name__ == '__main__':
    main()
