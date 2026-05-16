import json
from pathlib import Path
from contexte.ir.models import ContextChunk, ContextDocument
from contexte.pack.manifest import PackManifest

def generate_schemas():
    output_dir = Path("docs/schemas")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    schemas = {
        "context-document.schema.json": ContextDocument.model_json_schema(),
        "context-chunk.schema.json": ContextChunk.model_json_schema(),
        "pack-manifest.schema.json": PackManifest.model_json_schema(),
    }
    
    for filename, schema in schemas.items():
        (output_dir / filename).write_text(json.dumps(schema, indent=2), encoding="utf-8")
        print(f"Generated {output_dir / filename}")

if __name__ == "__main__":
    generate_schemas()
