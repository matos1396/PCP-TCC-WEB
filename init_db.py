from app import db, app
from models import Grupo, EstiloDemanda, PrevisaoDemanda, PlanoCompras, PlanoProducao

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


def criar_planos_iniciais_para_grupo(grupo):
    # Obter o estilo de demanda do grupo
    estilo = grupo.estilo_demanda.nome_estilo

    # Criar planos de produção iniciais
    for period in periods:
        for familia, estoque in estoques_iniciais_producao[estilo].items():

            existing_plan = PlanoProducao.query.filter_by(
                            periodo_numero=period, familia=familia, grupo_id=grupo.id
                            ).order_by(PlanoProducao.periodo_numero.desc()).first()

            if existing_plan:
                print(familia, estoque)
            #existing_plan.grupo_id=grupo.id,
            #existing_plan.periodo_numero=grupo.periodo_atual,  # Período atual
            #existing_plan.periodo_modificado=grupo.periodo_atual,
            #existing_plan.familia=familia,
                existing_plan.estoques_iniciais = estoque
            #existing_plan.producao_planejada=0  # Inicialmente vazio
                
    db.session.commit()

            # plano_producao = PlanoProducao(
            #     grupo_id=grupo.id,
            #     periodo_numero=grupo.periodo_atual,  # Período atual
            #     periodo_modificado=grupo.periodo_atual,
            #     familia=familia,
            #     estoques_iniciais=estoque,
            #     producao_planejada=0  # Inicialmente vazio
            # )
            # db.session.add(plano_producao)

    # Criar planos de compras iniciais
    for material, estoque in estoques_iniciais_compras[estilo].items():
        plano_compras = PlanoCompras(
            grupo_id=grupo.id,
            periodo_numero=grupo.periodo_atual,  # Período atual
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

    demanda_media = EstiloDemanda(nome_estilo='Média')
    db.session.add(demanda_media)
    db.session.commit()

    # Grupo teste
    user = Grupo(grupo_nome='Grupo Teste', 
                 password='123',
                 estilo_demanda_id = demanda_media.id)
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

    criar_planos_iniciais_para_grupo(user)
    db.session.commit()
