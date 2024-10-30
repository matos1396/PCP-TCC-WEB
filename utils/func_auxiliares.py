import math
from models import (PlanoCompras,
                    PlanoProducao, TaxaProducao,
                    Custos, CapacidadeJets,
                    CapacidadeRamas, CapacidadeTeares,
                    RelatorioFinanceiro, CustosFixos,
                    CustosCapital, CustosTerceirizacao,
                    CustosCompraMP, ReceitasVendas,
                    CustosEstoques, CustosVendasPerdidas,
                    ControlePlanos,
                    db)

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
                plano_compra.consumo_previsto = math.ceil(consumo_previsto)
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
                t_tear = math.ceil(producao_planejada * taxa_tear)
                t_rama = math.ceil(producao_planejada * (taxa_rama_1 + taxa_rama_2))
                t_jet = math.ceil(producao_planejada)

                if capacidade_teares:
                    setattr(capacidade_teares, familia.lower(), t_tear)
                if capacidade_ramas:
                    setattr(capacidade_ramas, familia.lower(), t_rama)
                if capacidade_jets:
                    setattr(capacidade_jets, familia.lower(), t_jet)

    for period in periods:
        capacidade_teares = capacidades_teares_dict.get(period)
        capacidade_ramas = capacidades_ramas_dict.get(period)
        capacidade_jets = capacidades_jets_dict.get(period)

        if capacidade_teares:
            soma_teares = capacidade_teares.colmeia + capacidade_teares.piquet + capacidade_teares.maxim
            capacidade_teares.capacidade_necessaria = math.ceil(soma_teares + capacidade_teares.produtividade + capacidade_teares.setup)
        if capacidade_ramas:
            soma_ramas = capacidade_ramas.colmeia + capacidade_ramas.piquet + capacidade_ramas.maxim
            capacidade_ramas.capacidade_necessaria = math.ceil(soma_ramas + capacidade_ramas.produtividade + capacidade_ramas.setup)
        if capacidade_jets:
            soma_jets = capacidade_jets.colmeia + capacidade_jets.piquet + capacidade_jets.maxim
            capacidade_jets.capacidade_necessaria = math.ceil(soma_jets + capacidade_jets.produtividade + capacidade_jets.setup)

    db.session.commit()



def atualizar_financeiro(grupo):
    periodo_atual = grupo.periodo_atual
    custos = Custos.query.first()
    period_list = range(13, 25)

    # Pré-carregar todos os registros relevantes para os períodos de 13 a 25 em uma única consulta
    capacidade_teares = CapacidadeTeares.query.filter_by(grupo_id=grupo.id).filter(
        CapacidadeTeares.periodo_numero.in_(period_list)
    ).all()
    capacidade_ramas = CapacidadeRamas.query.filter_by(grupo_id=grupo.id).filter(
        CapacidadeRamas.periodo_numero.in_(period_list)
    ).all()
    capacidade_jets = CapacidadeJets.query.filter_by(grupo_id=grupo.id).filter(
        CapacidadeJets.periodo_numero.in_(period_list)
    ).all()

    plano_compras = PlanoCompras.query.filter_by(grupo_id=grupo.id).filter(
        PlanoCompras.periodo_numero.in_(period_list)
    )
    plano_producao = PlanoProducao.query.filter_by(grupo_id=grupo.id).filter(
        PlanoProducao.periodo_numero.in_(period_list)
    )

    # Pré-carregar registros
    custos_fixos_registros = CustosFixos.query.filter_by(grupo_id=grupo.id).filter(
        CustosFixos.periodo.in_(period_list)
    ).all()
    custos_compra_mp_registros = CustosCompraMP.query.filter_by(grupo_id=grupo.id).filter(
        CustosCompraMP.periodo.in_(period_list)
    ).all()
    custos_estoques_registros = CustosEstoques.query.filter_by(grupo_id=grupo.id).filter(
        CustosEstoques.periodo.in_(period_list)
    ).all()
    custos_terceirizacao_registros = CustosTerceirizacao.query.filter_by(grupo_id=grupo.id).filter(
        CustosTerceirizacao.periodo.in_(period_list)
    ).all()
    custos_capital_registros = CustosCapital.query.filter_by(grupo_id=grupo.id).filter(
        CustosCapital.periodo.in_(period_list)
    ).all()
    custos_vendas_perdidas_registros = CustosVendasPerdidas.query.filter_by(grupo_id=grupo.id).filter(
        CustosVendasPerdidas.periodo.in_(period_list)
    ).all()
    receitas_vendas_registros = ReceitasVendas.query.filter_by(grupo_id=grupo.id).filter(
        ReceitasVendas.periodo.in_(period_list)
    ).all()
    relatorio_financeiro_registros = RelatorioFinanceiro.query.filter_by(grupo_id=grupo.id).filter(
        RelatorioFinanceiro.periodo.in_(period_list)
    ).all()



    # Organizar os dados em dicionários por período para acesso rápido
    capacidade_teares_dict = {ct.periodo_numero: ct for ct in capacidade_teares}
    capacidade_ramas_dict = {cr.periodo_numero: cr for cr in capacidade_ramas}
    capacidade_jets_dict = {cj.periodo_numero: cj for cj in capacidade_jets}
    custos_fixos_dict = {cf.periodo: cf for cf in custos_fixos_registros}
    custos_compra_mp_dict = {cmp.periodo: cmp for cmp in custos_compra_mp_registros}
    plano_compras_dict = {(pc.periodo_numero, pc.material): pc for pc in plano_compras}
    plano_producao_dict = {(pp.periodo_numero, pp.familia): pp for pp in plano_producao}
    custos_estoques_dict = {ce.periodo: ce for ce in custos_estoques_registros}
    custos_terceirizacao_dict = {ct.periodo: ct for ct in custos_terceirizacao_registros}
    custos_capital_dict = {cc.periodo: cc for cc in custos_capital_registros}
    custos_vendas_perdidas_dict = {cvp.periodo: cvp for cvp in custos_vendas_perdidas_registros}
    receitas_vendas_dict = {rv.periodo: rv for rv in receitas_vendas_registros}

    ## CUSTO FIXO
    novos_custos_fixos = []  # Lista para armazenar novos registros
    for period in period_list:
        # Obter as capacidades de cada máquina para o período atual
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
    ## FIM CUSTO FIXO

    ## CUSTO COMPRAS MP
    novos_custos_compra_mp = []
    for period in period_list:
        # Inicializar as variáveis de custos de compra e emergência
        c_compras_corantes = 0.0
        c_compras_fio_algodao = 0.0
        c_compras_fio_sintetico = 0.0
        c_emergencia_corante = 0.0
        c_emergencia_fio_algodao = 0.0
        c_emergencia_fio_sintetico = 0.0

        for material, custo_unitario in [
            ('Corantes', custos.custo_unitario_corantes),
            ('Fio Algodao', custos.custo_unitario_fio_algodao),
            ('Fio Sintetico', custos.custo_unitario_fio_sintetico)
        ]:
            plano_compra = plano_compras_dict.get((period, material))
            if plano_compra:
                if period > periodo_atual:
                    compra_valor = plano_compra.compra_planejada * custo_unitario
                else:
                    compra_valor = plano_compra.compra_real * custo_unitario
                if plano_compra.compra_emergencial > 0:
                    emergencia_valor = plano_compra.compra_emergencial * custo_unitario * custos.custo_unitario_compra_emergencia
                else: emergencia_valor = 0
                # Atribuir o valor à variável correspondente
                if material == 'Corantes':
                    c_compras_corantes = compra_valor
                    c_emergencia_corante = emergencia_valor
                elif material == 'Fio Algodao':
                    c_compras_fio_algodao = compra_valor
                    c_emergencia_fio_algodao = emergencia_valor
                elif material == 'Fio Sintetico':
                    c_compras_fio_sintetico = compra_valor
                    c_emergencia_fio_sintetico = emergencia_valor

        # Cálculo do custo total de compras e emergência
        c_compras_total = (
            c_compras_corantes + c_compras_fio_algodao + c_compras_fio_sintetico +
            c_emergencia_corante + c_emergencia_fio_algodao + c_emergencia_fio_sintetico
        )

        # Atualizar ou criar o registro em CustosCompraMP
        custos_compra_mp = custos_compra_mp_dict.get(period)
        if custos_compra_mp:
            custos_compra_mp.c_compras_corantes = c_compras_corantes
            custos_compra_mp.c_compras_fio_algodao = c_compras_fio_algodao
            custos_compra_mp.c_compras_fio_sintetico = c_compras_fio_sintetico
            custos_compra_mp.c_emergencia_corante = c_emergencia_corante
            custos_compra_mp.c_emergencia_fio_algodao = c_emergencia_fio_algodao
            custos_compra_mp.c_emergencia_fio_sintetico = c_emergencia_fio_sintetico
            custos_compra_mp.c_compras_total = c_compras_total
        else:
            novos_custos_compra_mp.append(CustosCompraMP(
                grupo_id=grupo.id,
                periodo=period,
                c_compras_corantes=c_compras_corantes,
                c_compras_fio_algodao=c_compras_fio_algodao,
                c_compras_fio_sintetico=c_compras_fio_sintetico,
                c_emergencia_corante=c_emergencia_corante,
                c_emergencia_fio_algodao=c_emergencia_fio_algodao,
                c_emergencia_fio_sintetico=c_emergencia_fio_sintetico,
                c_compras_total=c_compras_total
            ))

    # Adicionar novos registros de CustosCompraMP ao banco de dados
    db.session.add_all(novos_custos_compra_mp)
    db.session.commit()
    ## FIM CUSTO COMPRAS MP

    ## CUSTO ESTOQUES
    novos_custos_estoques = []
    for period in period_list:
        # Inicializar as variáveis de custos de estoque
        c_estoque_corantes = 0.0
        c_estoque_fio_algodao = 0.0
        c_estoque_fio_sintetico = 0.0
        c_estoque_colmeia = 0.0
        c_estoque_piquet = 0.0
        c_estoque_maxim = 0.0

        # Cálculo para cada tipo de material no estoque
        for material, custo_unitario, taxa in [
            ('Corantes', custos.custo_unitario_corantes, custos.taxa_armazenagem),
            ('Fio Algodao', custos.custo_unitario_fio_algodao, custos.taxa_armazenagem),
            ('Fio Sintetico', custos.custo_unitario_fio_sintetico, custos.taxa_armazenagem)
        ]:
            plano_compra = plano_compras_dict.get((period, material))
            if plano_compra:
                estoque_medio = (plano_compra.estoques_iniciais + plano_compra.estoques_finais) / 2
                custo_estoque = estoque_medio * custo_unitario * taxa

                if material == 'Corantes':
                    c_estoque_corantes = custo_estoque
                elif material == 'Fio Algodao':
                    c_estoque_fio_algodao = custo_estoque
                elif material == 'Fio Sintetico':
                    c_estoque_fio_sintetico = custo_estoque

        # Cálculo para cada tipo de família de produto no estoque
        for familia, custo_unitario, taxa in [
            ('Colmeia', custos.custo_unitario_colmeia, custos.taxa_armazenagem),
            ('Piquet', custos.custo_unitario_piquet, custos.taxa_armazenagem),
            ('Maxim', custos.custo_unitario_maxim, custos.taxa_armazenagem)
        ]:
            plano_producao = plano_producao_dict.get((period, familia))
            if plano_producao:
                estoque_medio = (plano_producao.estoques_iniciais + plano_producao.estoques_finais) / 2
                custo_estoque = estoque_medio * custo_unitario * taxa

                if familia == 'Colmeia':
                    c_estoque_colmeia = custo_estoque
                elif familia == 'Piquet':
                    c_estoque_piquet = custo_estoque
                elif familia == 'Maxim':
                    c_estoque_maxim = custo_estoque

        # Cálculo do custo total de estoque
        c_estoque_total = (
            c_estoque_corantes + c_estoque_fio_algodao + c_estoque_fio_sintetico +
            c_estoque_colmeia + c_estoque_piquet + c_estoque_maxim
        )

        # Atualizar ou criar o registro em CustosEstoques
        custos_estoque = custos_estoques_dict.get(period)
        if custos_estoque:
            custos_estoque.c_estoque_corantes = c_estoque_corantes
            custos_estoque.c_estoque_fio_algodao = c_estoque_fio_algodao
            custos_estoque.c_estoque_fio_sintetico = c_estoque_fio_sintetico
            custos_estoque.c_estoque_colmeia = c_estoque_colmeia
            custos_estoque.c_estoque_piquet = c_estoque_piquet
            custos_estoque.c_estoque_maxim = c_estoque_maxim
            custos_estoque.c_estoque_total = c_estoque_total
        else:
            novos_custos_estoques.append(CustosEstoques(
                grupo_id=grupo.id,
                periodo=period,
                c_estoque_corantes=c_estoque_corantes,
                c_estoque_fio_algodao=c_estoque_fio_algodao,
                c_estoque_fio_sintetico=c_estoque_fio_sintetico,
                c_estoque_colmeia=c_estoque_colmeia,
                c_estoque_piquet=c_estoque_piquet,
                c_estoque_maxim=c_estoque_maxim,
                c_estoque_total=c_estoque_total
            ))

    # Adicionar novos registros de CustosEstoques ao banco de dados
    db.session.add_all(novos_custos_estoques)
    db.session.commit()
    ## FIM CUSTO ESTOQUE

    ## CUSTO TERCEIRIZAÇÃO
    novos_custos_terceirizacao = []
    for period in period_list:
        # Obter as capacidades de cada máquina para o período
        capacidade_teares = capacidade_teares_dict.get(period)
        capacidade_ramas = capacidade_ramas_dict.get(period)
        capacidade_jets = capacidade_jets_dict.get(period)

        # Cálculo para terceirização
        c_terc_tecelagem = (capacidade_teares.capacidade_terceirizada * custos.custo_terceirizacao_tecelagem) if capacidade_teares else 0.0
        c_terc_fixacao_acabamento = (capacidade_ramas.capacidade_terceirizada * custos.custo_terceirizacao_fixacao_acabamento) if capacidade_ramas else 0.0
        c_terc_purga_tinturaria = (capacidade_jets.capacidade_terceirizada * custos.custo_terceirizacao_purga_tinturaria) if capacidade_jets else 0.0

        # Total de custo de terceirização
        c_terc_total = c_terc_tecelagem + c_terc_fixacao_acabamento + c_terc_purga_tinturaria

        # Atualizar ou criar registro em CustosTerceirizacao
        custos_terceirizacao = custos_terceirizacao_dict.get(period)
        if custos_terceirizacao:
            custos_terceirizacao.c_terc_tecelagem = c_terc_tecelagem
            custos_terceirizacao.c_terc_purga_tinturaria = c_terc_purga_tinturaria
            custos_terceirizacao.c_terc_fixacao_acabamento = c_terc_fixacao_acabamento
            custos_terceirizacao.c_terc_total = c_terc_total
        else:
            # Criar novo registro
            novos_custos_terceirizacao.append(CustosTerceirizacao(
                grupo_id=grupo.id,
                periodo=period,
                c_terc_tecelagem=c_terc_tecelagem,
                c_terc_purga_tinturaria=c_terc_purga_tinturaria,
                c_terc_fixacao_acabamento=c_terc_fixacao_acabamento,
                c_terc_total=c_terc_total
            ))

    # Adicionar novos registros de CustosTerceirizacao ao banco de dados
    db.session.add_all(novos_custos_terceirizacao)
    db.session.commit()
    ## FIM CUSTO TERCEIRIZAÇÃO

    ## CUSTO CAPITAL
    novos_custos_capital = []
    for period in period_list:
        capacidade_teares = capacidade_teares_dict.get(period)
        capacidade_ramas = capacidade_ramas_dict.get(period)
        capacidade_jets = capacidade_jets_dict.get(period)
        plano_compra = plano_compras_dict.get(period)
        plano_producao = plano_producao_dict.get(period)

        # Cálculo para custos de capital dos equipamentos
        custo_capital_teares = (capacidade_teares.quantidade * custos.preco_aquisicao_teares * custos.tma) if capacidade_teares else 0.0
        custo_capital_ramas = (capacidade_ramas.quantidade * custos.preco_aquisicao_rama * custos.tma) if capacidade_ramas else 0.0
        custo_capital_jets = ((capacidade_jets.quantidade_tipo1 * custos.preco_aquisicao_jet1 +
                               capacidade_jets.quantidade_tipo2 * custos.preco_aquisicao_jet2 +
                               capacidade_jets.quantidade_tipo3 * custos.preco_aquisicao_jet3) * custos.tma) if capacidade_jets else 0.0

        # Cálculo do custo de capital para produtos acabados (PA)
        custo_capital_pa = 0
        for familia in ['Colmeia', 'Piquet', 'Maxim']:
            plano_produto = plano_producao_dict.get((period, familia))
            if plano_produto:
                estoque_inicial = plano_produto.estoques_iniciais or 0.0
                estoque_final = plano_produto.estoques_finais or 0.0
                custo_unitario = getattr(custos, f"custo_unitario_{familia.lower()}", 0.0)
                estoque_medio = (estoque_inicial + estoque_final) / 2
                custo_capital_pa += estoque_medio * custo_unitario * custos.tma

        # Cálculo do custo de capital para matéria-prima (MP)
        custo_capital_mp = 0
        for material_1, material_2 in [('corantes', "Corantes"),
                                       ('fio_algodao', "Fio Algodao"),
                                       ('fio_sintetico', "Fio Sintetico")]:
            plano_mp = plano_compras_dict.get((period, material_2))
            if plano_mp:
                estoque_inicial = plano_mp.estoques_iniciais or 0.0
                estoque_final = plano_mp.estoques_finais or 0.0
                custo_unitario = getattr(custos, f"custo_unitario_{material_1}", 0.0)
                estoque_medio = (estoque_inicial + estoque_final) / 2
                custo_capital_mp += estoque_medio * custo_unitario * custos.tma

        # Total de custo de capital
        custo_capital_total = (custo_capital_teares + custo_capital_jets + custo_capital_ramas +
                               custo_capital_pa + custo_capital_mp)

        # Atualizar ou criar registro em CustosCapital
        custos_capital = custos_capital_dict.get(period)
        if custos_capital:
            custos_capital.custo_capital_teares = custo_capital_teares
            custos_capital.custo_capital_jets = custo_capital_jets
            custos_capital.custo_capital_ramas = custo_capital_ramas
            custos_capital.custo_capital_pa = custo_capital_pa
            custos_capital.custo_capital_mp = custo_capital_mp
            custos_capital.custo_capital_total = custo_capital_total
        else:
            # Criar novo registro
            novos_custos_capital.append(CustosCapital(
                grupo_id=grupo.id,
                periodo=period,
                custo_capital_teares=custo_capital_teares,
                custo_capital_jets=custo_capital_jets,
                custo_capital_ramas=custo_capital_ramas,
                custo_capital_pa=custo_capital_pa,
                custo_capital_mp=custo_capital_mp,
                custo_capital_total=custo_capital_total
            ))

    # Adicionar novos registros de CustosCapital ao banco de dados
    db.session.add_all(novos_custos_capital)
    db.session.commit()
    ## FIM CUSTO CAPITAL

    ## CUSTO VENDAS PERDIDAS
    novos_custos_vendas_perdidas = []
    for period in period_list:
        # Inicializa os custos de vendas perdidas para cada família
        c_vp_colmeia = c_vp_piquet = c_vp_maxim = 0.0

        # Calcular os custos de vendas perdidas para cada família
        for familia in ['Colmeia', 'Piquet', 'Maxim']:
            plano_familia = plano_producao_dict.get((period, familia))
            if plano_familia:
                vendas_perdidas = plano_familia.vendas_perdidas or 0.0
                custo_venda_perdida = getattr(custos, f"custo_venda_perdida_{familia.lower()}", 0.0)
                custo_perdido = vendas_perdidas * custo_venda_perdida

                if familia == 'Colmeia':
                    c_vp_colmeia = custo_perdido
                elif familia == 'Piquet':
                    c_vp_piquet = custo_perdido
                elif familia == 'Maxim':
                    c_vp_maxim = custo_perdido

        # Cálculo total das vendas perdidas
        c_vp_total = c_vp_colmeia + c_vp_piquet + c_vp_maxim

        # Atualizar ou criar registro em CustosVendasPerdidas
        custos_vendas_perdidas = custos_vendas_perdidas_dict.get(period)
        if custos_vendas_perdidas:
            # Atualizar valores existentes
            custos_vendas_perdidas.c_vp_comeia = c_vp_colmeia
            custos_vendas_perdidas.c_vp_piquet = c_vp_piquet
            custos_vendas_perdidas.c_vp_maxim = c_vp_maxim
            custos_vendas_perdidas.c_vp_total = c_vp_total
        else:
            # Criar novo registro
            novos_custos_vendas_perdidas.append(CustosVendasPerdidas(
                grupo_id=grupo.id,
                periodo=period,
                c_vp_comeia=c_vp_colmeia,
                c_vp_piquet=c_vp_piquet,
                c_vp_maxim=c_vp_maxim,
                c_vp_total=c_vp_total
            ))

    # Adicionar novos registros de CustosVendasPerdidas ao banco de dados
    db.session.add_all(novos_custos_vendas_perdidas)
    db.session.commit()
    ## FIM CUSTO VENDAS PERDIDAS

    ## RECEITAS VENDAS
    novas_receitas_vendas = []
    for period in period_list:
        # Inicializa as receitas de vendas para cada família
        r_vendas_colmeia = r_vendas_piquet = r_vendas_maxim = 0.0

        # Calcular as receitas de vendas para cada família
        for familia in ['Colmeia', 'Piquet', 'Maxim']:
            plano_familia = plano_producao_dict.get((period, familia))
            if plano_familia:
                vendas = plano_familia.vendas or 0.0
                preco_venda = getattr(custos, f"preco_venda_{familia.lower()}", 0.0)
                receita_venda = vendas * preco_venda

                if familia == 'Colmeia':
                    r_vendas_colmeia = receita_venda
                elif familia == 'Piquet':
                    r_vendas_piquet = receita_venda
                elif familia == 'Maxim':
                    r_vendas_maxim = receita_venda

        # Cálculo total das receitas de vendas
        r_vendas_total = r_vendas_colmeia + r_vendas_piquet + r_vendas_maxim

        # Atualizar ou criar registro em ReceitasVendas
        receitas_vendas = receitas_vendas_dict.get(period)
        if receitas_vendas:
            # Atualizar valores existentes
            receitas_vendas.r_vendas_colmeia = r_vendas_colmeia
            receitas_vendas.r_vendas_piquet = r_vendas_piquet
            receitas_vendas.r_vendas_maxim = r_vendas_maxim
            receitas_vendas.r_vendas_total = r_vendas_total
        else:
            # Criar novo registro
            novas_receitas_vendas.append(ReceitasVendas(
                grupo_id=grupo.id,
                periodo=period,
                r_vendas_colmeia=r_vendas_colmeia,
                r_vendas_piquet=r_vendas_piquet,
                r_vendas_maxim=r_vendas_maxim,
                r_vendas_total=r_vendas_total
            ))

    # Adicionar novos registros de ReceitasVendas ao banco de dados
    db.session.add_all(novas_receitas_vendas)
    db.session.commit()
    ## FIM RECEITAS VENDAS

    ## RELATÓRIO FINANCEIRO
    novos_relatorios_financeiros = []
    ro_acumulado = 0  # Variável para armazenar o resultado operacional acumulado

    for period in period_list:
        # Obter os custos e receitas para o período
        custos_fixos = custos_fixos_dict.get(period).c_fixo_total if custos_fixos_dict.get(period) else 0.0
        custos_compra_mp = custos_compra_mp_dict.get(period).c_compras_total if custos_compra_mp_dict.get(period) else 0.0
        custos_estoques = custos_estoques_dict.get(period).c_estoque_total if custos_estoques_dict.get(period) else 0.0
        custos_terceirizacao = custos_terceirizacao_dict.get(period).c_terc_total if custos_terceirizacao_dict.get(period) else 0.0
        custos_capital = custos_capital_dict.get(period).custo_capital_total if custos_capital_dict.get(period) else 0.0
        custos_vendas_perdidas = custos_vendas_perdidas_dict.get(period).c_vp_total if custos_vendas_perdidas_dict.get(period) else 0.0
        receitas_vendas = receitas_vendas_dict.get(period).r_vendas_total if receitas_vendas_dict.get(period) else 0.0

        # Calcular custos totais
        custos_totais = (custos_fixos + custos_compra_mp + custos_estoques +
                         custos_terceirizacao + custos_capital + custos_vendas_perdidas)

        # Calcular resultado operacional
        resultado_operacional = receitas_vendas - custos_totais

        # Atualizar o resultado operacional acumulado
        ro_acumulado += resultado_operacional

        # Atualizar ou criar o registro em RelatorioFinanceiro
        relatorio_financeiro = next((rf for rf in relatorio_financeiro_registros if rf.periodo == period), None)
        if relatorio_financeiro:
            # Atualizar valores existentes
            relatorio_financeiro.custos_fixos = custos_fixos
            relatorio_financeiro.custos_compra_mp = custos_compra_mp
            relatorio_financeiro.custos_estoques = custos_estoques
            relatorio_financeiro.custos_terceirizacao = custos_terceirizacao
            relatorio_financeiro.custos_capital = custos_capital
            relatorio_financeiro.custos_vendas_perdidas = custos_vendas_perdidas
            relatorio_financeiro.custos_totais = custos_totais
            relatorio_financeiro.receitas_vendas = receitas_vendas
            relatorio_financeiro.resultado_operacional = resultado_operacional
            relatorio_financeiro.ro_acumulado = ro_acumulado
        else:
            # Criar novo registro
            novos_relatorios_financeiros.append(RelatorioFinanceiro(
                grupo_id=grupo.id,
                periodo=period,
                custos_fixos=custos_fixos,
                custos_compra_mp=custos_compra_mp,
                custos_estoques=custos_estoques,
                custos_terceirizacao=custos_terceirizacao,
                custos_capital=custos_capital,
                custos_vendas_perdidas=custos_vendas_perdidas,
                custos_totais=custos_totais,
                receitas_vendas=receitas_vendas,
                resultado_operacional=resultado_operacional,
                ro_acumulado=ro_acumulado
            ))

    # Adicionar novos registros de RelatorioFinanceiro ao banco de dados
    db.session.add_all(novos_relatorios_financeiros)
    db.session.commit()
    ## FIM RELATÓRIO FINANCEIRO


    db.session.commit()




def calcular_consumo_previsto(grupo, material, periodo, periodo_atual):
    # #### Dicionario apenas para consulta manualmente (DEBUG / TESTE)
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


def set_flag_controle(grupo, tipo):
    # Obtém o período atual do grupo
    periodo_simular = grupo.periodo_atual + 1

    # Verifica se já existe um registro para o grupo e período
    controle = ControlePlanos.query.filter_by(grupo_id=grupo.id, periodo=periodo_simular).first()

    if not controle:
        # Se não existir, cria um novo registro
        controle = ControlePlanos(
            grupo_id=grupo.id,
            periodo=periodo_simular,
            plano_producao_salvo=(tipo == "producao"),
            plano_compras_salvo=(tipo == "compras")
        )
        db.session.add(controle)
    else:
        if tipo == "producao":
            controle.plano_producao_salvo = True
        elif tipo == "compras":
            controle.plano_compras_salvo = True

    # Commit para salvar as mudanças no banco de dados
    db.session.commit()
