FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the run.py file into the container
COPY run.py /app/

# Install git and SSH server
RUN apt-get update && \
    apt-get install -y git openssh-server && \
    mkdir /var/run/sshd && \
    echo 'root:password' | chpasswd && \
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Copy requirements under /app
COPY requirements.txt /app/

# Install Flask
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app directory contents into the container at /app
COPY app /app/app

# Copy the SSH public key into the container
COPY id_rsa.pub /root/.ssh/authorized_keys

# Expose SSH port
EXPOSE 22

# Expose Flask application port
EXPOSE 3000

# CMD instruction to start SSH server and Flask application
CMD ["/usr/sbin/sshd", "-D"]
