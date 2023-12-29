FROM ubuntu:22.10

ARG TIMEZONE=America/New_York
ARG PYTHON_VERSION=3.11.4


# tz
ENV TZ=${TIMEZONE}
RUN ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone


# install tools
RUN apt update -y \
    ;apt install -y nano

# install python build deps
RUN apt install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev git

# install chrome deps
RUN apt install -y libappindicator1 fonts-liberation


# install pyenv
ENV PYENV_ROOT=/usr/lib/pyenv
ENV PATH=${PYENV_ROOT}/bin:${PATH}
RUN git clone --depth 1 https://github.com/pyenv/pyenv.git ${PYENV_ROOT}


# install python
ENV PYTHON_PATH=${PYENV_ROOT}/versions/${PYTHON_VERSION}/bin
ENV PATH=${PYTHON_PATH}:${PATH}
RUN pyenv install ${PYTHON_VERSION} \
    ;pyenv global ${PYTHON_VERSION}


# install chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    ;dpkg -i google-chrome*.deb \
    ;apt -f install -y


# copy teams-ka
WORKDIR /usr/src/app

COPY __main__.py config.json holidays.json requirements.txt sched.json ./
COPY scripts/install_chrome_ubuntu.sh ./
COPY app ./app

RUN chmod +x install_chrome_ubuntu.sh;./install_chrome_ubuntu.sh
RUN pip install --no-cache-dir -r requirements.txt


# CMD [ "/bin/bash" ]


CMD [ "python", "." ]