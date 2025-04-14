FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV LAVENDER_DIR=/usr/share/lav_engine
ENV PATH="$LAVENDER_DIR/tools:$PATH"

WORKDIR /usr/share/lav_game

ENTRYPOINT ["sh", "-c"]
CMD ["gcc", "--version"]
