# Sistema de Manutenção Preditiva & Fleet Management (Indústria 4.0)

Este projeto implementa um sistema **end-to-end** de Manutenção Preditiva e Gestão de Frota focado em antecipar falhas industriais e maximizar a eficiência dos ativos físicos. Desenvolvido com base em Inteligência Artificial e Ciência de Dados, o sistema orquestra desde a recolha de telemetria simulada até à geração automatizada de alertas de manutenção e monetização do tempo de inatividade.

---

## Arquitetura do Sistema

O pipeline opera de forma sequencial, garantindo que os dados passam por uma cadeia de valor estruturada, convertendo dados brutos em inteligência acionável de negócio:

1. **Geração de Dados (Multi-Máquina):** Um script Python injeta anomalias estocásticas de vibração e temperatura ao longo de 24 horas, simulando múltiplos perfis de equipamentos (ex: motores com degradação térmica vs. motores totalmente operacionais).
2. **Machine Learning (Deteção de Anomalias):** Um modelo de `Isolation Forest` treinado *on-the-fly* analisa os limiares multidimensionais (Vibração e Temperatura) para identificar padrões anómalos de telemetria sem necessidade de anotações prévias (Unsupervised Learning).
3. **Previsão de Falhas (Cálculo de RUL):** Um algoritmo de `Regressão Linear` avalia a velocidade de degradação da temperatura ao longo do tempo para calcular o *Remaining Useful Life* (RUL). Ele projeta o momento exato em que a máquina vai ultrapassar o limite crítico de falha funcional (105°C).
4. **Cálculo de KPIs Industriais:** Os dados são sintetizados em indicadores como o MTBF (Tempo Médio Entre Falhas), MTTR (Tempo Médio de Reparação), Disponibilidade global da máquina e Downtime.
5. **Automação CMMS (Ordens de Serviço):** Se o RUL cair abaixo do limiar de segurança estipulado (5.0 horas), o sistema gera automaticamente um ficheiro `.txt` contendo a Ordem de Serviço (Work Order) para a equipa de manutenção local, listando as causas e ações corretivas sugeridas.

---

## Visão de Negócio e Impacto Financeiro

Num cenário de Manutenção 4.0, a mera identificação técnica de anomalias é insuficiente. Este projeto vai além da deteção matemática, incorporando contexto de negócio:

* **Monetização de Downtime:** O sistema correlaciona os minutos exatos em que a máquina permaneceu no estado 'Parado', traduzindo-os imediatamente em prejuízo financeiro com base numa métrica configurável (ex: 500€/hora de inatividade).
* **Gestão de Risco Proativa:** O uso de Semáforos Dinâmicos previne *unplanned downtime*, orientando os gestores de operações (O&M) para reparações cirúrgicas, poupando tempo em diagnósticos morosos.
* **Escalabilidade da Frota:** Ao analisar em formato de lote (*Fleet Management*), permite focar os recursos humanos nos equipamentos em risco, ignorando máquinas estruturalmente saudáveis.

---

## Interface Web (Dashboard)

A visualização de toda a lógica arquitetural dá-se na **Dashboard Streamlit**. Focada numa estética industrial profissional, ela oferece:

* **Menu Lateral Dinâmico:** Reação em tempo real ao selecionar um ativo diferente da frota, com recálculo automático de todos os painéis.
* **Células de KPIs de Gestão:** Componentes que sintetizam métricas como Prejuízo, Disponibilidade, Downtime e MTBF.
* **Alertas CMMS em Tempo Real:** Interface acoplada com o sistema de tickets, mostrando avisos críticos e recomendações de serviço diretamente aos operadores.
* **Análise Visual:** Acesso instantâneo a dois modos visuais: um estático de alta resolução desenhado com `Matplotlib` (com limiares ISO traçados) e um gráfico interativo customizável focado em séries temporais.

---

## Como Executar

### Pré-Requisitos
Certifique-se de ter o Python instalado com os seguintes pacotes essenciais: `pandas`, `scikit-learn`, `matplotlib`, `streamlit`.

### Instruções Passo-a-Passo

**1. Executar o Orquestrador Analítico**  
Abra o seu terminal na raiz do projeto e corra o orquestrador. Este comando irá limpar resíduos de execuções passadas, gerar os dados Multi-Máquina e rodar todo o pipeline de ML e CMMS:
```bash
python run_pipeline.py
```

**2. Lançar a Dashboard Industrial**  
Assim que os ficheiros `.json` e `.txt` tiverem sido injetados na diretoria `/output`, lance a aplicação Streamlit:
```bash
streamlit run app.py
```

O dashboard será imediatamente aberto no seu browser predefinido (tipicamente no porto 8501). Mude as máquinas na barra lateral e veja a inteligência da manutenção preditiva atuar em tempo real!
