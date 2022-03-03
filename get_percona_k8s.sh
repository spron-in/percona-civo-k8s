k8s_api_url="http://137.184.230.26:5000"

# get k8s
cluster_id=`curl -s $k8s_api_url/create_k8s`

regexp="(.*Too Many Requests.*)"
if [[ $cluster_id =~ $regexp ]]; then
	echo "[ERROR] You can create one cluster per day. Exiting."
	exit 1
fi

echo "[INFO] Creating the cluster"

echo "[INFO] Waiting for cluster to be ready"
# get kube config
while :
do
	kubeconfig=`curl -s $k8s_api_url/get_k8s_config/$cluster_id`
	regexp="(.*Cluster is not ready yet.*)"
	if [[ $kubeconfig =~ $regexp ]]; then
		sleep 5
		continue
	else
		echo "[INFO] Cluster is ready"
		echo "[INFO] Copy kubeconfig below"
		sleep 1
		echo
		echo
		curl -s $k8s_api_url/get_k8s_config/$cluster_id
		break
	fi

done
