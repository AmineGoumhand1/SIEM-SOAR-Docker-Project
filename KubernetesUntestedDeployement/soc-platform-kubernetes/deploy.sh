#!/bin/bash

# Create the namespace
kubectl apply -f 00-namespace.yaml

# Create the secrets
kubectl apply -f 00-secrets.yaml

# Apply the manifests
kubectl apply -f 01-storage.yaml
kubectl apply -f 02-elasticsearch.yaml
kubectl apply -f 03-logstash.yaml
kubectl apply -f 04-kibana.yaml
kubectl apply -f 05-cassandra.yaml
kubectl apply -f 06-minio.yaml
kubectl apply -f 07-mysql.yaml
kubectl apply -f 08-redis.yaml
kubectl apply -f 09-misp.yaml
kubectl apply -f 10-cortex.yaml
kubectl apply -f 11-thehive.yaml
kubectl apply -f 12-misp-modules.yaml
kubectl apply -f 13-ingress.yaml
kubectl apply -f 14-network-policies.yaml
