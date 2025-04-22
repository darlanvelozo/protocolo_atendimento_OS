from django.core.management.base import BaseCommand
import psycopg2
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    filename='importacao_servicos.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Command(BaseCommand):
    help = 'Importa serviços do HubSoft para o sistema de protocolamento'
    
    # Configurações dos bancos de dados
    DB_CONFIG_HUBSOFT = {
        'dbname': 'hubsoft',
        'user': 'mega_leitura',
        'password': '4630a1512ee8e738f935a73a65cebf75b07fcab5',
        'host': '177.10.118.77',
        'port': '9432'
    }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--cliente',
            type=int,
            default=45418,
            help='ID do cliente no HubSoft (padrão: 45418)'
        )
    
    def handle(self, *args, **options):
        cliente_id = options['cliente']
        self.stdout.write(self.style.SUCCESS(f'Iniciando importação de serviços para o cliente {cliente_id}...'))
        
        try:
            # Buscar serviços do Hubsoft
            services = self.fetch_services_from_hubsoft(cliente_id)
            
            if not services:
                self.stdout.write(self.style.WARNING('Nenhum serviço encontrado para importação'))
                return
            
            # Inserir serviços no banco de protocolamento
            processed_count = self.insert_services_into_django(services)
            
            self.stdout.write(self.style.SUCCESS(f'Importação concluída com sucesso! {processed_count} serviços processados.'))
        
        except Exception as e:
            logging.error(f"Erro no processo de importação: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Erro durante a importação: {str(e)}'))
    
    def connect_to_db(self, config):
        """Estabelece conexão com o banco de dados baseado na configuração fornecida."""
        try:
            conn = psycopg2.connect(**config)
            logging.info(f"Conexão estabelecida com sucesso ao banco {config['dbname']} em {config['host']}")
            return conn
        except Exception as e:
            logging.error(f"Erro ao conectar ao banco {config['dbname']}: {str(e)}")
            raise
    
    def fetch_services_from_hubsoft(self, cliente_id):
        """Busca os serviços do Hubsoft conforme a consulta SQL especificada."""
        conn = None
        try:
            conn = self.connect_to_db(self.DB_CONFIG_HUBSOFT)
            cursor = conn.cursor()
            
            query = """
            SELECT
                cs.id_cliente_servico,
                s.descricao
            FROM
                cliente_servico cs
            LEFT JOIN
                servico s ON cs.id_servico = s.id_servico
            WHERE
                cs.id_cliente = %s
            """
            
            cursor.execute(query, (cliente_id,))
            services = cursor.fetchall()
            
            self.stdout.write(self.style.SUCCESS(f"Recuperados {len(services)} serviços do Hubsoft"))
            logging.info(f"Recuperados {len(services)} serviços do Hubsoft")
            
            return services
        
        except Exception as e:
            logging.error(f"Erro ao buscar serviços do Hubsoft: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
                logging.info("Conexão com Hubsoft fechada")
    
    def insert_services_into_django(self, services):
        """Insere os serviços recuperados na tabela protocolocd_servico usando o ORM do Django."""
        from protocolocd.models import Servico
        
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        
        # Contagem antes da inserção
        count_before = Servico.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Total de serviços antes: {count_before}"))
        
        for service in services:
            id_cliente_servico, descricao = service
            
            try:
                # Verificar se o serviço já existe
                servico, created = Servico.objects.update_or_create(
                    id_cliente_servico=id_cliente_servico,
                    defaults={
                        'descricao': descricao
                    }
                )
                
                if created:
                    inserted_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                logging.error(f"Erro ao processar serviço {id_cliente_servico}: {str(e)}")
                self.stdout.write(self.style.ERROR(f"Erro ao processar serviço {id_cliente_servico}: {str(e)}"))
                skipped_count += 1
                continue
        
        # Contagem após a inserção
        count_after = Servico.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f"Inserção concluída: {inserted_count} inseridos, {updated_count} atualizados, {skipped_count} ignorados"))
        self.stdout.write(self.style.SUCCESS(f"Total de serviços antes: {count_before}, depois: {count_after}"))
        
        logging.info(f"Inserção concluída: {inserted_count} inseridos, {updated_count} atualizados, {skipped_count} ignorados")
        logging.info(f"Total de serviços antes: {count_before}, depois: {count_after}")
        
        return inserted_count + updated_count 