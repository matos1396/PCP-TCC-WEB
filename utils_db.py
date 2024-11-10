from models import db
from models import (Grupo, EstiloDemanda, PrevisaoDemanda, PlanoCompras, PlanoProducao, 
                    TaxaProducao, Custos, CapacidadeJets, CapacidadeRamas, CapacidadeTeares, 
                    RelatorioFinanceiro, CustosFixos, CustosCapital, CustosTerceirizacao, 
                    CustosCompraMP, ReceitasVendas, CustosEstoques, CustosVendasPerdidas, 
                    LeadTimeMaquinas, ControlePlanos)
from dados.dados import demanda_base

# Função para inicializar os estoques de compras
def inicializar_estoques_compras(grupo_id, estilo_demanda):

    estoques_iniciais_compras = {
        'Baixa': {'Fio Algodao': 500, 'Fio Sintetico': 400, 'Corantes': 300},
        'Média': {'Fio Algodao': 1000, 'Fio Sintetico': 1000, 'Corantes': 1000},
        'Alta': {'Fio Algodao': 1500, 'Fio Sintetico': 1200, 'Corantes': 900}
    }

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


def cadastrar_grupo_db(dados_grupo):

    novo_grupo = inicializar_grupo(dados_grupo)

    inicializar_controle_planos(novo_grupo.id)

    # Rever essa previsoes_demanda e planos_producao
    inicializar_previsoes_demanda(novo_grupo.estilo_demanda_id)
    inicializar_planos_producao(novo_grupo.id)

    # Inicializar estoques iniciais de produção e compras
    estilo_demanda = EstiloDemanda.query.get(novo_grupo.estilo_demanda_id)
    inicializar_estoques_iniciais_producao(novo_grupo.id, estilo_demanda.nome_estilo)
    inicializar_estoques_compras(novo_grupo.id, estilo_demanda)
    inicializar_planos_compras(novo_grupo.id, novo_grupo.periodo_atual)

    inicializar_capacidades_maquinas(novo_grupo.id)
    inicializar_tabelas_financeiras(novo_grupo.id)


def inicializar_grupo(dados_grupo):
    dados_grupo
    estilo_id = dados_grupo["Estilo"]
    estilo_demanda = EstiloDemanda.query.get(estilo_id)
    novo_grupo = Grupo(
        grupo_nome = dados_grupo["Nome"], password = dados_grupo["Senha"], estilo_demanda_id = estilo_id,
        quantidade_teares=estilo_demanda.quantidade_teares,
        quantidade_ramas=estilo_demanda.quantidade_ramas,
        quantidade_jets_tipo1=estilo_demanda.quantidade_jets_tipo1,
        quantidade_jets_tipo2=estilo_demanda.quantidade_jets_tipo2,
        quantidade_jets_tipo3=estilo_demanda.quantidade_jets_tipo3)

    db.session.add(novo_grupo)
    db.session.commit()
    return novo_grupo


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

