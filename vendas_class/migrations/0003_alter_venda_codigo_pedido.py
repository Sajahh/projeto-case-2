# Generated by Django 5.0 on 2024-01-16 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendas_class', '0002_venda_codigo_pedido'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venda',
            name='codigo_pedido',
            field=models.IntegerField(unique=True),
        ),
    ]