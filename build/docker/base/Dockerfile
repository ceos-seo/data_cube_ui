FROM jcrattzama/datacube-core:1.8.3

ARG WORKDIR="/app"
WORKDIR $WORKDIR

# Install system dependencies.
COPY build/native/sys_deps/install_apache_deps.sh \
     build/native/sys_deps/install_apache_deps.sh
RUN build/native/sys_deps/install_apache_deps.sh
COPY build/native/sys_deps/install_dbs.sh \
     build/native/sys_deps/install_dbs.sh
RUN build/native/sys_deps/install_dbs.sh
COPY build/native/sys_deps/install_img_deps.sh \
     build/native/sys_deps/install_img_deps.sh
RUN build/native/sys_deps/install_img_deps.sh

# Install Python Dependencies. #
COPY build/native/python_deps/install_core_python_deps.sh \
     build/native/python_deps/install_core_python_deps.sh
COPY requirements_core.txt requirements_core.txt
RUN build/native/python_deps/install_core_python_deps.sh
COPY build/native/python_deps/install_python_deps.sh \
     build/native/python_deps/install_python_deps.sh
COPY requirements.txt requirements.txt
RUN build/native/python_deps/install_python_deps.sh

# End Install Python Dependencies #

# (prod) Create a directory to store files for the UI (notably task outputs).
# COPY build/native/mk_ui_tmp_dir.sh build/native/mk_ui_tmp_dir.sh
# RUN build/native/mk_ui_tmp_dir.sh

# (Optional) Install postfix and mailutils.
# ARG ADMIN_EMAIL=""
# ENV ADMIN_EMAIL=${ADMIN_EMAIL}
# Credit to https://serverfault.com/a/144010/367947 and
#           https://serverfault.com/a/143982/367947.
#RUN debconf-set-selections << "postfix postfix/mailname string your.hostname.com" && \
#    debconf-set-selections << "postfix postfix/main_mailer_type string 'Internet Site'"
#RUN DEBIAN_FRONTEND=noninteractive apt-get install -y postfix mailutils
# RUN cat "\
# myhostname = ${ADMIN_EMAIL}\n\
# mailbox_size_limit = 0\n\
# recipient_delimiter = +\n\
# inet_interfaces = localhost" > /etc/postfix/main.cf && \
#     service postfix restart

# Enable a login shell for the Apache user (allows `su www-data`).
RUN chsh -s /bin/bash www-data

# Sleep to keep the container from exiting so we can `exec` it.
CMD ["tail", "-f", "/dev/null"]
