### Example In-toto link file
```json
{
 "signatures": [
  {
   "keyid": "8a98b0773b596abdb6a3c5dc1afc620ee37a2cf5357ce90c9746fab2633162f0",
   "sig": "52321220f9b58f97549dc3dd9a78d40f416c6ffffab737d28788f550deb3a85da89c1fc94adfaefb5dc3cf7a5b238f2678c5858d091324ab1bdc7698c53b230a"
  }
 ],
 "signed": {
  "_type": "link",
  "byproducts": {
   "stdout": "Task completed successfully."
  },
  "command": [
   "python",
   "tasks.py",
   "run_training"
  ],
  "environment": {},
  "materials": {
   "429cb678-e5d3-439c-8436-57e9e0e718f3/dataset/image_dataset.zip": {
    "sha256": "8d4e0f16706071c14d8a508299c9642df8dc92ab13b359d18beaf510938ee57f"
   },
   "429cb678-e5d3-439c-8436-57e9e0e718f3/definition/image_definition.yaml": {
    "sha256": "eb434d36856dd0489f8581a3bfa75965e39e86eceabeef62f1c720390c7a54d2"
   },
   "429cb678-e5d3-439c-8436-57e9e0e718f3/model/image_model.keras": {
    "sha256": "1c6edfb52716cf675fa436df734d8521d0c46caecc145829c4aad7b99cd7983b"
   }
  },
  "name": "run_training",
  "products": {
   "429cb678-e5d3-439c-8436-57e9e0e718f3/output/metrics.json": {
    "sha256": "f317d78e75bdc86f40ac0f12f42e32388e71242b46dfabaad83b6893bd84c4f8"
   },
   "429cb678-e5d3-439c-8436-57e9e0e718f3/output/trained_model.keras": {
    "sha256": "9a716018bae617ab72757db2b3631e3f41e8874571d62622ee054fa009a57892"
   }
  }
 }
}
```