
import json
import subprocess
from pathlib import Path
from pydantic import BaseModel
from typing import Type

def schema_exporter(model: Type[BaseModel], generate_ts: bool = False):
    """Exporta el esquema JSON del modelo y genera el modelo TypeScript con json2ts."""
    schema = model.model_json_schema()
    file_name = f"{model.__name__}_schema.json"

    # Directorios de entrada y salida
    output_dir = Path(__file__).parent / 'api' / 'schemas'
    ts_output_dir = Path(__file__).parent / 'api' / 'models'

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        ts_output_dir.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        print(f"Warning: Could not create schema export directories: {e}")
        return

    json_path = output_dir / file_name
    ts_path = ts_output_dir / f"{model.__name__}.ts"

    # Guardar el JSON
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
    except (OSError, PermissionError) as e:
        print(f"Warning: Could not export schema for {model.__name__}: {e}")
        return

    #print(f"✔ Esquema exportado: {json_path}")

    # Ejecutar json2ts
    if generate_ts:
      try:
          result = subprocess.run([
              "json2ts",
              "-i", str(json_path),
              "-o", str(ts_path)
          ], capture_output=True, text=True)

          if result.returncode != 0:
              print("❌ Error ejecutando json2ts:")
              print("STDERR:", result.stderr)
      except Exception as e:
          print(f"Warning: Could not generate TypeScript for {model.__name__}: {e}")

    #print(f"✔ Modelo TypeScript generado: {ts_path}")
