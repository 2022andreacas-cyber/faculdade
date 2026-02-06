# Projeto Andrea
from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
import csv


class Imovel(ABC):
    @abstractmethod
    def calcular_aluguel(self) -> float:
        """Retorna o valor do aluguel mensal."""
        raise NotImplementedError


@dataclass
class Apartamento(Imovel):
    quartos: int = 1              # 1 ou 2
    garagem: bool = False         # +300 se True
    tem_criancas: bool = True     # desconto 5% se False

    def calcular_aluguel(self) -> float:
        valor = 700.0
        if self.quartos == 2:
            valor += 200.0
        if self.garagem:
            valor += 300.0
        # Desconto 5% para apartamento se NÃO possui crianças
        if not self.tem_criancas:
            valor *= 0.95
        return valor


@dataclass
class Casa(Imovel):
    quartos: int = 1
    garagem: bool = False

    def calcular_aluguel(self) -> float:
        valor = 900.0
        if self.quartos == 2:
            valor += 250.0
        if self.garagem:
            valor += 300.0
        return valor


@dataclass
class Estudio(Imovel):
    estacionamento: bool = False  # se True: +250 (2 vagas)
    vagas_extras: int = 0         # extras além das 2: +60 cada

    def calcular_aluguel(self) -> float:
        valor = 1200.0
        if self.estacionamento:
            valor += 250.0  # pacote 2 vagas
            if self.vagas_extras > 0:
                valor += 60.0 * self.vagas_extras
        return valor


@dataclass
class Orcamento:
    imovel: Imovel
    valor_contrato: float = 2000.0
    parcelas_contrato: int = 5  # FIXO: contrato dividido em 5 e incluído só nos 5 primeiros meses

    def aluguel_mensal(self) -> float:
        return self.imovel.calcular_aluguel()

    def valor_parcela_contrato(self) -> float:
        return self.valor_contrato / self.parcelas_contrato

    def gerar_12_meses(self) -> list[dict]:
        """
        Gera 12 meses:
        - aluguel aparece em todos os meses
        - contrato (2000/5) aparece somente nos meses 1..5
        - meses 6..12 contrato = 0
        """
        aluguel = self.aluguel_mensal()
        parcela = self.valor_parcela_contrato()

        linhas = []
        for mes in range(1, 13):
            contrato_no_mes = parcela if mes <= self.parcelas_contrato else 0.0
            total = aluguel + contrato_no_mes

            linhas.append({
                "mes": mes,
                "aluguel": round(aluguel, 2),
                "contrato": round(contrato_no_mes, 2),
                "total": round(total, 2),
            })
        return linhas

    def exportar_csv(self, arquivo: str) -> None:
        linhas = self.gerar_12_meses()
        with open(arquivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["mes", "aluguel", "contrato", "total"],
                delimiter=";"
            )
            writer.writeheader()
            writer.writerows(linhas)


def ler_int(msg: str, validos: set[int] | None = None, minimo: int | None = None, maximo: int | None = None) -> int:
    while True:
        try:
            valor = int(input(msg).strip())
            if validos is not None and valor not in validos:
                print(f"Valor inválido. Use: {sorted(validos)}")
                continue
            if minimo is not None and valor < minimo:
                print(f"Valor inválido. Mínimo: {minimo}")
                continue
            if maximo is not None and valor > maximo:
                print(f"Valor inválido. Máximo: {maximo}")
                continue
            return valor
        except ValueError:
            print("Digite um número inteiro válido.")


def ler_sn(msg: str) -> bool:
    while True:
        v = input(msg).strip().lower()
        if v in ("s", "sim"):
            return True
        if v in ("n", "nao", "não"):
            return False
        print("Responda com S/N.")



def main():
    print("\n=== Imobiliária R.M - Orçamento de Aluguel ===")
    print("1) Apartamento (R$ 700,00 / 1 quarto)")
    print("2) Casa        (R$ 900,00 / 1 quarto)")
    print("3) Estúdio     (R$ 1200,00)\n")

    tipo = ler_int("Escolha o tipo (1-3): ", validos={1, 2, 3})

    # Criar objeto do imóvel conforme o tipo
    if tipo == 1:
        quartos = ler_int("Apartamento: 1 ou 2 quartos? ", validos={1, 2})
        garagem = ler_sn("Incluir vaga de garagem (+R$300)? (S/N): ")
        tem_criancas = ler_sn("Possui crianças? (S/N): ")
        imovel = Apartamento(quartos=quartos, garagem=garagem, tem_criancas=tem_criancas)

    elif tipo == 2:
        quartos = ler_int("Casa: 1 ou 2 quartos? ", validos={1, 2})
        garagem = ler_sn("Incluir vaga de garagem (+R$300)? (S/N): ")
        imovel = Casa(quartos=quartos, garagem=garagem)

    else:
        estacionamento = ler_sn("Adicionar estacionamento (2 vagas por +R$250)? (S/N): ")
        vagas_extras = 0
        if estacionamento:
            vagas_extras = ler_int("Quantas vagas extras além das 2? (0..): ", minimo=0)
        imovel = Estudio(estacionamento=estacionamento, vagas_extras=vagas_extras)

    # Contrato fixo: 2000 dividido em 5 e incluído nos 5 primeiros meses
    orc = Orcamento(imovel=imovel)

    aluguel = orc.aluguel_mensal()
    parcela_contrato = orc.valor_parcela_contrato()

    print("\n--- Resultado do Orçamento ---")
    print(f"Aluguel mensal: R$ {aluguel:.2f}")
    print(f"Contrato: R$ {orc.valor_contrato:.2f} em {orc.parcelas_contrato}x de R$ {parcela_contrato:.2f}")
    print("Obs.: O contrato entra somente nos meses 1 a 5. Do mês 6 ao 12, entra apenas o aluguel.\n")

    print("Prévia (primeiros 6 meses):")
    meses = orc.gerar_12_meses()
    for linha in meses[:6]:
        print(f"Mês {linha['mes']:02d} | Aluguel: R$ {linha['aluguel']:.2f} | "
              f"Contrato: R$ {linha['contrato']:.2f} | Total: R$ {linha['total']:.2f}")
    print("...")

    if ler_sn("\nDeseja gerar o CSV com 12 meses? (S/N): "):
        nome = input("Nome do arquivo (ex: parcelas.csv): ").strip()
        if not nome.lower().endswith(".csv"):
            nome += ".csv"
        orc.exportar_csv(nome)
        print(f"CSV gerado com sucesso: {nome}")

    print("\nFim do programa.\n")


if __name__ == "__main__":
    main()