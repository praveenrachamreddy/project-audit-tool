# Use Red Hat's Universal Base Image for Python on RHEL 8
FROM image-registry.openshift-image-registry.svc:5000/openshift/python:3.11-ubi9

# Set the working directory in the container
WORKDIR /app

# Set environment variables
# Note: For production, it's recommended to use OpenShift secrets to manage sensitive data like API keys.
ENV GEMINI_API_KEY="AIzaSyCFzvpJlFbKCl-AQv4clFh0b00YiVdGlaQ"
ENV MILVUS_HOST=milvus-grpc-praveen.apps.ocp4.imss.work
ENV MILVUS_PORT=443

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
# Running as root to install packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port that Streamlit runs on
EXPOSE 8501

# Create a non-root user and set permissions for OpenShift
# This is a security best practice and often required by cluster policies.
# RUN groupadd -r -g 1001 default && \
#     useradd -u 1001 -r -g default -d /app -s /sbin/nologin -c "Default User" default && \
#     chown -R 1001:1001 /app

# Switch to the non-root user to run the application
USER 1001

# Command to run the Streamlit app
CMD ["streamlit", "run", "frontend.py"]
