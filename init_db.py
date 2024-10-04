from app import db, app
from models import Grupo, EstiloDemanda, PrevisaoDemanda, PlanoCompras, PlanoProducao, TaxaProducao, Custos

periods = list(range(13, 25))

# Estoques Iniciais
estoques_iniciais_producao = {
    'Baixa': {'Colmeia': 1000, 'Piquet': 1200, 'Maxim': 800},
    'Média': {'Colmeia': 1000, 'Piquet': 1000, 'Maxim': 1000},
    'Alta': {'Colmeia': 3000, 'Piquet': 3200, 'Maxim': 2800}
}

estoques_iniciais_compras = {
    'Baixa': {'Fio Algodao': 500, 'Fio Sintetico': 400, 'Corantes': 300},
    'Média': {'Fio Algodao': 1000, 'Fio Sintetico': 1000, 'Corantes': 100},
    'Alta': {'Fio Algodao': 1500, 'Fio Sintetico': 1200, 'Corantes': 900}
}

taxas_producao = [
    {'familia': 'Colmeia', 'processo': 'Malharia', 'tipo_equipamento': 'Teares', 'taxa': 0.090},
    {'familia': 'Colmeia', 'processo': 'Purga', 'tipo_equipamento': 'Jets', 'taxa': 1.0},
    {'familia': 'Colmeia', 'processo': 'Fixação', 'tipo_equipamento': 'Ramas', 'taxa': 0.002},
    {'familia': 'Colmeia', 'processo': 'Tinturaria', 'tipo_equipamento': 'Jets', 'taxa': 3.000},
    {'familia': 'Colmeia', 'processo': 'Acabamento', 'tipo_equipamento': 'Ramas', 'taxa': 0.003},
    
    {'familia': 'Piquet', 'processo': 'Malharia', 'tipo_equipamento': 'Teares', 'taxa': 0.100},
    {'familia': 'Piquet', 'processo': 'Purga', 'tipo_equipamento': 'Jets', 'taxa': 1.0},
    {'familia': 'Piquet', 'processo': 'Fixação', 'tipo_equipamento': 'Ramas', 'taxa': 0.002},
    {'familia': 'Piquet', 'processo': 'Tinturaria', 'tipo_equipamento': 'Jets', 'taxa': 3.500},
    {'familia': 'Piquet', 'processo': 'Acabamento', 'tipo_equipamento': 'Ramas', 'taxa': 0.003},

    {'familia': 'Maxim', 'processo': 'Malharia', 'tipo_equipamento': 'Teares', 'taxa': 0.110},
    {'familia': 'Maxim', 'processo': 'Purga', 'tipo_equipamento': 'Jets', 'taxa': 1.500},
    {'familia': 'Maxim', 'processo': 'Fixação', 'tipo_equipamento': 'Ramas', 'taxa': 0.003},
    {'familia': 'Maxim', 'processo': 'Tinturaria', 'tipo_equipamento': 'Jets', 'taxa': 4.000},
    {'familia': 'Maxim', 'processo': 'Acabamento', 'tipo_equipamento': 'Ramas', 'taxa': 0.004},
]



def criar_planos_iniciais_para_grupo(grupo):
    # Obter o estilo de demanda do grupo
    estilo = grupo.estilo_demanda.nome_estilo

    # Criar planos de produção iniciais
    #for period in periods:
    for familia, estoque in estoques_iniciais_producao[estilo].items():

        existing_plan = PlanoProducao.query.filter_by(
                        periodo_numero=grupo.periodo_atual+1, familia=familia, grupo_id=grupo.id
                        ).order_by(PlanoProducao.periodo_numero.desc()).first()

        if existing_plan:
            existing_plan.estoques_iniciais = estoque


    db.session.commit()

    # Criar planos de compras iniciais
    for material, estoque in estoques_iniciais_compras[estilo].items():
        plano_compras = PlanoCompras(
            grupo_id=grupo.id,
            periodo_numero=grupo.periodo_atual+1,  # Período atual
            periodo_modificado=grupo.periodo_atual,
            material=material,
            estoques_iniciais=estoque,
            compra_planejada=0  # Inicialmente vazio
        )
        db.session.add(plano_compras)



    # Salvar as mudanças no banco de dados
    db.session.commit()



with app.app_context():
    db.create_all()

    # Estilos Demandas
    demanda_media = EstiloDemanda(nome_estilo='Média',
                                  quantidade_teares = 5,
                                  quantidade_ramas = 1,
                                  quantidade_jets_tipo1 = 0,
                                  quantidade_jets_tipo2 = 3,
                                  quantidade_jets_tipo3 = 0)
    db.session.add(demanda_media)
    db.session.commit()

    # Grupo teste
    estilo_demanda = EstiloDemanda.query.get(demanda_media.id)
    user = Grupo(grupo_nome='Grupo Teste', 
                password='123',
                estilo_demanda_id = demanda_media.id,
                quantidade_teares=estilo_demanda.quantidade_teares,
                quantidade_ramas=estilo_demanda.quantidade_ramas,
                quantidade_jets_tipo1=estilo_demanda.quantidade_jets_tipo1,
                quantidade_jets_tipo2=estilo_demanda.quantidade_jets_tipo2,
                quantidade_jets_tipo3=estilo_demanda.quantidade_jets_tipo3)
    db.session.add(user)
    db.session.commit()





    # Teste estilo demanda Media
    # Preencher as previsões para cada família (Colmeia, Piquet, Maxim) e período para o estilo "Média"
    previsoes_media = [
        {'numero_periodo': 1, 'familia': 'Colmeia', 'valor_previsao': 3637.8},
        {'numero_periodo': 1, 'familia': 'Piquet', 'valor_previsao': 3891.6},
        {'numero_periodo': 1, 'familia': 'Maxim', 'valor_previsao': 1443.8},
        
        {'numero_periodo': 2, 'familia': 'Colmeia', 'valor_previsao': 3767},
        {'numero_periodo': 2, 'familia': 'Piquet', 'valor_previsao': 3926},
        {'numero_periodo': 2, 'familia': 'Maxim', 'valor_previsao': 1899.8},
        
        {'numero_periodo': 3, 'familia': 'Colmeia', 'valor_previsao': 3458.6},
        {'numero_periodo': 3, 'familia': 'Piquet', 'valor_previsao': 3861},
        {'numero_periodo': 3, 'familia': 'Maxim', 'valor_previsao': 2610},
        
        {'numero_periodo': 4, 'familia': 'Colmeia', 'valor_previsao': 3452},
        {'numero_periodo': 4, 'familia': 'Piquet', 'valor_previsao': 3609.8},
        {'numero_periodo': 4, 'familia': 'Maxim', 'valor_previsao': 3201.8},
        
        {'numero_periodo': 5, 'familia': 'Colmeia', 'valor_previsao': 3752},
        {'numero_periodo': 5, 'familia': 'Piquet', 'valor_previsao': 3577},
        {'numero_periodo': 5, 'familia': 'Maxim', 'valor_previsao': 3328.2},
        
        {'numero_periodo': 6, 'familia': 'Colmeia', 'valor_previsao': 3503.2},
        {'numero_periodo': 6, 'familia': 'Piquet', 'valor_previsao': 3654.2},
        {'numero_periodo': 6, 'familia': 'Maxim', 'valor_previsao': 2981.8},
        
        {'numero_periodo': 7, 'familia': 'Colmeia', 'valor_previsao': 3597},
        {'numero_periodo': 7, 'familia': 'Piquet', 'valor_previsao': 3351.8},
        {'numero_periodo': 7, 'familia': 'Maxim', 'valor_previsao': 2843.4},
        
        {'numero_periodo': 8, 'familia': 'Colmeia', 'valor_previsao': 3316},
        {'numero_periodo': 8, 'familia': 'Piquet', 'valor_previsao': 3375.2},
        {'numero_periodo': 8, 'familia': 'Maxim', 'valor_previsao': 3481.6},
        
        {'numero_periodo': 9, 'familia': 'Colmeia', 'valor_previsao': 3692},
        {'numero_periodo': 9, 'familia': 'Piquet', 'valor_previsao': 3197.2},
        {'numero_periodo': 9, 'familia': 'Maxim', 'valor_previsao': 4542},
        
        {'numero_periodo': 10, 'familia': 'Colmeia', 'valor_previsao': 3683},
        {'numero_periodo': 10, 'familia': 'Piquet', 'valor_previsao': 3165.2},
        {'numero_periodo': 10, 'familia': 'Maxim', 'valor_previsao': 5445.6},
        
        {'numero_periodo': 11, 'familia': 'Colmeia', 'valor_previsao': 3339},
        {'numero_periodo': 11, 'familia': 'Piquet', 'valor_previsao': 3022},
        {'numero_periodo': 11, 'familia': 'Maxim', 'valor_previsao': 5248.6},
        
        {'numero_periodo': 12, 'familia': 'Colmeia', 'valor_previsao': 3531},
        {'numero_periodo': 12, 'familia': 'Piquet', 'valor_previsao': 2947.8},
        {'numero_periodo': 12, 'familia': 'Maxim', 'valor_previsao': 4572.6},
        
        {'numero_periodo': 13, 'familia': 'Colmeia', 'valor_previsao': 3637.4},
        {'numero_periodo': 13, 'familia': 'Piquet', 'valor_previsao': 2796.4},
        {'numero_periodo': 13, 'familia': 'Maxim', 'valor_previsao': 4385.8},
        
        {'numero_periodo': 14, 'familia': 'Colmeia', 'valor_previsao': 3584.8},
        {'numero_periodo': 14, 'familia': 'Piquet', 'valor_previsao': 2901.6},
        {'numero_periodo': 14, 'familia': 'Maxim', 'valor_previsao': 5206.8},
        
        {'numero_periodo': 15, 'familia': 'Colmeia', 'valor_previsao': 3731.2},
        {'numero_periodo': 15, 'familia': 'Piquet', 'valor_previsao': 2879.8},
        {'numero_periodo': 15, 'familia': 'Maxim', 'valor_previsao': 6444.6},
        
        {'numero_periodo': 16, 'familia': 'Colmeia', 'valor_previsao': 3561},
        {'numero_periodo': 16, 'familia': 'Piquet', 'valor_previsao': 2735.4},
        {'numero_periodo': 16, 'familia': 'Maxim', 'valor_previsao': 7395.8},
        
        {'numero_periodo': 17, 'familia': 'Colmeia', 'valor_previsao': 3370.8},
        {'numero_periodo': 17, 'familia': 'Piquet', 'valor_previsao': 2531.8},
        {'numero_periodo': 17, 'familia': 'Maxim', 'valor_previsao': 7033.2},
        
        {'numero_periodo': 18, 'familia': 'Colmeia', 'valor_previsao': 3295.2},
        {'numero_periodo': 18, 'familia': 'Piquet', 'valor_previsao': 2520.8},
        {'numero_periodo': 18, 'familia': 'Maxim', 'valor_previsao': 6174.6},
        
        {'numero_periodo': 19, 'familia': 'Colmeia', 'valor_previsao': 3607.6},
        {'numero_periodo': 19, 'familia': 'Piquet', 'valor_previsao': 2411.4},
        {'numero_periodo': 19, 'familia': 'Maxim', 'valor_previsao': 5814.8},
        
        {'numero_periodo': 20, 'familia': 'Colmeia', 'valor_previsao': 3428.6},
        {'numero_periodo': 20, 'familia': 'Piquet', 'valor_previsao': 2400.6},
        {'numero_periodo': 20, 'familia': 'Maxim', 'valor_previsao': 6914.4},

        {'numero_periodo': 21, 'familia': 'Colmeia', 'valor_previsao': 3484.4},
        {'numero_periodo': 21, 'familia': 'Piquet', 'valor_previsao': 2415.8},
        {'numero_periodo': 21, 'familia': 'Maxim', 'valor_previsao': 8699.6},

        {'numero_periodo': 22, 'familia': 'Colmeia', 'valor_previsao': 3639},
        {'numero_periodo': 22, 'familia': 'Piquet', 'valor_previsao': 2331},
        {'numero_periodo': 22, 'familia': 'Maxim', 'valor_previsao': 9626.8},

        {'numero_periodo': 23, 'familia': 'Colmeia', 'valor_previsao': 3505},
        {'numero_periodo': 23, 'familia': 'Piquet', 'valor_previsao': 2141.6},
        {'numero_periodo': 23, 'familia': 'Maxim', 'valor_previsao': 9080},

        {'numero_periodo': 24, 'familia': 'Colmeia', 'valor_previsao': 3481.6},
        {'numero_periodo': 24, 'familia': 'Piquet', 'valor_previsao': 2018.8},
        {'numero_periodo': 24, 'familia': 'Maxim', 'valor_previsao': 7861.8}
        ]

    for previsao in previsoes_media:
        db.session.add(PrevisaoDemanda(
            numero_periodo=previsao['numero_periodo'],
            familia=previsao['familia'],
            valor_previsao=previsao['valor_previsao'],
            estilo_demanda_id=demanda_media.id
        ))
    db.session.commit()


    for previsao in previsoes_media:
        db.session.add(PlanoProducao(
            periodo_numero=previsao['numero_periodo'],
            periodo_modificado=user.periodo_atual,
            familia=previsao['familia'],
            demanda_prevista=previsao['valor_previsao'],
            grupo_id=user.id,
            producao_planejada=0  # Inicialmente vazio
        ))


    for taxa in taxas_producao:
        nova_taxa = TaxaProducao(
            familia=taxa['familia'],
            processo=taxa['processo'],
            tipo_equipamento=taxa['tipo_equipamento'],
            taxa=taxa['taxa']
        )
        db.session.add(nova_taxa)
    db.session.commit()

    custos_iniciais = Custos(
        custo_fixo_tecelagem=5.00,
        custo_fixo_purga_jet1=0.50,
        custo_fixo_purga_jet2=0.25,
        custo_fixo_purga_jet3=0.10,
        custo_fixo_fixacao_acabamento=100.00,
        tma=0.03,
        custo_unitario_compra_emergencia=1,
        taxa_armazenagem=0.05,
        custo_terceirizacao_tecelagem=20.00,
        custo_terceirizacao_purga_tinturaria=2.00,
        custo_terceirizacao_fixacao_acabamento=150.00,
        taxa_desempenho_producao=0.95,
        taxa_desempenho_fornecimento_fios=0.90,
        taxa_desempenho_fornecimento_corantes=0.85,
        preco_aquisicao_teares=10000.00,
        preco_venda_teares=1000.00,
        preco_aquisicao_jet1=90000.00,
        preco_venda_jet1=9000.00,
        preco_aquisicao_jet2=50000.00,
        preco_venda_jet2=5000.00,
        preco_aquisicao_jet3=20000.00,
        preco_venda_jet3=2000.00,
        preco_aquisicao_rama=120000.00,
        preco_venda_rama=12000.00,

        # Preço vendas e Custos relacionado as familias
        preco_venda_colmeia=5.50,
        preco_venda_piquet=6.5,
        preco_venda_maxim=7.5,

        custo_venda_perdida_colmeia=30.00,
        custo_venda_perdida_piquet=40.00,
        custo_venda_perdida_maxim=45.00,

        custo_unitario_colmeia=4.50,
        custo_unitario_piquet=5.00,
        custo_unitario_maxim=5.50,

        # Custos unitários de materiais
        custo_unitario_corantes=20.00,
        custo_unitario_fio_algodao=1.00,
        custo_unitario_fio_sintetico=1.50
    )
    db.session.add(custos_iniciais)
    db.session.commit()

    criar_planos_iniciais_para_grupo(user)
    db.session.commit()
