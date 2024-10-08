from models import (PlanoCompras,
                    PlanoProducao, TaxaProducao,
                    Custos, CapacidadeJets,
                    CapacidadeRamas, CapacidadeTeares,
                    RelatorioFinanceiro, CustosFixos,
                    CustosCapital, CustosTerceirizacao,
                    CustosCompraMP, ReceitasVendas,
                    CustosEstoques, CustosVendasPerdidas)
from app import db
import time

def atualizar_plano_compras(grupo):
    periods = list(range(13, 25))
    periodo_atual = grupo.periodo_atual

    # Pré-carregar todos os registros de PlanoCompras para o grupo e períodos de interesse
    planos_compra = PlanoCompras.query.filter_by(grupo_id=grupo.id, periodo_modificado=periodo_atual).filter(
        PlanoCompras.periodo_numero.in_(periods)
    ).all()

    # Organizar os registros por período e material para acesso rápido
    planos_compra_dict = {(pc.periodo_numero, pc.material): pc for pc in planos_compra}

    novos_planos = []  # Lista para armazenar novos registros

    for material in ['Fio Algodao', 'Fio Sintetico', 'Corantes']:
        for period in periods:
            # Verificar se existe um plano de compras para o período e material atual
            plano_compra = planos_compra_dict.get((period, material))

            # Calcular o consumo previsto
            consumo_previsto = calcular_consumo_previsto(grupo, material, period, periodo_atual)

            if plano_compra:
                # Atualizar o registro existente
                plano_compra.consumo_previsto = consumo_previsto
            else:
                # Criar novo plano de compras para o período e material
                novo_plano = PlanoCompras(
                    grupo_id=grupo.id,
                    periodo_numero=period,
                    periodo_modificado=periodo_atual,
                    material=material,
                    consumo_previsto=consumo_previsto
                )
                novos_planos.append(novo_plano)

    # Adicionar todos os novos registros de uma vez
    db.session.add_all(novos_planos)
    db.session.commit()


def atualizar_capacidade_maquinas(grupo):
    periods = list(range(13, 25))
    periodo_atual = grupo.periodo_atual

    # Pré-carregar registros de PlanoProducao para o grupo e períodos
    planos_producao = PlanoProducao.query.filter(
        PlanoProducao.grupo_id == grupo.id,
        PlanoProducao.periodo_numero.in_(periods)
    ).order_by(PlanoProducao.periodo_modificado.desc()).all()
    planos_producao_dict = {(pp.periodo_numero, pp.familia): pp for pp in planos_producao}

    # Pré-carregar registros de CapacidadeTeares, CapacidadeRamas, e CapacidadeJets
    capacidades_teares = CapacidadeTeares.query.filter(
        CapacidadeTeares.grupo_id == grupo.id,
        CapacidadeTeares.periodo_numero.in_(periods),
        CapacidadeTeares.periodo_modificado == periodo_atual
    ).all()
    capacidades_teares_dict = {ct.periodo_numero: ct for ct in capacidades_teares}

    capacidades_ramas = CapacidadeRamas.query.filter(
        CapacidadeRamas.grupo_id == grupo.id,
        CapacidadeRamas.periodo_numero.in_(periods),
        CapacidadeRamas.periodo_modificado == periodo_atual
    ).all()
    capacidades_ramas_dict = {cr.periodo_numero: cr for cr in capacidades_ramas}

    capacidades_jets = CapacidadeJets.query.filter(
        CapacidadeJets.grupo_id == grupo.id,
        CapacidadeJets.periodo_numero.in_(periods),
        CapacidadeJets.periodo_modificado == periodo_atual
    ).all()
    capacidades_jets_dict = {cj.periodo_numero: cj for cj in capacidades_jets}

    # Pré-carregar taxas de produção
    taxas_producao = TaxaProducao.query.filter(
        TaxaProducao.tipo_equipamento.in_(["Teares", "Ramas"]),
        TaxaProducao.processo.in_(["Malharia", "Fixação", "Acabamento"])
    ).all()
    taxas_dict = {(tp.tipo_equipamento, tp.processo, tp.familia): tp.taxa for tp in taxas_producao}

    for familia in ['Colmeia', 'Piquet', 'Maxim']:
        for period in periods:
            plano_producao = planos_producao_dict.get((period, familia))
            capacidade_teares = capacidades_teares_dict.get(period)
            capacidade_ramas = capacidades_ramas_dict.get(period)
            capacidade_jets = capacidades_jets_dict.get(period)

            # Obter as taxas de produção
            taxa_tear = taxas_dict.get(("Teares", "Malharia", familia), 0)
            taxa_rama_1 = taxas_dict.get(("Ramas", "Fixação", familia), 0)
            taxa_rama_2 = taxas_dict.get(("Ramas", "Acabamento", familia), 0)

            if plano_producao:
                producao_planejada = plano_producao.producao_planejada

                # Calcular e atribuir os valores para cada família e máquina
                t_tear = producao_planejada * taxa_tear
                t_rama = producao_planejada * (taxa_rama_1 + taxa_rama_2)
                t_jet = producao_planejada

                if capacidade_teares:
                    setattr(capacidade_teares, familia.lower(), t_tear)
                if capacidade_ramas:
                    setattr(capacidade_ramas, familia.lower(), t_rama)
                if capacidade_jets:
                    setattr(capacidade_jets, familia.lower(), t_jet)

    # Ajustar Capacidade Necessária fora do loop para reduzir consultas
    for period in periods:
        capacidade_teares = capacidades_teares_dict.get(period)
        capacidade_ramas = capacidades_ramas_dict.get(period)
        capacidade_jets = capacidades_jets_dict.get(period)

        if capacidade_teares:
            soma_teares = capacidade_teares.colmeia + capacidade_teares.piquet + capacidade_teares.maxim
            capacidade_teares.capacidade_necessaria = soma_teares + capacidade_teares.produtividade + capacidade_teares.setup
        if capacidade_ramas:
            soma_ramas = capacidade_ramas.colmeia + capacidade_ramas.piquet + capacidade_ramas.maxim
            capacidade_ramas.capacidade_necessaria = soma_ramas + capacidade_ramas.produtividade + capacidade_ramas.setup
        if capacidade_jets:
            soma_jets = capacidade_jets.colmeia + capacidade_jets.piquet + capacidade_jets.maxim
            capacidade_jets.capacidade_necessaria = soma_jets + capacidade_jets.produtividade + capacidade_jets.setup

    # Salvar as alterações de uma vez
    db.session.commit()



def atualizar_financeiro(grupo):
    periodo_atual = grupo.periodo_atual
    custos = Custos.query.first()

    # Pré-carregar todos os registros de capacidades para os períodos de 13 a 25 em uma única consulta
    capacidade_teares = CapacidadeTeares.query.filter_by(grupo_id=grupo.id).filter(
        CapacidadeTeares.periodo_numero.in_(range(13, 25))
    ).all()

    capacidade_ramas = CapacidadeRamas.query.filter_by(grupo_id=grupo.id).filter(
        CapacidadeRamas.periodo_numero.in_(range(13, 25))
    ).all()

    capacidade_jets = CapacidadeJets.query.filter_by(grupo_id=grupo.id).filter(
        CapacidadeJets.periodo_numero.in_(range(13, 25))
    ).all()

    # Pré-carregar todos os registros de CustosFixos para os períodos de 13 a 25 em uma única consulta
    custos_fixos_registros = CustosFixos.query.filter_by(grupo_id=grupo.id).filter(
        CustosFixos.periodo.in_(range(13, 25))
    ).all()

    # Organizar os dados em dicionários por período para acesso rápido
    capacidade_teares_dict = {ct.periodo_numero: ct for ct in capacidade_teares}
    capacidade_ramas_dict = {cr.periodo_numero: cr for cr in capacidade_ramas}
    capacidade_jets_dict = {cj.periodo_numero: cj for cj in capacidade_jets}
    custos_fixos_dict = {cf.periodo: cf for cf in custos_fixos_registros}

    novos_custos_fixos = []  # Lista para armazenar novos registros

    for period in range(13, 25):
        # Obter as capacidades de cada máquina para o período atual, se existir
        capacidade_teares = capacidade_teares_dict.get(period)
        capacidade_ramas = capacidade_ramas_dict.get(period)
        capacidade_jets = capacidade_jets_dict.get(period)

        # Realizar cálculos para Custos Fixos
        c_fixo_tecelagem = (capacidade_teares.capacidade_instalada * custos.custo_fixo_tecelagem) if capacidade_teares else 0
        c_fixo_fixacao_acabamento = (capacidade_ramas.capacidade_instalada * custos.custo_fixo_fixacao_acabamento) if capacidade_ramas else 0
        c_fixo_purga_tinturaria = (
            (capacidade_jets.capacidade_instalada_tipo1 * custos.custo_fixo_purga_jet1) +
            (capacidade_jets.capacidade_instalada_tipo2 * custos.custo_fixo_purga_jet2) +
            (capacidade_jets.capacidade_instalada_tipo3 * custos.custo_fixo_purga_jet3)
        ) if capacidade_jets else 0

        # Depreciação
        c_fixo_depreciacao_tecelagem = capacidade_teares.quantidade * custos.preco_aquisicao_teares / (5 * 12) if capacidade_teares else 0
        c_fixo_depreciacao_fixacao_acabamento = capacidade_ramas.quantidade * custos.preco_aquisicao_rama / (5 * 12) if capacidade_ramas else 0
        c_fixo_depreciacao_purga_tinturaria = (
            (capacidade_jets.quantidade_tipo1 * custos.preco_aquisicao_jet1) / (5 * 12) +
            (capacidade_jets.quantidade_tipo2 * custos.preco_aquisicao_jet2) / (5 * 12) +
            (capacidade_jets.quantidade_tipo3 * custos.preco_aquisicao_jet3) / (5 * 12)
        ) if capacidade_jets else 0

        # Total de custos fixos
        c_fixo_total = (
            c_fixo_tecelagem + c_fixo_purga_tinturaria + c_fixo_fixacao_acabamento +
            c_fixo_depreciacao_tecelagem + c_fixo_depreciacao_purga_tinturaria + c_fixo_depreciacao_fixacao_acabamento
        )

        # Atualizar ou criar registro em CustosFixos
        custos_fixos = custos_fixos_dict.get(period)
        if custos_fixos:
            # Atualizar valores existentes
            custos_fixos.c_fixo_tecelagem = c_fixo_tecelagem
            custos_fixos.c_fixo_purga_tinturaria = c_fixo_purga_tinturaria
            custos_fixos.c_fixo_fixacao_acabamento = c_fixo_fixacao_acabamento
            custos_fixos.c_fixo_depreciacao_tecelagem = c_fixo_depreciacao_tecelagem
            custos_fixos.c_fixo_depreciacao_purga_tinturaria = c_fixo_depreciacao_purga_tinturaria
            custos_fixos.c_fixo_depreciacao_fixacao_acabamento = c_fixo_depreciacao_fixacao_acabamento
            custos_fixos.c_fixo_total = c_fixo_total
        else:
            # Criar novo registro
            novos_custos_fixos.append(CustosFixos(
                grupo_id=grupo.id,
                periodo=period,
                c_fixo_tecelagem=c_fixo_tecelagem,
                c_fixo_purga_tinturaria=c_fixo_purga_tinturaria,
                c_fixo_fixacao_acabamento=c_fixo_fixacao_acabamento,
                c_fixo_depreciacao_tecelagem=c_fixo_depreciacao_tecelagem,
                c_fixo_depreciacao_purga_tinturaria=c_fixo_depreciacao_purga_tinturaria,
                c_fixo_depreciacao_fixacao_acabamento=c_fixo_depreciacao_fixacao_acabamento,
                c_fixo_total=c_fixo_total
            ))

    # Adicionar novos registros de CustosFixos ao banco de dados
    db.session.add_all(novos_custos_fixos)
    db.session.commit()




def calcular_consumo_previsto(grupo, material, periodo, periodo_atual):
    # #### Dicionario apenas para consulta manualmente
    dici_estrutura = {"Colmeia": {"Fio Algodao": 1,
                                  "Fio Sintetico": 0,
                                  "Corante": 0.02
                                  },
                      "Piquet":  {"Fio Algodao": 0.5,
                                  "Fio Sintetico": 0.5,
                                  "Corante": 0.02
                                  },
                      "Maxim":   {"Fio Algodao": 0,
                                  "Fio Sintetico": 1,
                                  "Corante": 0.02
                                  }}
    # ####
    if material == "Fio Algodao":
        consumo_previsto_fio_algodao = 0
        for familia in ["Colmeia", "Piquet"]:
            plano_producao = PlanoProducao.query.filter_by(grupo_id = grupo.id,
                                                        periodo_numero = periodo,
                                                        periodo_modificado = periodo_atual,
                                                        familia=familia).order_by(
                                                            PlanoProducao.periodo_numero.asc()).first()
            if familia == "Colmeia":
                consumo_previsto_fio_algodao += float(plano_producao.producao_planejada)
            if familia == "Piquet":
                consumo_previsto_fio_algodao += float(plano_producao.producao_planejada) * 0.5
        return consumo_previsto_fio_algodao

    if material == "Fio Sintetico":
        consumo_previsto_fio_sintetico = 0
        for familia in ["Piquet", "Maxim"]:
            plano_producao = PlanoProducao.query.filter_by(grupo_id = grupo.id,
                                                        periodo_numero = periodo,
                                                        periodo_modificado = periodo_atual,
                                                        familia=familia).order_by(
                                                            PlanoProducao.periodo_numero.asc()).first()
            if familia == "Maxim":
                consumo_previsto_fio_sintetico += float(plano_producao.producao_planejada)
            if familia == "Piquet":
                consumo_previsto_fio_sintetico += float(plano_producao.producao_planejada) * 0.5
        return consumo_previsto_fio_sintetico

    if material == "Corantes":
        consumo_previsto_corantes = 0
        for familia in ["Colmeia", "Piquet", "Maxim"]:
            plano_producao = PlanoProducao.query.filter_by(grupo_id = grupo.id,
                                                        periodo_numero = periodo,
                                                        periodo_modificado = periodo_atual,
                                                        familia=familia).order_by(
                                                            PlanoProducao.periodo_numero.asc()).first()
            if familia == "Colmeia":
                consumo_previsto_corantes += float(plano_producao.producao_planejada) * 0.02
            if familia == "Piquet":
                consumo_previsto_corantes += float(plano_producao.producao_planejada) * 0.02
            if familia == "Maxim":
                consumo_previsto_corantes += float(plano_producao.producao_planejada) * 0.02
        return consumo_previsto_corantes
    
