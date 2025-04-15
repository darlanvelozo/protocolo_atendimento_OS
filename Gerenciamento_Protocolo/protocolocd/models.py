from django.db import models
import requests
from django.db import transaction
from django.contrib.auth.models import User




# Token inicial
token_primordial = []
def adicionar_mensagem(id_mensagem, mensagem):
    # Obter o token
    if not token_primordial:
        new_token()
    token = token_primordial[0]

    url = f"https://api.megalinktelecom.hubsoft.com.br/api/v1/integracao/atendimento/adicionar_mensagem/{id_mensagem}"
    payload = {
        "mensagem": mensagem
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao adicionar mensagem: {response.text}")
# Função para obter um novo token
def new_token():
    url = "https://api.megalinktelecom.hubsoft.com.br/oauth/token"
    data = {
        "client_id": "75",
        "client_secret": "JCqEuHLcam8zt0mYGvJVP8rZpNJFA2hf7aMrhGmM",
        "username": "api.hub.buzzlead@megalinkinternet.com.br",
        "password": "Api#5554",
        "grant_type": "password"
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        token_primordial.clear()
        token_primordial.append(response.json()['access_token'])
        return token_primordial[0]
    else:
        raise Exception(f"Erro ao obter token: {response.text}")

# Função para criar atendimento
def new_atendimento(id_cliente_servico, descricao, nome, telefone, id_tipo_atendimento):
    # Obter o token
    if not token_primordial:
        new_token()
    token = token_primordial[0]

    url = "https://api.megalinktelecom.hubsoft.com.br/api/v1/integracao/atendimento"
    payload = {
        "id_cliente_servico": id_cliente_servico,
        "descricao": descricao,
        "nome": nome,
        "telefone": telefone,
        "id_tipo_atendimento": id_tipo_atendimento
        
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao criar atendimento: {response.text}")
    



class Atendimento(models.Model):
    protocolo_atendimento = models.CharField(max_length=50)
    descricao_abertura = models.TextField()
    A_tipo_atendimento = models.CharField(max_length=50)
    usuario_abertura = models.CharField(max_length=100)
    usuario_responsavel = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    cliente_nome = models.CharField(max_length=255)
    cliente_codigo = models.IntegerField()
    servico_id = models.IntegerField()
    servico_nome = models.CharField(max_length=255)
    data_cadastro = models.DateTimeField()
    data_fechamento = models.DateTimeField(null=True, blank=True)
    id_atendimento = models.IntegerField(default=None)


    def __str__(self):
        return f"Atendimento {self.protocolo_atendimento} - {self.status}"
    
class Mensagem(models.Model):
    atendimento = models.ForeignKey(Atendimento, on_delete=models.CASCADE, related_name='mensagens')
    usuario = models.CharField(max_length=100)  # Nome do usuário que enviou a mensagem
    data_hora = models.DateTimeField(auto_now_add=True)  # Data e hora da mensagem
    mensagem = models.TextField()  # Conteúdo da mensagem

    def __str__(self):
        return f"Mensagem de {self.usuario} em {self.data_hora}"


class Protocolo(models.Model):
    
    RUPTURA = 'RUPTURA'
    ATENUACAO = 'ATENUAÇÃO'
    INDISPONIBILIDADE = 'INDISPONIBILIDADE'
    TAXA_ERRO = 'TAXA DE ERRO'
    OSCILACAO = 'OSCILAÇÃO'
    FALHA_ELETRICA = 'FALHA ELÉTRICA'
    OUTRAS = 'OUTRAS'

    TIPOS_EVENTO = [
        (RUPTURA, 'Ruptura'),
        (ATENUACAO, 'Atenuação'),
        (INDISPONIBILIDADE, 'Indisponibilidade'),
        (TAXA_ERRO, 'Taxa de Erro'),
        (OSCILACAO, 'Oscilação'),
        (FALHA_ELETRICA, 'Falha Elétrica'),
        (OUTRAS, 'Outros')
    ]

    METRO = 'METRO'
    DWDM = 'DWDM'
    CAPACIDADE = 'CAPACIDADE'
    
    TIPOS_REDE = [
        (METRO, 'Rede Metro'),
        (DWDM, 'Rede DWDM'),
        (CAPACIDADE, 'Capacidade'),
        
    ]

    SIGLAS_EVENTOS = {
        RUPTURA: "RUP",
        ATENUACAO: "ATN",
        INDISPONIBILIDADE: "IND",
        TAXA_ERRO: "TXE",
        OSCILACAO: "OSC",
        FALHA_ELETRICA: "RGE",
        OUTRAS: "OUT",
    }

    TIPOS_ATENDIMENTO = [
        (661, 'NOC TX > ATENUAÇÃO PARCEIRO'),
        (662, 'NOC TX > OSCILAÇÃO PARCEIRO'),
        (663, 'NOC TX > PT NOC - CLIENTE'),
        (664, 'NOC TX > RUPTURA PARCEIRO'),
        (666, 'NOC TX > ATENUAÇÃO MEGALINK'),
        (668, 'NOC TX > OSCILAÇÃO MEGALINK'),
        (723, 'NOC TX > ENERGIA'),
        (660, 'NOC TX'),
        (667, 'NOC TX > INDISPONIBILIDADE SITE'),
        (670, 'NOC TX > REBOOT SITE'),
        (669, 'NOC TX > OUTROS'),
        (671, 'NOC TX > RUPTURA MEGALINK'),
    ]

    trecho = models.ForeignKey('Trecho', on_delete=models.CASCADE, verbose_name="Trecho")
    
    tipo_rede = models.CharField(max_length=100, choices=TIPOS_REDE)
    numero_chamado_interno = models.CharField(max_length=50, default='AUTOMATICO')
    estado = models.CharField(max_length=2) 
    nome_pop_a = models.CharField(max_length=100)
    nome_pop_b = models.CharField(max_length=100)
    nome_responsavel = models.CharField(max_length=100, default='Megalink')
    numero_chamado_os = models.CharField(max_length=50)
    tipo_evento = models.CharField(max_length=20, choices=TIPOS_EVENTO)
    site_a = models.CharField(max_length=100)
    equipamento_site_a = models.CharField(max_length=100)
    porta_site_a = models.CharField(max_length=50)
    site_b = models.CharField(max_length=100)
    equipamento_site_b = models.CharField(max_length=100)
    porta_site_b = models.CharField(max_length=50)
    data_hora_falha = models.DateTimeField()  # Para armazenar data e hora
    responsavel_trecho = models.CharField(max_length=100)
    protocolo_parceiro = models.CharField(max_length=100)
    clientes_afetados = models.TextField()  # Usando TextField para clientes afetados
    data_criacao = models.DateTimeField(auto_now_add=True)
    titulo = models.CharField(max_length=255, editable=False)
    atendimento = models.ForeignKey('Atendimento', null=True, blank=True, on_delete=models.SET_NULL)
    tipo_atendimento = models.IntegerField(
          # Tamanho máximo para o ID (ex.: '661')
        choices=TIPOS_ATENDIMENTO,
        verbose_name="Tipo de Atendimento",
        help_text="Selecione o tipo de atendimento com base nos IDs disponíveis",
        default=660
    )
    ativo = models.BooleanField(default=True)
    class Meta:
        ordering = ['trecho']
    def gerar_titulo(self):
        # Obter a sigla do tipo de evento
        sigla_evento = self.SIGLAS_EVENTOS.get(self.tipo_evento, "OUT")
    
        # Montar o título
        titulo = (
            f"{self.numero_chamado_interno}-"
            f"{self.estado}:{sigla_evento}:"
            f"{self.tipo_rede}:"
            f"{self.nome_pop_a}"
        )
        if self.nome_pop_b:
            titulo += f" <> {self.nome_pop_b}"
        titulo += f" - {self.responsavel_trecho}"

        return titulo
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Verifica se é um novo registro
        self.titulo = self.gerar_titulo()  # Gera o título antes de salvar
        
        # Salva o protocolo no banco
        super().save(*args, **kwargs)
        
        # Caso seja um novo protocolo, cria o atendimento fora da transação
        if is_new:
            try:
                # Use um bloco separado para garantir a consistência
                with transaction.atomic():
                    atendimento_data = new_atendimento(
                        id_cliente_servico=79856,
                        descricao= f"""
                        Titulo: {self.titulo}\n
                        Trecho: {self.trecho}\n
                        Tipo de Rede: {self.tipo_rede}\n
                        Tipo de Evento: {self.tipo_evento}\n
                        Responsável: {self.responsavel_trecho}\n  
                        Data/Hora Falha: {self.data_hora_falha}\n
                        Pop A: {self.nome_pop_a}\n
                        Pop B: {self.nome_pop_b}\n
                        Equipamento A: {self.equipamento_site_a}\n
                        Porta A: {self.porta_site_a}\n
                        Equipamento B: {self.equipamento_site_b}\n
                        Porta B: {self.porta_site_b}\n
                        Clientes Afetados: {self.clientes_afetados}\n
                        Número do Chamado Interno: {self.numero_chamado_interno}\n
                        Número do Chamado OS: {self.numero_chamado_os}\n
                        Protocolo Parceiro: {self.protocolo_parceiro}
                        """,
                        nome=self.nome_responsavel,
                        telefone=86999998888,
                        id_tipo_atendimento = self.tipo_atendimento
                    )
                    
                    print(atendimento_data)
                    if atendimento_data.get('status') == 'success':
                        atendimento_info = atendimento_data['atendimento']
                        atendimento = Atendimento.objects.create(
                            id_atendimento=atendimento_info['id_atendimento'],
                            protocolo_atendimento=atendimento_info['protocolo'],
                            descricao_abertura=atendimento_info['descricao_abertura'],
                            A_tipo_atendimento=atendimento_info['tipo_atendimento'],
                            usuario_abertura=atendimento_info['usuario_abertura'],
                            usuario_responsavel=atendimento_info['usuario_responsavel'],
                            status=atendimento_info['status'],
                            cliente_nome=atendimento_info['cliente']['nome_razaosocial'],
                            cliente_codigo=atendimento_info['cliente']['codigo_cliente'],
                            servico_id=atendimento_info['servico']['id_cliente_servico'],
                            servico_nome=atendimento_info['servico']['nome'],
                            data_cadastro=self.data_hora_falha
                        )
                           
                    # Atualiza o campo numero_chamado_interno com o protocolo gerado
                    self.numero_chamado_interno = atendimento.protocolo_atendimento
                    self.atendimento = atendimento
                    super().save(*args, **kwargs)
                    self.titulo = self.gerar_titulo()
                    # Salva novamente para refletir as alterações
                    super().save(*args, **kwargs)
                       
            except Exception as e:
                # Log ou tratativa para falhas no atendimento
                print(f"Erro ao criar atendimento: {e}")
    def __str__(self):
        return f"Protocolo - {self.numero_chamado_interno} ({self.tipo_rede})"



class Trecho(models.Model):
    # Campos do trecho
    uf_a = models.CharField(max_length=2, verbose_name="UF - A")  # Ex.: MA
    municipio_a = models.CharField(max_length=100, verbose_name="Município - A")  # Ex.: Imperatriz
    nome_pop_a = models.CharField(max_length=100, verbose_name="Nome do POP - A")  # Ex.: Eletronet
    trecho = models.CharField(max_length=255, verbose_name="Trecho")  # Ex.: Eletronet <> Vila Nova
    uf_b = models.CharField(max_length=2, verbose_name="UF - B")  # Ex.: MA
    municipio_b = models.CharField(max_length=100, verbose_name="Município - B")  # Ex.: Imperatriz
    nome_pop_b = models.CharField(max_length=100, verbose_name="Nome do POP - B")  # Ex.: Vila Nova
    tipo_rede = models.CharField(max_length=100, verbose_name="Tipo de Rede")  # Ex.: Metro
    responsaveis = models.CharField(max_length=255, verbose_name="Responsáveis")  # Ex.: NETFACIL
    equipamento_a = models.CharField(max_length=100, verbose_name="Equipamento - A", default='')
    porta_a = models.CharField(max_length=100, verbose_name="Porta Equipamento - A", default='')
    equipamento_b = models.CharField(max_length=100, verbose_name="Equipamento - B", default='')
    porta_b = models.CharField(max_length=100, verbose_name="Porta Equipamento - B", default='')
    class Meta:
        ordering = ['trecho']
    def __str__(self):
        # Representação do trecho como string
        return f"{self.trecho} ({self.tipo_rede})"
    
class DescricaoTrecho(models.Model):
    trecho = models.ForeignKey(Trecho, on_delete=models.CASCADE, related_name='descricoes')
    descricao = models.TextField(verbose_name="Descrição do Trecho")
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Descrição do Trecho"
        verbose_name_plural = "Descrições dos Trechos"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Descrição para {self.trecho.trecho} ({self.data_criacao})"