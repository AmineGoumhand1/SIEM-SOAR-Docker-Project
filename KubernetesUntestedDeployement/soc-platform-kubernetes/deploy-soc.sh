#!/bin/bash
# deploy-soc.sh

echo "Deploying SOC Platform..."

# Label nodes (adjust node names according to your cluster)
kubectl label nodes minikube role=siem --overwrite
kubectl label nodes minikube role=soar --overwrite

# Apply configurations in order
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-storage.yaml

# Wait for storage to be ready
sleep 10

# Deploy core databases and storage
kubectl apply -f 05-cassandra.yaml
kubectl apply -f 07-mysql.yaml
kubectl apply -f 06-minio.yaml
kubectl apply -f 08-redis.yaml
kubectl apply -f 02-elasticsearch.yaml

echo "Waiting for databases to be ready..."
kubectl wait --for=condition=ready pod -l app=cassandra -n soc-platform --timeout=300s
kubectl wait --for=condition=ready pod -l app=misp-mysql -n soc-platform --timeout=300s
kubectl wait --for=condition=ready pod -l app=elasticsearch -n soc-platform --timeout=300s

# Deploy SIEM components
kubectl apply -f 03-logstash.yaml
kubectl apply -f 04-kibana.yaml

# Deploy SOAR components
kubectl apply -f 09-misp.yaml
kubectl apply -f 10-cortex.yaml
kubectl apply -f 11-thehive.yaml
kubectl apply -f 12-misp-modules.yaml

echo "SOC Platform deployment completed!"
echo ""
echo "Access URLs:"
echo "  Kibana: http://<node-ip>:30601"
echo "  TheHive: http://<node-ip>:30090"
echo "  Cortex: http://<node-ip>:30091"
echo "  MISP: http://<node-ip>:30080"
echo "  MinIO Console: http://<node-ip>:30092"