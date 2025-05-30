# Generated by Django 5.1.5 on 2025-04-15 20:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('protocolocd', '0003_descricaotrecho'),
    ]

    operations = [
        migrations.CreateModel(
            name='Servico',
            fields=[
                ('id_cliente_servico', models.IntegerField(primary_key=True, serialize=False)),
                ('descricao', models.TextField(verbose_name='Descrição do Serviço')),
            ],
            options={
                'verbose_name': 'Serviço',
                'verbose_name_plural': 'Serviços',
                'ordering': ['id_cliente_servico'],
            },
        ),
        migrations.AddField(
            model_name='protocolo',
            name='pop_trecho',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='protocolos_pop_trecho', to='protocolocd.servico', verbose_name='POP/Trecho'),
        ),
    ]
