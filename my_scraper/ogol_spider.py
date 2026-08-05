import scrapy

class OgolSpider(scrapy.Spider):
    name = 'ogol'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    start_urls = ['https://www.ogol.com.br/equipe/atletico-mineiro/jogadores?epoca_stats_id=155']

    def parse(self, response):
        self.log(f"Acessado: {response.url}. Salvando HTML para depuração.")

        # Salva o conteúdo HTML da resposta em um arquivo para análise
        with open('pagina_atletico.html', 'wb') as f:
            f.write(response.body)

        self.log("HTML salvo em 'pagina_atletico.html'.")

        # A lógica de extração foi temporariamente removida para depuração.
        # player_rows = response.xpath('//div[@id="team_squad_stats"]//tbody/tr')
        # ...
