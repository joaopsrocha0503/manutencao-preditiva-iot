import os
import sys
import subprocess
import glob

def run_script(script_path):
    """Executa um script Python utilizando o mesmo interpretador do pipeline principal."""
    # Obter o caminho absoluto para o script
    abs_path = os.path.abspath(script_path)
    
    if not os.path.exists(abs_path):
        print(f"[PIPELINE][ERRO] Ficheiro não encontrado: {script_path}")
        sys.exit(1)
        
    print(f"\n[PIPELINE] >>> A iniciar execução de: {script_path} ...")
    
    # Executa o subprocesso herdando os canais padrão de input/output para feedback em tempo real
    result = subprocess.run([sys.executable, abs_path])
    
    if result.returncode != 0:
        print(f"[PIPELINE][ERRO] A execução de {script_path} falhou com o código de saída: {result.returncode}")
        sys.exit(result.returncode)
        
    print(f"[PIPELINE] >>> {script_path} concluído com sucesso!")

def main():
    # Garantir que estamos a correr a partir do diretório raiz do projeto
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    print("=================================================================")
    print(" FEUP Industrial Pipeline - Orquestração de Manutenção Preditiva")
    print("=================================================================")
    print(f"[PIPELINE] Diretorório raiz do projeto: {project_root}")
    
    # PRELIMINAR: Limpar ordens de serviço e gráficos antigos
    print("\n[PIPELINE] PASSO PRELIMINAR: A limpar relatórios visuais e ordens de serviço antigas...")
    
    # Apagar txts em output/analise/
    analise_txts = glob.glob(os.path.join(project_root, 'output', 'analise', '*.txt'))
    for txt_file in analise_txts:
        try:
            os.remove(txt_file)
        except Exception as e:
            print(f"[AVISO] Não foi possível apagar {txt_file}: {e}")
            
    # Apagar pngs em output/visualizacao/
    vis_pngs = glob.glob(os.path.join(project_root, 'output', 'visualizacao', '*.png'))
    for png_file in vis_pngs:
        try:
            os.remove(png_file)
        except Exception as e:
            print(f"[AVISO] Não foi possível apagar {png_file}: {e}")
            
    print(f"[PIPELINE] PASSO PRELIMINAR: Limpeza de {len(analise_txts)} tickets e {len(vis_pngs)} gráficos concluída.")
    
    # 0. Executar o Script de Geração de Dados (Multi-Máquina)
    print("\n[PIPELINE] PASSO 0: A gerar telemetria simulada da Frota (Multi-Máquina)...")
    run_script(os.path.join('scripts', 'gerador_multi_maquina.py'))
    print("[PIPELINE] PASSO 0: Dados da frota gerados e gravados.")
    
    # 1. Executar o Script de Análise Preditiva (Treino e classificação Isolation Forest)
    print("\n[PIPELINE] PASSO 1: A iniciar motor de análise preditiva (Machine Learning)...")
    run_script(os.path.join('scripts', 'analise_preditiva.py'))
    print("[PIPELINE] PASSO 1: Análise concluída e deteções gravadas.")
    
    # 2. Executar o Script de Cálculo de RUL (Regressão Linear)
    print("\n[PIPELINE] PASSO 2: A iniciar cálculo de Remaining Useful Life (RUL)...")
    run_script(os.path.join('scripts', 'calcular_rul.py'))
    print("[PIPELINE] PASSO 2: Previsão de RUL concluída e gravada.")
    
    # 3. Executar o Script de Visualização Gráfica (Matplotlib e Limiares ISO)
    print("\n[PIPELINE] PASSO 3: A iniciar geração de relatórios visuais (Matplotlib)...")
    run_script(os.path.join('scripts', 'gerar_visualizacao.py'))
    print("[PIPELINE] PASSO 3: Geração de relatórios visuais concluída.")
    
    # 4. Executar o Script de Cálculo de KPIs Industriais (Gestão)
    print("\n[PIPELINE] PASSO 4: A iniciar motor de cálculo de KPIs Industriais (Gestão)...")
    run_script(os.path.join('scripts', 'calcular_metricas.py'))
    print("[PIPELINE] PASSO 4: KPIs e métricas de gestão calculadas.")
    
    # 5. Executar o Script de Geração de Ordens de Serviço (CMMS)
    print("\n[PIPELINE] PASSO 5: A iniciar motor de integração de Ordens de Serviço (CMMS)...")
    run_script(os.path.join('scripts', 'gerar_ordem_servico.py'))
    print("[PIPELINE] PASSO 5: Verificação de Work Orders concluída.")
    
    print("\n=================================================================")
    print(" [SUCESSO] Pipeline de Manutenção Preditiva finalizado (Fleet Management)!")
    print(" -> Relatório de Deteções JSON: output/analise/detecoes.json (aninhado por máquina)")
    print(" -> Projeção de RUL JSON: output/analise/previsao_rul.json (aninhado por máquina)")
    print(" -> KPIs de Gestão Industrial JSON: output/analise/metricas_gestao.json (aninhado por máquina)")
    print(" -> Ordens de Serviço Pendentes TXT: output/analise/ordem_servico_urgente_<máquina>.txt")
    print(" -> Gráficos exportados: output/visualizacao/grafico_sensores_<máquina>.png")
    print("=================================================================")

if __name__ == '__main__':
    main()
