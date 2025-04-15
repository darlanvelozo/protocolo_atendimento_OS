from django.contrib import admin
from .models import Protocolo,Trecho, Atendimento, DescricaoTrecho
import csv
from django.http import HttpResponse


@admin.action(description="Importar Trechos de um CSV")
def importar_trechos_csv(modeladmin, request, queryset):
    if 'csv' in request.FILES:
        arquivo_csv = request.FILES['csv']
        leitor_csv = csv.DictReader(arquivo_csv.read().decode('utf-8').splitlines())
        for linha in leitor_csv:
            Trecho.objects.create(
                uf_a=linha['UF - A'],
                municipio_a=linha['MUNICIPIO - A'],
                nome_pop_a=linha['NOME DO POP - A'],
                trecho=linha['TRECHO'],
                uf_b=linha['UF - B'],
                municipio_b=linha['MUNICIPIO - B'],
                nome_pop_b=linha['NOME DO POP - B'],
                tipo_rede=linha['TIPO DE REDE'],
                responsaveis=linha['RESPONSAVEIS'],
            )
        return HttpResponse("Trechos importados com sucesso!")
    return HttpResponse("Nenhum arquivo CSV enviado.")

@admin.register(Trecho)
class TrechoAdmin(admin.ModelAdmin):
    list_display = ('trecho', 'uf_a', 'municipio_a', 'nome_pop_a', 'uf_b', 'municipio_b', 'nome_pop_b', 'tipo_rede', 'responsaveis')
    search_fields = ('trecho', 'uf_a', 'municipio_a', 'nome_pop_a', 'uf_b', 'municipio_b', 'nome_pop_b', 'tipo_rede')
#    actions = [importar_trechos_csv]


class ProtocoloAdmin(admin.ModelAdmin):
    ordering = ['trecho']
    list_display = ('numero_chamado_interno', 'estado', 'tipo_evento', 'responsavel_trecho', 'data_hora_falha')  # Customize as colunas que aparecem na listagem
    search_fields = ('numero_chamado_interno', 'estado', 'responsavel_trecho')  # Adiciona um campo de busca
    list_filter = ('estado', 'tipo_evento', 'ativo')  # Adiciona filtros de busca por estado e tipo de evento
    class Media:
        js = ('js/protocolo_admin.js',)
     # Preencher campos automaticamente quando o Trecho for selecionado
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Verifica se o campo for 'trecho'
        if db_field.name == "Trecho":
            kwargs['queryset'] = Trecho.objects.all()  # Isso não é necessário, mas garante que o queryset esteja correto
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.trecho:  # Se um trecho for selecionado
            trecho = obj.trecho  # Pega o Trecho selecionado
            # Preenche os campos automaticamente com base no Trecho
            obj.estado = trecho.uf_a
            obj.tipo_rede = trecho.tipo_rede
            obj.nome_pop_a = trecho.nome_pop_a
            obj.nome_pop_b = trecho.nome_pop_b
            obj.responsavel_trecho = trecho.responsaveis
            obj.site_a = trecho.nome_pop_a  # Assumindo que o nome do POP é o site
            obj.equipamento_site_a = trecho.equipamento_a
            obj.porta_site_a = trecho.porta_a
            obj.site_b = trecho.nome_pop_b  # Assumindo que o nome do POP é o site
            obj.equipamento_site_b = trecho.equipamento_b
            obj.porta_site_b = trecho.porta_b
        super().save_model(request, obj, form, change)

admin.site.register(Protocolo, ProtocoloAdmin)
from .models import Mensagem

@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'atendimento', 'data_hora', 'mensagem')
    list_filter = ('data_hora',)
    search_fields = ('usuario', 'mensagem')

@admin.register(DescricaoTrecho)
class DescricaoTrechoAdmin(admin.ModelAdmin):
    list_display = ('trecho', 'descricao', 'data_criacao')
    list_filter = ('data_criacao',)
    search_fields = ('trecho__trecho', 'descricao')
    ordering = ['-data_criacao']
