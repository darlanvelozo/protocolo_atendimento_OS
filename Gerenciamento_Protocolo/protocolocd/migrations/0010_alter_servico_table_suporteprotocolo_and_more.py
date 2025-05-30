# Generated by Django 5.1.5 on 2025-04-22 14:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('protocolocd', '0009_ordemservico'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='servico',
            table='protocolocd_servico',
        ),
        migrations.CreateModel(
            name='SuporteProtocolo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_cliente_servico', models.IntegerField()),
                ('descricao', models.TextField()),
                ('id_tipo_atendimento', models.IntegerField()),
                ('id_atendimento_status', models.IntegerField(choices=[(1, 'PENDENTE (Abertura de OS)'), (2, 'AGUARDANDO ANALISE')])),
                ('ativo', models.BooleanField(default=True)),
                ('protocolo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='protocolocd.protocolo')),
                ('responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='protocolocd.responsavel')),
            ],
        ),
        migrations.AddField(
            model_name='protocolo',
            name='protocolos_suporte',
            field=models.ManyToManyField(blank=True, related_name='protocolos', to='protocolocd.suporteprotocolo'),
        ),
    ]
