"""
RentSmart - Sistema de Orcamento de Locacao
R.M Imoveis

Trabalho da disciplina: Algorithmic Thinking & Introduction to Object-Oriented Programming
RA: 241981

Como executar:
    python rentsmart.py

O programa faz perguntas no terminal, calcula o orcamento mensal,
mostra um resumo detalhado e gera o arquivo projecao_12_meses.csv
com a projecao dos 12 meses da locacao.
"""

import csv

# ============================================================
# TABELA DE PRECOS (constantes)
# ============================================================
# Deixar os valores aqui no topo facilita a manutencao:
# se a imobiliaria mudar um preco, altera-se em um lugar so.

ALUGUEL_BASE = {
    "apartamento": 700.00,
    "casa": 900.00,
    "estudio": 1200.00,
}

ADICIONAL_SEGUNDO_QUARTO = {
    "apartamento": 200.00,
    "casa": 250.00,
}

VALOR_GARAGEM_CASA_APTO = 300.00
PACOTE_ESTUDIO_2_VAGAS = 250.00
VALOR_VAGA_EXTRA_ESTUDIO = 60.00

TAXA_CONTRATUAL = 2000.00
MAX_PARCELAS = 5

DESCONTO_APARTAMENTO_SEM_CRIANCAS = 0.05

ARQUIVO_CSV = "projecao_12_meses.csv"


# ============================================================
# FUNCOES DE ENTRADA (com validacao)
# ============================================================
# Cada funcao pergunta uma informacao e so aceita resposta valida.
# Enquanto o usuario digitar algo errado, o programa pergunta de novo.

def perguntar_opcao(mensagem, opcoes_validas):
    """Pergunta uma opcao e so aceita se estiver na lista de opcoes validas."""
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in opcoes_validas:
            return resposta
        print("  Opcao invalida. Escolha uma destas: " + ", ".join(opcoes_validas))


def perguntar_sim_nao(mensagem):
    """Pergunta uma pergunta de sim/nao e devolve True ou False."""
    resposta = perguntar_opcao(mensagem + " (s/n): ", ["s", "n"])
    return resposta == "s"


def perguntar_inteiro(mensagem, minimo, maximo):
    """Pergunta um numero inteiro dentro de um intervalo."""
    while True:
        resposta = input(mensagem).strip()
        if resposta.isdigit():
            numero = int(resposta)
            if minimo <= numero <= maximo:
                return numero
        print("  Valor invalido. Digite um numero inteiro entre "
              + str(minimo) + " e " + str(maximo) + ".")


# ============================================================
# CLASSE IMOVEL (classe mae)
# ============================================================
# A classe Imovel guarda o que e comum a todos os imoveis:
# o tipo, a quantidade de quartos e o aluguel base.
# As classes filhas (Apartamento, Casa, Estudio) herdam dela
# e cada uma implementa o seu proprio calculo de adicionais.

class Imovel:
    def __init__(self, tipo, quartos):
        self.tipo = tipo
        self.quartos = quartos
        self.aluguel_base = ALUGUEL_BASE[tipo]
        self.adicionais = []  # lista de (descricao, valor)

    def adicionar_adicional(self, descricao, valor):
        """Guarda um adicional para aparecer no resumo do orcamento."""
        self.adicionais.append((descricao, valor))

    def total_adicionais(self):
        """Soma todos os adicionais cadastrados."""
        total = 0.0
        for descricao, valor in self.adicionais:
            total = total + valor
        return total

    def desconto(self):
        """Regra padrao: nenhum desconto. As filhas podem sobrescrever."""
        return 0.0

    def aluguel_mensal(self):
        """Calculo final: base + adicionais - desconto."""
        return self.aluguel_base + self.total_adicionais() - self.desconto()

    def descricao(self):
        return self.tipo + " de " + str(self.quartos) + " quarto(s)"


# ============================================================
# CLASSE APARTAMENTO
# ============================================================

class Apartamento(Imovel):
    def __init__(self, quartos, tem_garagem, tem_criancas):
        super().__init__("apartamento", quartos)
        self.tem_garagem = tem_garagem
        self.tem_criancas = tem_criancas

        if quartos == 2:
            self.adicionar_adicional("Segundo quarto",
                                     ADICIONAL_SEGUNDO_QUARTO["apartamento"])
        if tem_garagem:
            self.adicionar_adicional("Vaga de garagem", VALOR_GARAGEM_CASA_APTO)

    def desconto(self):
        # 5% sobre o aluguel ja com adicionais, somente se nao houver criancas.
        if not self.tem_criancas:
            valor_com_adicionais = self.aluguel_base + self.total_adicionais()
            return valor_com_adicionais * DESCONTO_APARTAMENTO_SEM_CRIANCAS
        return 0.0

    def descricao_desconto(self):
        if not self.tem_criancas:
            return "Desconto de 5% (apartamento sem criancas)"
        return ""


# ============================================================
# CLASSE CASA
# ============================================================

class Casa(Imovel):
    def __init__(self, quartos, tem_garagem):
        super().__init__("casa", quartos)
        self.tem_garagem = tem_garagem

        if quartos == 2:
            self.adicionar_adicional("Segundo quarto",
                                     ADICIONAL_SEGUNDO_QUARTO["casa"])
        if tem_garagem:
            self.adicionar_adicional("Vaga de garagem", VALOR_GARAGEM_CASA_APTO)

    def descricao_desconto(self):
        return ""


# ============================================================
# CLASSE ESTUDIO
# ============================================================

class Estudio(Imovel):
    def __init__(self, vagas):
        super().__init__("estudio", 1)
        self.vagas = vagas

        # Regra: ou nenhuma vaga, ou o pacote de 2 vagas (R$ 250),
        # e a partir da terceira vaga soma-se R$ 60 por vaga extra.
        if vagas == 2:
            self.adicionar_adicional("Pacote de 2 vagas", PACOTE_ESTUDIO_2_VAGAS)
        elif vagas > 2:
            extras = vagas - 2
            self.adicionar_adicional(
                "Pacote de 2 vagas + " + str(extras) + " vaga(s) extra(s)",
                PACOTE_ESTUDIO_2_VAGAS + (extras * VALOR_VAGA_EXTRA_ESTUDIO)
            )

    def descricao_desconto(self):
        return ""


# ============================================================
# CLASSE CONTRATO
# ============================================================

class Contrato:
    def __init__(self, parcelas):
        self.parcelas = parcelas
        self.taxa = TAXA_CONTRATUAL

    def valor_parcela(self):
        return self.taxa / self.parcelas


# ============================================================
# CLASSE ORCAMENTO
# ============================================================
# Junta o imovel e o contrato e sabe se apresentar na tela
# e gerar o arquivo CSV.

class Orcamento:
    def __init__(self, imovel, contrato):
        self.imovel = imovel
        self.contrato = contrato

    def exibir(self):
        print()
        print("=" * 55)
        print("        ORCAMENTO DE LOCACAO - R.M IMOVEIS")
        print("=" * 55)
        print("Imovel: " + self.imovel.descricao())
        print("-" * 55)
        print("Aluguel base ................ R$ %10.2f" % self.imovel.aluguel_base)

        for descricao, valor in self.imovel.adicionais:
            print("%-28s R$ %10.2f" % (descricao + " ...", valor))

        if self.imovel.desconto() > 0:
            print("%-28s R$ %10.2f" % ("Desconto 5% ...", -self.imovel.desconto()))

        print("-" * 55)
        print("ALUGUEL MENSAL .............. R$ %10.2f" % self.imovel.aluguel_mensal())
        print()
        print("Taxa contratual ............. R$ %10.2f" % self.contrato.taxa)
        print("Parcelamento ................ " + str(self.contrato.parcelas)
              + "x de R$ %.2f" % self.contrato.valor_parcela())
        print("=" * 55)

    def gerar_csv(self, nome_arquivo):
        """Gera a projecao dos 12 meses da locacao."""
        aluguel = self.imovel.aluguel_mensal()
        parcela = self.contrato.valor_parcela()

        with open(nome_arquivo, "w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(["Mes", "Aluguel (R$)", "Parcela da taxa (R$)",
                               "Total do mes (R$)"])

            for mes in range(1, 13):
                # A taxa contratual so e cobrada nos primeiros meses,
                # conforme o numero de parcelas escolhido.
                if mes <= self.contrato.parcelas:
                    parcela_mes = parcela
                else:
                    parcela_mes = 0.0

                total_mes = aluguel + parcela_mes
                escritor.writerow([mes, "%.2f" % aluguel, "%.2f" % parcela_mes,
                                   "%.2f" % total_mes])

        print()
        print("Arquivo gerado com sucesso: " + nome_arquivo)


# ============================================================
# FUNCAO PRINCIPAL
# ============================================================

def main():
    print("=" * 55)
    print("   RENTSMART - ORCAMENTO DE LOCACAO - R.M IMOVEIS")
    print("=" * 55)

    # 1) Tipo de imovel
    tipo = perguntar_opcao(
        "\nTipo de imovel (apartamento / casa / estudio): ",
        ["apartamento", "casa", "estudio"]
    )

    # 2) Monta o objeto conforme o tipo escolhido
    if tipo == "apartamento":
        quartos = perguntar_inteiro("Quantos quartos (1 ou 2)? ", 1, 2)
        tem_garagem = perguntar_sim_nao("Deseja vaga de garagem?")
        tem_criancas = perguntar_sim_nao("Ha criancas morando no imovel?")
        imovel = Apartamento(quartos, tem_garagem, tem_criancas)

    elif tipo == "casa":
        quartos = perguntar_inteiro("Quantos quartos (1 ou 2)? ", 1, 2)
        tem_garagem = perguntar_sim_nao("Deseja vaga de garagem?")
        imovel = Casa(quartos, tem_garagem)

    else:  # estudio
        print("  Estudio: 0 vagas, o pacote de 2 vagas, ou mais vagas.")
        vagas = perguntar_inteiro("Quantas vagas de garagem (0 a 10)? ", 0, 10)
        if vagas == 1:
            print("  Atencao: nao existe opcao de 1 vaga. O pacote minimo e de 2 vagas.")
            vagas = perguntar_inteiro("Informe 0 ou de 2 a 10 vagas: ", 0, 10)
            while vagas == 1:
                vagas = perguntar_inteiro("Informe 0 ou de 2 a 10 vagas: ", 0, 10)
        imovel = Estudio(vagas)

    # 3) Parcelamento da taxa contratual
    parcelas = perguntar_inteiro(
        "\nEm quantas parcelas pagar a taxa contratual (1 a 5)? ", 1, MAX_PARCELAS
    )
    contrato = Contrato(parcelas)

    # 4) Mostra o orcamento e gera o CSV
    orcamento = Orcamento(imovel, contrato)
    orcamento.exibir()
    orcamento.gerar_csv(ARQUIVO_CSV)


# Este bloco garante que o programa so roda quando executado diretamente.
if __name__ == "__main__":
    main()
