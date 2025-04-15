import csv
import unicodedata
from django.core.management.base import BaseCommand
from protocolocd.models import Trecho

class Command(BaseCommand):
    help = "Importa dados de trechos de um arquivo CSV para o banco de dados."

    def add_arguments(self, parser):
        parser.add_argument('arquivo_csv', type=str, help="Caminho para o arquivo CSV.")

    def handle(self, *args, **kwargs):
        caminho_csv = kwargs['arquivo_csv']
        try:
            with open(caminho_csv, 'r', encoding='utf-8') as csvfile:
                leitor_csv = csv.DictReader(csvfile)
                if not leitor_csv.fieldnames:
                    self.stderr.write(self.style.ERROR("O arquivo CSV não possui cabeçalhos ou está vazio."))
                    return

                for linha in leitor_csv:
                    try:
                        # Normaliza strings para lidar com caracteres especiais
                        trecho = Trecho.objects.create(
                            uf_a=self._normalize(linha['UF - A']),
                            municipio_a=self._normalize(linha['MUNICIPIO - A']),
                            nome_pop_a=self._normalize(linha['NOME DO POP - A']),
                            trecho=self._normalize(linha['TRECHO']),
                            uf_b=self._normalize(linha['UF - B']),
                            municipio_b=self._normalize(linha['MUNICIPIO - B']),
                            nome_pop_b=self._normalize(linha['NOME DO POP - B']),
                            tipo_rede=self._normalize(linha['TIPO DE REDE']),
                            responsaveis=self._normalize(linha['RESPONSAVEIS']),
                        )
                        self.stdout.write(self.style.SUCCESS(f"Trecho '{trecho.trecho}' importado com sucesso!"))
                    except KeyError as e:
                        self.stderr.write(self.style.ERROR(f"Erro ao importar linha: Coluna ausente no CSV: {e}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Erro inesperado ao importar linha: {e}"))

            self.stdout.write(self.style.SUCCESS("Importação concluída!"))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Arquivo {caminho_csv} não encontrado."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro inesperado: {e}"))

    def _normalize(self, text):
        """Normaliza o texto para lidar com caracteres especiais e remover espaços extras."""
        if text:
            return unicodedata.normalize('NFKD', text).strip()
        return text
    
# Para usar o comando:
#python manage.py importar_trechos protocolocd/management/a.csv