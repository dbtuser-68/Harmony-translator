echo "Establishing proxy connection to connect to GCS"
set -e
gcloud config set proxy/type http
gcloud config set proxy/address proxy.wal-mart.com
gcloud config set proxy/port 9080



gcloud config set project $PROJECT_NAME
echo "Activating Service Account"

echo "Creds Location For Service Account: $GOOGLE_CREDENTIALS"

gcloud auth activate-service-account --key-file=$GOOGLE_CREDENTIALS

#gcloud artifacts repositories create flex --repository-format=docker --location=us-central1
gcloud dataflow flex-template build gs://sams-personalization-nba-dev-export-bucket/harmony/harmony_template.json --image-gcr-path "us-central1-docker.pkg.dev/sams-personalization-nba-dev/flex/harmony-docker:latest" --sdk-language "PYTHON" --flex-template-base-image "PYTHON3" --metadata-file "code/flex/metadata.json"  --gcs-log-dir="$GCS_BUILD_LOG_DIR" --subnetwork="$VPC_SUB_NETWORK" --disable-public-ips  --py-path "." --env "FLEX_TEMPLATE_PYTHON_PY_FILE=code/flex/harmony_translator_flex.py" --env "FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE=requirements.txt"
# sleep 120
# gcloud dataflow flex-template run "harmony-job-$(date +%Y%m%d-%H%M%S)" \
#   --template-file-gcs-location "gs://poc-sample-parquet/harmony.json" \
#   --region='us-central1' \
#   --subnetwork="$VPC_SUB_NETWORK" \
#   --parameters input_parquet_path="gs://poc-sample-parquet/input_file_ds/harmony_poc_input_file_ds_rye_reco_2024-06-22_part-000000000000_cid.parquet-00000-of-00001" \
#   --parameters output_parquet_path="gs://poc-sample-parquet/output_file/"

# WORKFLOW="harmony-workflow"
# WORKFLOW_YML_PATH="code/flex/test-workflow.yml"

# gcloud workflows deploy "${WORKFLOW}" --source="${WORKFLOW_YML_PATH}"

# input_parquet_path="gs://sams-personalization-nba-dev-export-bucket/harmony_poc/input_file_ds/*.parquet"
# output_parquet_path="gs://sams-personalization-nba-dev-export-bucket/harmony_poc/output_file/"
# #input_parquet_path="gs://sams-personalization-nba-dev-export-bucket/harmony_poc/input_file_ds/rye_reco_2024-06-22_part-000000000000_cid.parquet-00000-of-00001"
# #output_parquet_path="gs://sams-personalization-nba-dev-export-bucket/harmony_poc/output_file/output"

# gcloud workflows execute "${WORKFLOW}" --data='{"inputParquetPath":"'"$input_parquet_path"'","outputParquetPath":"'"$output_parquet_path"'"}'