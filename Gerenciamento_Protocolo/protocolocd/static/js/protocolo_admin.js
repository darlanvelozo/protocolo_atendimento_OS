document.addEventListener('DOMContentLoaded', function () {
    const trechoSelect = document.querySelector('#id_trecho');

    if (trechoSelect) {
        trechoSelect.addEventListener('change', function () {
            const trechoId = this.value;

            if (trechoId) {
                // Faz uma requisição AJAX para buscar os dados do Trecho
                fetch(`/trecho/${trechoId}/json/`)
                    .then(response => response.json())
                    .then(data => {
                        if (!data.error) {
                            // Preenche os campos do formulário com os dados do Trecho
                            
                            document.querySelector('#id_tipo_rede').value = data.tipo_rede || '';
                            document.querySelector('#id_estado').value = data.uf_a || '';
                            document.querySelector('#id_nome_pop_a').value = data.nome_pop_a || '';
                            document.querySelector('#id_nome_pop_b').value = data.nome_pop_b || '';
                            document.querySelector('#id_responsavel_trecho').value = data.responsaveis || '';
                            document.querySelector('#id_site_a').value = data.nome_pop_a || '';
                            document.querySelector('#id_equipamento_site_a').value = data.equipamento_a || '';
                            document.querySelector('#id_porta_site_a').value = data.porta_a || '';
                            document.querySelector('#id_site_b').value = data.nome_pop_b || '';
                            document.querySelector('#id_equipamento_site_b').value = data.equipamento_b || '';
                            document.querySelector('#id_porta_site_b').value = data.porta_b || '';
                        } else {
                            console.error(data.error);
                        }
                    })
                    .catch(error => console.error('Erro ao buscar os dados do trecho:', error));
            }
        });
    }
});
