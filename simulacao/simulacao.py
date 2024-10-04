# simulacao.py
from models import Grupo, PlanoProducao, PlanoCompras, Custos, CapacidadeTeares, CapacidadeJets, CapacidadeRamas
from app import db

# Função principal da simulação
def executar_simulacao(grupo):

    # Buscar os dados do grupo
    periodo_atual = grupo.periodo_atual
    # periodo_simular = periodo_atual + 1
    periodo_simular = periodo_atual + 1
    print ("Periodo Atual = ", periodo_atual)

    ### Para teste###
    # TODO: Implementar Lógica para demanda real
    data_demanda_real = 3500
    ########

    for familia in ["Colmeia", "Piquet", "Maxim"]:
        plano_producao = PlanoProducao.query.filter_by(grupo_id = grupo.id,
                                                periodo_numero = periodo_simular,
                                                periodo_modificado = periodo_atual,
                                                familia=familia).order_by(
                                                    PlanoProducao.periodo_numero.asc()).first()

        # Para estoque inicial Futuro
        plano_producao_futuro = PlanoProducao.query.filter_by(grupo_id = grupo.id,
                                                        periodo_numero = periodo_simular+1,
                                                        periodo_modificado = periodo_atual,
                                                        familia=familia).order_by(
                                                            PlanoProducao.periodo_numero.asc()).first()

        ##### Para teste ####
        # TODO: Implementar Lógica para produção real
        data_producao_real = plano_producao.producao_planejada
        ########

        # Demanda real e Producao Real
        plano_producao.demanda_real = data_demanda_real
        plano_producao.producao_real = data_producao_real

        # Calculo para Vendas reais e perdidas
        vendas_perdidas, vendas = calculo_vendas(plano_producao.estoques_iniciais,
                                                 data_demanda_real,
                                                 data_producao_real)
        plano_producao.vendas_perdidas = vendas_perdidas
        plano_producao.vendas = vendas

        # Calculo para estoques
        estoque_final = calculo_estoques(plano_producao.estoques_iniciais,
                                         data_demanda_real,
                                         data_producao_real)

        plano_producao.estoques_finais = estoque_final
        plano_producao_futuro.estoques_iniciais = estoque_final

    db.session.commit()

# Funcao calculo vendas
def calculo_vendas(estoque_inicial, demanda_real, producao_real):

    if producao_real + estoque_inicial <= demanda_real:
        vendas = producao_real + estoque_inicial
        vendas_perdidas = demanda_real - producao_real - estoque_inicial
    else:
        vendas = round(demanda_real)
        vendas_perdidas = 0

    return vendas_perdidas, vendas

# Funcao Calculo estoque
def calculo_estoques(estoque_inicial, demanda_real, producao_real):
    estoque_final = producao_real - demanda_real + estoque_inicial
    if estoque_final < 0:
        estoque_final = 0

    return estoque_final