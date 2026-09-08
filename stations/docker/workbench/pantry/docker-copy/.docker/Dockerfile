FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

COPY .docker/apt-packages.txt /tmp/apt-packages.txt
RUN apt-get update && xargs -a /tmp/apt-packages.txt apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /usr/bin/zsh baker
COPY .docker/install-omz-extensions.sh /tmp/install-omz-extensions.sh
RUN chmod +x /tmp/install-omz-extensions.sh
RUN su - baker -c 'RUNZSH=no CHSH=no KEEP_ZSHRC=yes sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"'
RUN su - baker -c '/tmp/install-omz-extensions.sh'
RUN su - baker -c 'curl -sSL https://github.com/salomepoulain/makery-bakery/releases/latest/download/install_bake.sh | bash'

WORKDIR /workspace
USER baker
ENV PATH="/home/baker/.local/bin:${PATH}"

CMD ["/usr/bin/zsh", "-l"]
