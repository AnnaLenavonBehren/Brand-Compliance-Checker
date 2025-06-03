FROM ollama/ollama

ENV APP_HOME=/home

WORKDIR $APP_HOME

COPY . .

RUN chmod +x pull-mistral.sh

ENTRYPOINT ["/usr/bin/bash", "pull-mistral.sh"]