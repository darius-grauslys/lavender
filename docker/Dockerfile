FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    build-essential \
    mingw-w64 \
    libglew-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-ttf-dev \
    libglm-dev \
    libcglm-dev \
    libgl1-mesa-dev \
    && rm -rf /var/lib/apt/lists/*

ENV LAVENDER_DIR=/usr/share/lav_engine
ENV PATH="$LAVENDER_DIR/tools:$PATH"

WORKDIR /usr/share/lav_game

ENTRYPOINT ["sh", "-c"]
CMD ["gcc", "--version"]
