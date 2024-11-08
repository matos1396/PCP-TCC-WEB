from app import db, app
from models import (Grupo, EstiloDemanda, PrevisaoDemanda, PlanoCompras, PlanoProducao, 
                    TaxaProducao, Custos, CapacidadeJets, CapacidadeRamas, CapacidadeTeares, 
                    RelatorioFinanceiro, CustosFixos, CustosCapital, CustosTerceirizacao, 
                    CustosCompraMP, ReceitasVendas, CustosEstoques, CustosVendasPerdidas, 
                    LeadTimeMaquinas, ControlePlanos)
from dados.dados import demanda_base

# Funções auxiliares

# Estoques iniciais para produção e compras
estoques_iniciais_producao = {
    'Baixa': {'Colmeia': 1000, 'Piquet': 1200, 'Maxim': 800},
    'Média': {'Colmeia': 1000, 'Piquet': 1000, 'Maxim': 1000},
    'Alta': {'Colmeia': 3000, 'Piquet': 3200, 'Maxim': 2800}
}

estoques_iniciais_compras = {
    'Baixa': {'Fio Algodao': 500, 'Fio Sintetico': 400, 'Corantes': 300},
    'Média': {'Fio Algodao': 1000, 'Fio Sintetico': 1000, 'Corantes': 1000},
    'Alta': {'Fio Algodao': 1500, 'Fio Sintetico': 1200, 'Corantes': 900}
}

# # Função para inicializar os estoques de produção
# def inicializar_estoques_producao(grupo_id, estilo_demanda):
#     planos_producao = []
#     for familia, estoque in estoques_iniciais_producao[estilo_demanda.nome_estilo].items():
#         plano = PlanoProducao(
#             periodo_numero=13,
#             periodo_modificado=12,
#             familia=familia,
#             estoques_iniciais=estoque,
#             grupo_id=grupo_id,
#             producao_planejada=0
#         )
#         planos_producao.append(plano)
#     adicionar_objetos_no_db(planos_producao)

# Função para inicializar os estoques de compras
def inicializar_estoques_compras(grupo_id, estilo_demanda):
    planos_compras = []
    for material, estoque in estoques_iniciais_compras[estilo_demanda.nome_estilo].items():
        plano = PlanoCompras(
            grupo_id=grupo_id,
            periodo_numero=13,
            periodo_modificado=12,
            material=material,
            estoques_iniciais=estoque,
            compra_planejada=0
        )
        planos_compras.append(plano)
    adicionar_objetos_no_db(planos_compras)


def obter_ids_lead_time():
    lead_time_teares = LeadTimeMaquinas.query.filter_by(tipo_maquina='Teares').first().id
    lead_time_jets = LeadTimeMaquinas.query.filter_by(tipo_maquina='Jets').first().id
    lead_time_ramas = LeadTimeMaquinas.query.filter_by(tipo_maquina='Ramas').first().id
    return lead_time_teares, lead_time_jets, lead_time_ramas

def adicionar_objetos_no_db(objetos):
    for objeto in objetos:
        # Tenta inserir ou atualizar o objeto no banco de dados
        db.session.merge(objeto)
    db.session.commit()

def criar_usuario_admin():
    # TEMP
    estilo_demanda = EstiloDemanda.query.get(1)

    admin = Grupo(
        grupo_nome='Admin', password='123', estilo_demanda_id=1,
        quantidade_teares=estilo_demanda.quantidade_teares,
        quantidade_ramas=estilo_demanda.quantidade_ramas,
        quantidade_jets_tipo1=estilo_demanda.quantidade_jets_tipo1,
        quantidade_jets_tipo2=estilo_demanda.quantidade_jets_tipo2,
        quantidade_jets_tipo3=estilo_demanda.quantidade_jets_tipo3,
        is_admin = True)

    db.session.add(admin)
    db.session.commit()

def criar_grupo_teste():

    estilo_demanda = EstiloDemanda.query.get(1)
    grupo_teste = Grupo(
        grupo_nome='Grupo Teste', password='123', estilo_demanda_id=1,
        quantidade_teares=estilo_demanda.quantidade_teares,
        quantidade_ramas=estilo_demanda.quantidade_ramas,
        quantidade_jets_tipo1=estilo_demanda.quantidade_jets_tipo1,
        quantidade_jets_tipo2=estilo_demanda.quantidade_jets_tipo2,
        quantidade_jets_tipo3=estilo_demanda.quantidade_jets_tipo3)
    db.session.add(grupo_teste)
    db.session.commit()
    return grupo_teste

def inicializar_previsoes_demanda(estilo_demanda_id):

    objetos_previsao = [
        PrevisaoDemanda(numero_periodo=p['numero_periodo'], familia=p['familia'], 
                        valor_previsao=p['valor_previsao'], estilo_demanda_id=estilo_demanda_id) 
        for p in demanda_base
    ]
    adicionar_objetos_no_db(objetos_previsao)

def inicializar_planos_producao(grupo_id):

    objetos_plano_producao = [
        PlanoProducao(
            periodo_numero=p['numero_periodo'], periodo_modificado=12, 
            familia=p['familia'], demanda_prevista=p['valor_previsao'], 
            grupo_id=grupo_id, producao_planejada=0
        ) for p in demanda_base
    ]
    adicionar_objetos_no_db(objetos_plano_producao)

def inicializar_capacidades_maquinas(grupo_id):
    periods = range(13, 25)
    lead_time_teares, lead_time_jets, lead_time_ramas = obter_ids_lead_time()

    capacidades = []
    for period in periods:
        capacidades.append(CapacidadeTeares(
            grupo_id=grupo_id, lead_time_id=lead_time_teares, periodo_numero=period, 
            periodo_modificado=12, quantidade=5, numero_turnos=2, capacidade_necessaria=0, 
            capacidade_terceirizada=0, produtividade=0.1, colmeia=0, piquet=0, maxim=0))
        capacidades.append(CapacidadeRamas(
            grupo_id=grupo_id, lead_time_id=lead_time_ramas, periodo_numero=period, 
            periodo_modificado=12, quantidade=1, numero_turnos=2, capacidade_necessaria=0, 
            capacidade_terceirizada=0, produtividade=0.1, colmeia=0, piquet=0, maxim=0))
        capacidades.append(CapacidadeJets(
            grupo_id=grupo_id, lead_time_id=lead_time_jets, periodo_numero=period, 
            periodo_modificado=12, quantidade_tipo1=0, quantidade_tipo2=3, quantidade_tipo3=0, 
            capacidade_tipo1=480, capacidade_tipo2=120, capacidade_tipo3=80, numero_turnos=2, 
            capacidade_necessaria=0, capacidade_terceirizada=0, produtividade=0.1, colmeia=0, piquet=0, maxim=0))
    adicionar_objetos_no_db(capacidades)

def inicializar_custos():
    custos = Custos(
        custo_fixo_tecelagem=5.00, custo_fixo_purga_jet1=0.50, custo_fixo_purga_jet2=0.25, 
        custo_fixo_purga_jet3=0.10, custo_fixo_fixacao_acabamento=100.00, tma=0.03, 
        custo_unitario_compra_emergencia=2, taxa_armazenagem=0.05, 
        custo_terceirizacao_tecelagem=20.00, custo_terceirizacao_purga_tinturaria=2.00, 
        custo_terceirizacao_fixacao_acabamento=150.00, taxa_desempenho_producao=0.95, 
        taxa_desempenho_fornecimento_fios=0.90, taxa_desempenho_fornecimento_corantes=0.85, 
        preco_aquisicao_teares=10000.00, preco_venda_teares=1000.00, 
        preco_aquisicao_jet1=90000.00, preco_venda_jet1=9000.00, 
        preco_aquisicao_jet2=50000.00, preco_venda_jet2=5000.00, 
        preco_aquisicao_jet3=20000.00, preco_venda_jet3=2000.00, 
        preco_aquisicao_rama=120000.00, preco_venda_rama=12000.00, 
        preco_venda_colmeia=5.50, preco_venda_piquet=6.5, preco_venda_maxim=7.5, 
        custo_venda_perdida_colmeia=30.00, custo_venda_perdida_piquet=40.00, 
        custo_venda_perdida_maxim=45.00, custo_unitario_colmeia=4.50, 
        custo_unitario_piquet=5.00, custo_unitario_maxim=5.50, custo_unitario_corantes=20.00, 
        custo_unitario_fio_algodao=1.00, custo_unitario_fio_sintetico=1.50)
    db.session.add(custos)
    db.session.commit()

def inicializar_lead_time_maquinas():
    lead_times = [
        LeadTimeMaquinas(tipo_maquina='Teares', lead_time_ampliacao=2, lead_time_reducao=2),
        LeadTimeMaquinas(tipo_maquina='Jets', lead_time_ampliacao=3, lead_time_reducao=2),
        LeadTimeMaquinas(tipo_maquina='Ramas', lead_time_ampliacao=3, lead_time_reducao=3)
    ]
    adicionar_objetos_no_db(lead_times)

# Função principal de inicialização
def inicializar_banco_de_dados():
    with app.app_context():
        db.create_all()

        inicializar_demandas()

        criar_usuario_admin()
        grupo_teste = criar_grupo_teste()

        inicializar_taxas_producao()
        inicializar_lead_time_maquinas()
        inicializar_custos()

        inicializar_controle_planos(grupo_teste.id)

        # Rever essa previsoes_demanda e planos_producao
        inicializar_previsoes_demanda(grupo_teste.estilo_demanda_id)
        inicializar_planos_producao(grupo_teste.id)

        # Inicializar estoques iniciais de produção e compras
        estilo_demanda = EstiloDemanda.query.get(grupo_teste.estilo_demanda_id)
        inicializar_estoques_iniciais_producao(grupo_teste.id, 'Média')
        #inicializar_estoques_producao(grupo_teste.id, estilo_demanda)
        inicializar_estoques_compras(grupo_teste.id, estilo_demanda)
        inicializar_planos_compras(grupo_teste.id, grupo_teste.periodo_atual)

        inicializar_capacidades_maquinas(grupo_teste.id)
        inicializar_tabelas_financeiras(grupo_teste.id)

        print("Banco de dados inicializado com sucesso.")


def inicializar_estoques_iniciais_producao(grupo_id, estilo):

    estoques_iniciais_producao = {
    'Baixa': {'Colmeia': 1000, 'Piquet': 1200, 'Maxim': 800},
    'Média': {'Colmeia': 1000, 'Piquet': 1000, 'Maxim': 1000},
    'Alta': {'Colmeia': 3000, 'Piquet': 3200, 'Maxim': 2800}
    }

    estoques_iniciais = estoques_iniciais_producao[estilo]

    for familia, estoque in estoques_iniciais.items():
        filtros = {'grupo_id': grupo_id, 'familia': familia, 'periodo_numero': 13}
        novos_valores = {'estoques_iniciais': estoque}
        atualizar_ou_adicionar_tabela(PlanoProducao, filtros, novos_valores)



def atualizar_ou_adicionar_tabela(modelo, filtros, novos_valores):
    # Verifica se já existe um registro que corresponda aos filtros fornecidos
    registro_existente = modelo.query.filter_by(**filtros).first()
    if registro_existente:
        # Atualiza os valores do registro existente
        for chave, valor in novos_valores.items():
            setattr(registro_existente, chave, valor)
    else:
        # Se não existir, cria um novo registro
        novo_registro = modelo(**filtros, **novos_valores)
        db.session.add(novo_registro)
    db.session.commit()

def inicializar_tabelas_financeiras(grupo_id):
    periods = range(13, 25)

    for period in periods:
        # Relatório Financeiro
        filtros = {'grupo_id': grupo_id, 'periodo': period}
        novos_valores = {
            'custos_fixos': 0.0,
            'custos_compra_mp': 0.0,
            'custos_estoques': 0.0,
            'custos_terceirizacao': 0.0,
            'custos_capital': 0.0,
            'custos_vendas_perdidas': 0.0,
            'custos_totais': 0.0,
            'receitas_vendas': 0.0,
            'resultado_operacional': 0.0,
            'ro_acumulado': 0.0
        }
        atualizar_ou_adicionar_tabela(RelatorioFinanceiro, filtros, novos_valores)

        # Custos Fixos
        novos_valores = {
            'c_fixo_tecelagem': 0.0,
            'c_fixo_purga_tinturaria': 0.0,
            'c_fixo_fixacao_acabamento': 0.0,
            'c_fixo_depreciacao_tecelagem': 0.0,
            'c_fixo_depreciacao_purga_tinturaria': 0.0,
            'c_fixo_depreciacao_fixacao_acabamento': 0.0,
            'c_fixo_total': 0.0
        }
        atualizar_ou_adicionar_tabela(CustosFixos, filtros, novos_valores)

        # Custos de Compra MP
        novos_valores = {
            'c_compras_corantes': 0.0,
            'c_compras_fio_algodao': 0.0,
            'c_compras_fio_sintetico': 0.0,
            'c_emergencia_corante': 0.0,
            'c_emergencia_fio_algodao': 0.0,
            'c_emergencia_fio_sintetico': 0.0,
            'c_compras_total': 0.0
        }
        atualizar_ou_adicionar_tabela(CustosCompraMP, filtros, novos_valores)

        # Custos de Estoque
        novos_valores = {
            'c_estoque_corantes': 0.0,
            'c_estoque_fio_algodao': 0.0,
            'c_estoque_fio_sintetico': 0.0,
            'c_estoque_colmeia': 0.0,
            'c_estoque_piquet': 0.0,
            'c_estoque_maxim': 0.0,
            'c_estoque_total': 0.0
        }
        atualizar_ou_adicionar_tabela(CustosEstoques, filtros, novos_valores)

        # Custos de Terceirização
        novos_valores = {
            'c_terc_tecelagem': 0.0,
            'c_terc_purga_tinturaria': 0.0,
            'c_terc_fixacao_acabamento': 0.0,
            'c_terc_total': 0.0
        }
        atualizar_ou_adicionar_tabela(CustosTerceirizacao, filtros, novos_valores)

        # Custos de Capital
        novos_valores = {
            'custo_capital_teares': 0.0,
            'custo_capital_jets': 0.0,
            'custo_capital_ramas': 0.0,
            'custo_capital_mp': 0.0,
            'custo_capital_pa': 0.0,
            'custo_capital_total': 0.0
        }
        atualizar_ou_adicionar_tabela(CustosCapital, filtros, novos_valores)

        # Custos de Vendas Perdidas
        novos_valores = {
            'c_vp_comeia': 0.0,
            'c_vp_piquet': 0.0,
            'c_vp_maxim': 0.0,
            'c_vp_total': 0.0
        }
        atualizar_ou_adicionar_tabela(CustosVendasPerdidas, filtros, novos_valores)

        # Receitas de Vendas
        novos_valores = {
            'r_vendas_colmeia': 0.0,
            'r_vendas_piquet': 0.0,
            'r_vendas_maxim': 0.0,
            'r_vendas_equip': 0.0,
            'r_vendas_total': 0.0
        }
        atualizar_ou_adicionar_tabela(ReceitasVendas, filtros, novos_valores)


def inicializar_taxas_producao():
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

    for taxa in taxas_producao:
        filtros = {
            'familia': taxa['familia'],
            'processo': taxa['processo'],
            'tipo_equipamento': taxa['tipo_equipamento']
        }
        novos_valores = {'taxa': taxa['taxa']}

        atualizar_ou_adicionar_tabela(TaxaProducao, filtros, novos_valores)


def inicializar_controle_planos(grupo_id):
    # Define os períodos de 13 a 24
    periods = range(13, 25)

    for periodo in periods:
        # Verificar se já existe um registro para esse grupo e período
        controle_existente = ControlePlanos.query.filter_by(grupo_id=grupo_id, periodo=periodo).first()

        if not controle_existente:
            # Criar um novo registro de controle de planos
            novo_controle = ControlePlanos(
                grupo_id=grupo_id,
                periodo=periodo,
                plano_producao_salvo=False,
                plano_compras_salvo=False
            )
            db.session.add(novo_controle)
    
    # Commit após adicionar todos os registros
    db.session.commit()

def inicializar_planos_compras(grupo_id, periodo_atual):
    periods = range(13, 25)  # Períodos de 13 a 24
    materiais = ["Corantes", "Fio Algodao", "Fio Sintetico"]

    for period in periods:
        for material in materiais:
            # Verificar se já existe um registro de compra para o período, material e grupo especificados
            existing_plan = PlanoCompras.query.filter_by(
                periodo_numero=period,
                periodo_modificado=periodo_atual,
                material=material,
                grupo_id=grupo_id
            ).first()

            if existing_plan:
                # Atualizar o plano de compra existente
                existing_plan.compra_planejada = 0
            else:
                # Criar um novo plano de compra se não existir
                novo_plano_compras = PlanoCompras(
                    grupo_id=grupo_id,
                    periodo_numero=period,
                    periodo_modificado=periodo_atual,
                    material=material,
                    compra_planejada=0
                )
                db.session.add(novo_plano_compras)

    # Commit após adicionar ou atualizar todos os registros
    db.session.commit()

def inicializar_demandas():
    #TODO: Adicionar para os outros estilos de demanda
    demanda_media = EstiloDemanda(
        nome_estilo='Média', quantidade_teares=5, quantidade_ramas=1, 
        quantidade_jets_tipo1=0, quantidade_jets_tipo2=3, quantidade_jets_tipo3=0)

    db.session.add(demanda_media)
    db.session.commit()



# Chamada da função principal
if __name__ == '__main__':
    inicializar_banco_de_dados()
