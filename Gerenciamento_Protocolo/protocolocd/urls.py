from django.urls import path
from . import views
from django.http import JsonResponse
from .models import Trecho
from django.contrib.auth.decorators import login_required
def trecho_json(request, pk):
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

urlpatterns = [
    path('', login_required(views.home), name='home'),
    path('protocolo/<int:protocolo_id>/', login_required(views.detalhes_protocolo), name='detalhes_protocolo'),
    path('listar-protocolos/', login_required(views.listar_protocolos), name='listar_protocolos'),
    path('trecho/<int:pk>/json/', login_required(views.trecho_json), name='trecho-json'),
    path('gestao-de-protocolos/', login_required(views.gestao_protocolos), name='gestao_protocolos'),
]