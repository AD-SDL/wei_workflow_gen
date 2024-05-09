import os
import yaml
import chromadb
import json
class DB:
    def __init__(self, directory_path='workflows'):
        root_path = os.path.dirname(os.path.abspath(__file__))
        self.client = chromadb.EphemeralClient()
        try:
            self.client.get_collection("workflow-collection")
            self.client.delete_collection("workflow-collection")
        except:
            print("Creating collection")
        self.collection = self.client.create_collection("workflow-collection")
        workflows_dir = os.path.join(root_path, directory_path)
        self._load_workflows(workflows_dir)

    def _load_workflows(self, workflows_dir):
        for filename in os.listdir(workflows_dir):
            if filename.endswith('.yaml'):
                file_path = os.path.join(workflows_dir, filename)
                with open(file_path, 'r') as file:
                    workflow_yaml = yaml.safe_load(file)
                    info = workflow_yaml.get('metadata').get('info')
                    document_string = yaml.dump(workflow_yaml, sort_keys=False)
                    self.collection.add(
                        documents=[document_string],
                        metadatas=[{"experiment_info": info}],  
                        ids=[filename[:-5]]  
                    )

    def query(self, query_text, n_results=2):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
