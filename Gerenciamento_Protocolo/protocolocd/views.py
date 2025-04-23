from django.shortcuts import render, get_object_or_404
from .models import Protocolo, Trecho
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Protocolo
from .models import adicionar_mensagem  # Função já existente
from django.utils import timezone
from datetime import timedelta
import requests
from django.contrib.auth.decorators import login_required
from .models import Atendimento, Mensagem, Responsavel
from django.shortcuts import render, redirect
from .models import SuporteProtocolo
from .forms import SuporteProtocoloForm

def criar_protocolo_suporte(request):
    if request.method == 'POST':
        form = SuporteProtocoloForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home_suporte')
    else:
        form = SuporteProtocoloForm()
    return render(request, 'protocolocd/criar_protocolo_suporte.html', {'form': form})

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

def gestao_protocolos(request):
    current_order = request.GET.get('order', 'asc')
    current_sort = request.GET.get('sort', 'data_criacao')

    # Alternar entre 'asc' e 'desc'
    new_order_data_criacao = 'desc' if current_order == 'asc' and current_sort == 'data_criacao' else 'asc'
    new_order_tipo_evento = 'desc' if current_order == 'asc' and current_sort == 'tipo_evento' else 'asc'
    new_order_tipo_rede = 'desc' if current_order == 'asc' and current_sort == 'tipo_rede' else 'asc'
    new_order_estado = 'desc' if current_order == 'asc' and current_sort == 'estado' else 'asc'
    # Criar uma lista para adicionar informações extras
    protocolos_com_mensagens = []
    # Obter a hora atual considerando o fuso horário
    now = timezone.now()

    # Ordenar os protocolos
    protocolos = Protocolo.objects.filter(ativo=True).order_by(f"{'' if current_order == 'asc' else '-'}{current_sort}")

    # Criar uma lista com a diferença em horas para aplicar as cores
    for protocolo in protocolos:
        data_criacao = protocolo.data_criacao

        # Garantir que 'data_criacao' seja um objeto timezone-aware
        if data_criacao.tzinfo is None:
            data_criacao = timezone.make_aware(data_criacao)

        # Calcular a diferença em horas
        diff = now - data_criacao
        diff_hours = diff.total_seconds() / 3600

        # Definir a cor com base na diferença de horas
        if diff_hours < 3:
            protocolo.color_class = 'green-row'
        elif diff_hours < 6:
            protocolo.color_class = 'yellow-row'
        else:
            protocolo.color_class = 'red-row'
        # Obter a última mensagem do atendimento relacionado (se existir)
        if protocolo.atendimento:
            ultima_mensagem = (
                protocolo.atendimento.mensagens.order_by('-data_hora').first()
            )
            ultima_data_hora = (
                ultima_mensagem.data_hora if ultima_mensagem else "Sem atualização"
            )
        else:
            ultima_data_hora = "Sem atualização"

        # Adicionar informações ao protocolo
        protocolos_com_mensagens.append({
            'protocolo': protocolo,
            'ultima_data_hora': ultima_data_hora,
        })
    
    context = {
        'current_order': current_order,
        'current_sort': current_sort,
        'new_order_data_criacao': new_order_data_criacao,
        'new_order_tipo_evento': new_order_tipo_evento,
        'new_order_tipo_rede': new_order_tipo_rede,
        'new_order_estado': new_order_estado,
        'protocolos': protocolos,
        'protocolos_com_mensagens': protocolos_com_mensagens,
    }
    return render(request, 'protocolocd/gestao_protocolos.html', context)

def home(request):
    """
    Exibe a página inicial com os protocolos filtrados.
    """
    # Obtém todos os protocolos
    protocolos_disponiveis = Protocolo.objects.all()

    # Filtra protocolos com base nos parâmetros enviados
    protocolos_disponiveis = filtrar_protocolos(protocolos_disponiveis, request.GET)

    context = {
        'protocolos': protocolos_disponiveis,
    }

    # Renderiza o template home.html
    return render(request, 'protocolocd/home.html', context)

def listar_protocolos(request):
    """
    Lista todos os protocolos com opções de filtragem.
    """
    protocolos_disponiveis = Protocolo.objects.all()
    trechos_disponiveis = Trecho.objects.all()

    protocolos_disponiveis = filtrar_protocolos(protocolos_disponiveis, request.GET)

    context = {
        'protocolos_disponiveis': protocolos_disponiveis,
        'trechos_disponiveis': trechos_disponiveis,
    }

    return render(request, 'listar_protocolos.html', context)

def filtrar_protocolos(queryset, params):
    """
    Filtra os protocolos com base nos parâmetros enviados na requisição.
    """
    if params.get('numero_chamado_interno'):
        queryset = queryset.filter(numero_chamado_interno__icontains=params['numero_chamado_interno'])
    if params.get('trecho'):
        queryset = queryset.filter(trecho__trecho__icontains=params['trecho'])
    if params.get('tipo_rede'):
        queryset = queryset.filter(tipo_rede=params['tipo_rede'])
    if params.get('tipo_evento'):
        queryset = queryset.filter(tipo_evento=params['tipo_evento'])
    if params.get('data_inicio'):
        try:
            data_inicio = datetime.strptime(params['data_inicio'], '%Y-%m-%d')
            queryset = queryset.filter(data_criacao__gte=data_inicio)
        except ValueError:
            pass
    if params.get('data_fim'):
        try:
            data_fim = datetime.strptime(params['data_fim'], '%Y-%m-%d')
            queryset = queryset.filter(data_criacao__lte=data_fim)
        except ValueError:
            pass

     # Filtrar por status ativo/inativo
    ativo = params.get('ativo')
    inativo = params.get('inativo')
    if ativo and inativo:
        # Se ambos forem marcados, retorna todos os protocolos
        queryset = queryset.filter(ativo__in=[True, False])
    elif ativo:
        queryset = queryset.filter(ativo=True)
    elif inativo:
        queryset = queryset.filter(ativo=False)
    return queryset

def detalhes_protocolo(request, protocolo_id):
    """
    Exibe detalhes de um protocolo específico e processa o envio de uma mensagem.
    """
    # Busca o protocolo e o atendimento relacionado
    protocolo = get_object_or_404(Protocolo, id=protocolo_id)
    atendimento = protocolo.atendimento

    if request.method == "POST":
        # Captura os dados do formulário enviados via AJAX
        mensagem = request.POST.get('mensagem')  # Mensagem do formulário

        if atendimento:  # Verifica se há um atendimento associado ao protocolo
            # Obtém o nome do usuário logado
            id_atendimento = atendimento.id_atendimento
            nome_usuario = request.user.username

            # Salva a mensagem no banco de dados
            Mensagem.objects.create(
                atendimento=atendimento,
                usuario=nome_usuario,
                mensagem=mensagem
            )
             # Concatena o nome do usuário com a mensagem
            mensagem_completa = f"{nome_usuario}: {mensagem}"
            # >>> Adicione aqui o código para executar a função adicionar_mensagem <<<
            # Exemplo:
            response = adicionar_mensagem(id_atendimento, mensagem_completa)

            return JsonResponse({'status': 'success', 'message': 'Mensagem enviada com sucesso!'})

        return JsonResponse({'status': 'error', 'message': 'Protocolo sem atendimento associado.'})

    # Busca as mensagens relacionadas ao atendimento
    mensagens = Mensagem.objects.filter(atendimento=atendimento).order_by('data_hora')

    # Renderiza a página com os dados do protocolo, atendimento e mensagens
    return render(request, 'protocolocd/detalhes_protocolo.html', {
        'protocolo': protocolo,
        'atendimento': atendimento,
        'mensagens': mensagens,
    })

def trecho_json(request, pk):
    """
    Retorna os detalhes de um trecho em formato JSON.
    """
    try:
        trecho = Trecho.objects.get(pk=pk)

        data = {
            "tipo_rede": trecho.tipo_rede,
            "nome_pop_a": trecho.nome_pop_a,
            "nome_pop_b": trecho.nome_pop_b,
            "responsaveis": trecho.responsaveis,
            "uf_a": trecho.uf_a,
            "municipio_a": trecho.municipio_a,
            "uf_b": trecho.uf_b,
            "municipio_b": trecho.municipio_b,
            "equipamento_a": trecho.equipamento_a,
            "porta_a": trecho.porta_a,
            "equipamento_b": trecho.equipamento_b,
            "porta_b": trecho.porta_b,
        }

        return JsonResponse(data)
    except Trecho.DoesNotExist:
        return JsonResponse({"error": "Trecho não encontrado"}, status=404)

def home_suporte(request):
    """
    Exibe a página inicial com os protocolos de suporte filtrados.
    """
    # Obtém todos os protocolos de suporte
    protocolos_suporte = SuporteProtocolo.objects.all()
    
    # Obtém as opções para os filtros
    responsaveis = Responsavel.objects.filter(ativo=True)
    tipos_atendimento = SuporteProtocolo.TIPOS_ATENDIMENTO_SUPORTE
    status_atendimento_choices = SuporteProtocolo.status_atendimento_choices_suporte
    
    # Filtra protocolos com base nos parâmetros enviados
    if request.GET.get('descricao'):
        protocolos_suporte = protocolos_suporte.filter(descricao__icontains=request.GET.get('descricao'))
    
    if request.GET.get('responsavel'):
        protocolos_suporte = protocolos_suporte.filter(responsavel_id=request.GET.get('responsavel'))
    
    if request.GET.get('tipo_atendimento'):
        protocolos_suporte = protocolos_suporte.filter(id_tipo_atendimento=request.GET.get('tipo_atendimento'))
    
    if request.GET.get('status_atendimento'):
        protocolos_suporte = protocolos_suporte.filter(id_atendimento_status=request.GET.get('status_atendimento'))
    
    # Filtrar por status ativo/inativo
    ativo = request.GET.get('ativo')
    inativo = request.GET.get('inativo')
    
    if ativo == 'true' and inativo != 'false':
        protocolos_suporte = protocolos_suporte.filter(ativo=True)
    elif inativo == 'false' and ativo != 'true':
        protocolos_suporte = protocolos_suporte.filter(ativo=False)
    # Se ambos estiverem marcados ou nenhum estiver marcado, não aplicamos filtro de status
    
    context = {
        'protocolos_suporte': protocolos_suporte,
        'responsaveis': responsaveis,
        'tipos_atendimento': tipos_atendimento,
        'status_atendimento_choices': status_atendimento_choices,
    }
    
    return render(request, 'protocolocd/home_suporte.html', context)

def detalhes_protocolo_suporte(request, protocolo_id):
    """
    Exibe detalhes de um protocolo de suporte específico.
    """
    # Busca o protocolo de suporte pelo ID
    protocolo = get_object_or_404(SuporteProtocolo, id=protocolo_id)
    
    # Renderiza a página com os dados do protocolo de suporte
    return render(request, 'protocolocd/detalhes_protocolo_suporte.html', {
        'protocolo': protocolo,
    })

def relacionar_protocolos(request):
    """
    Exibe e permite relacionar protocolos com protocolos de suporte.
    """
    # Obter protocolos ativos
    protocolos = Protocolo.objects.filter(ativo=True)
    
    # Obter protocolos de suporte ativos
    protocolos_suporte = SuporteProtocolo.objects.filter(ativo=True)
    
    # Se for um POST, atualizar a relação
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            protocolo_id = request.POST.get('protocolo_id')
            suporte_id = request.POST.get('suporte_id')
            acao = request.POST.get('acao')  # 'adicionar' ou 'remover'
            
            protocolo = get_object_or_404(Protocolo, id=protocolo_id)
            suporte = get_object_or_404(SuporteProtocolo, id=suporte_id)
            
            if acao == 'adicionar':
                # Primeiro, removemos qualquer relacionamento existente
                suporte.protocolo = protocolo
                suporte.save()
                
                # Depois, adicionamos à relação many-to-many
                protocolo.protocolos_suporte.add(suporte)
                return JsonResponse({'status': 'success', 'message': 'Protocolos relacionados com sucesso!'})
            elif acao == 'remover':
                # Removemos o relacionamento
                suporte.protocolo = None
                suporte.save()
                
                # Removemos da relação many-to-many
                protocolo.protocolos_suporte.remove(suporte)
                return JsonResponse({'status': 'success', 'message': 'Relação removida com sucesso!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    # Criar um dicionário para mapear quais protocolos de suporte estão associados a quais protocolos
    relacoes = {}
    for protocolo in protocolos:
        relacoes[str(protocolo.id)] = list(protocolo.protocolos_suporte.values_list('id', flat=True))
    
    context = {
        'protocolos': protocolos,
        'protocolos_suporte': protocolos_suporte,
        'relacoes': relacoes,
    }
    
    return render(request, 'protocolocd/relacionar_protocolos.html', context)
