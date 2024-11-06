import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions, StandardOptions
from apache_beam.io import ReadFromParquet, WriteToParquet
import pyarrow as pa
import json


class ProcessElement(beam.DoFn):
    default_values = {
        "ipi": 24.0,
        "lpq": 1.0,
        "tot_ord": 7,
        "id": "",
        "g1": 1.0,
        "pb1": 1.0,
        "qP": 1,
        "src": 1,
        "bvId": "",
        "ptc": "",
        "lpd": "",
        "b1": 1.0,
        "g2": 1.0,
        "ipi1": 16.75,
        "g3": 1.0
    }

    def generate_items(self, prod_id_list):
        items = []
        for prod_id in prod_id_list:
            item = {
                "ipi": self.default_values["ipi"],
                "lpq": self.default_values["lpq"],
                "tot_ord": self.default_values["tot_ord"],
                "id": self.default_values["id"],
                "g1": self.default_values["g1"],
                "pb1": self.default_values["pb1"],
                "qP": self.default_values["qP"],
                "p": prod_id,
                "src": self.default_values["src"],
                "bvId": self.default_values["bvId"],
                "ptc": self.default_values["ptc"],
                "lpd": self.default_values["lpd"],
                "b1": self.default_values["b1"],
                "g2": self.default_values["g2"],
                "ipi1": self.default_values["ipi1"],
                "g3": self.default_values["g3"]
            }
            items.append(item)
        return items

    def process(self, element):
        import random
        prod_id = element['prod_id']
        cid = random.randint(1, 1000000) 
        prod_id_list = prod_id.split(',')
        items = self.generate_items(prod_id_list)

        # Serialize items as JSON string
        items_json = json.dumps(items)

        data = {
            "pbs": 1,
            "ts": 1720602704,
            "id": str(cid),
            "ct": 3,
            "items": items_json  # Store items as JSON string
        }
        
        # Serialize the entire dictionary as a JSON string
        data_json = json.dumps(data)

        # Yield a dictionary with a single key 'data' and the JSON string as the value
        yield {"data": data_json}

# Define the custom pipeline options
class CustomPipelineOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument('--input_parquet_path', type=str, help='Path to the input Parquet files in GCS')
        parser.add_value_provider_argument('--output_parquet_path', type=str, help='Path to the output Parquet files in GCS')

# Define the pipeline options
pipeline_options = PipelineOptions(
    runner='DataflowRunner',
    num_workers=20, 
    worker_machine_type='n2-highmem-8',
    worker_disk_type='pd-ssd',
    worker_disk_size_gb=100,
    machine_type='n2-highmem-8',
    experiments=['nsx_cache_memory_usage_mb=512']
)

custom_options = pipeline_options.view_as(CustomPipelineOptions)

google_cloud_options = pipeline_options.view_as(GoogleCloudOptions)
google_cloud_options.project = 'sams-personalization-nba-dev'
google_cloud_options.job_name = 'parquet-to-json'
google_cloud_options.staging_location = 'gs://sams-personalization-nba-dev-export-bucket/harmony/staging'
google_cloud_options.temp_location = 'gs://sams-personalization-nba-dev-export-bucket/harmony/temp'
pipeline_options.view_as(StandardOptions).runner = 'DataflowRunner'
pipeline_options.view_as(GoogleCloudOptions).region = 'us-central1'


schema = pa.schema([
    ('data', pa.string())  # Single column named 'data' as a JSON string
])

# Create the pipeline
with beam.Pipeline(options=pipeline_options) as p:
    (
        p
        | 'Read from Parquet' >> ReadFromParquet(custom_options.input_parquet_path)
        | 'Process Elements' >> beam.ParDo(ProcessElement())
        | 'Write to Parquet' >> WriteToParquet(
            custom_options.output_parquet_path.get(),
            schema=schema,
            num_shards=1000,
            file_name_suffix='.parquet'
        )
    )