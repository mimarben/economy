# economy
Domestic Economy

# App to save data of every month about home's incomes and expenses 

Flask back end


Angular FrontEnd

Generar los modelos de datos desde models.py para interfaces de angular.

datamodel-codegen --input api/schemas/UserBase_schema.json --input-file-type jsonschema --output api/models --output-model-type pydantic.BaseModel

datamodel-codegen --input /home/miguel/src/economy/api/utils/api/schemas/UserBase_schema.json --input-file-type jsonschema --output /home/miguel/src/economy/api/models/user.ts --output-model-type pydantic.BaseModel

npm install -g json-schema-to-typescript


json2ts -i /home/miguel/src/economy/api/utils/api/schemas/UserBase_schema.json -o user.ts
