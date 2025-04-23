from django.contrib import admin
from .models import Protocolo,Trecho, Atendimento, DescricaoTrecho, Mensagem, Servico, Responsavel, OrdemServico, SuporteProtocolo
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
    list_display = ('numero_chamado_interno', 'estado', 'tipo_evento', 'responsavel_trecho', 'data_hora_falha', 'get_pop_trecho_display')
    search_fields = ('numero_chamado_interno', 'estado', 'responsavel_trecho')
    list_filter = ('estado', 'tipo_evento', 'ativo', 'pop_trecho')
    class Media:
        js = ('js/protocolo_admin.js',)
    
    def get_pop_trecho_display(self, obj):
        """Retorna uma versão formatada do POP/Trecho para exibição na lista."""
        return obj.get_pop_trecho_info()
    get_pop_trecho_display.short_description = 'POP/Trecho'
    
    # Preencher campos automaticamente quando o Trecho for selecionado
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Verifica se o campo for 'trecho'
        if db_field.name == "trecho":
            kwargs['queryset'] = Trecho.objects.all()  # Isso não é necessário, mas garante que o queryset esteja correto
        # Verifica se o campo for 'pop_trecho'
        elif db_field.name == "pop_trecho":
            kwargs['queryset'] = Servico.objects.all().order_by('id_cliente_servico')
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

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('id_cliente_servico', 'get_descricao_resumida')
    search_fields = ('id_cliente_servico', 'descricao')
    ordering = ['id_cliente_servico']
    list_per_page = 50  # Aumentar para mostrar mais itens por página
    
    def get_descricao_resumida(self, obj):
        return obj.get_descricao_resumida()
    get_descricao_resumida.short_description = 'Descrição'
    
    def has_add_permission(self, request):
        # Desabilitar a adição manual, já que os serviços são importados
        return False

@admin.register(Responsavel)
class ResponsavelAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'ativo')
    search_fields = ('nome', 'telefone', 'email')
    list_filter = ('ativo',)
    ordering = ['nome']

@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ('numero_ordem_servico', 'status', 'cliente', 'data_cadastro')
    list_filter = ('status', 'data_cadastro')
    search_fields = ('numero_ordem_servico', 'cliente')
    ordering = ['-data_cadastro']

@admin.register(SuporteProtocolo)
class SuporteProtocoloAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'responsavel', 'id_atendimento_status', 'ativo', 'data_hora_falha')
    list_filter = ('id_atendimento_status', 'ativo')
    search_fields = ('descricao', 'responsavel__nome')
    ordering = ['-id_atendimento_status']
