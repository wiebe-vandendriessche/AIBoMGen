### Example AIBoM
```json
{
    "components": [
        {
            "bom-ref": "training-environment@1.0",
            "description": "Details of the environment used for training",
            "name": "Training Environment",
            "properties": [
                {
                    "name": "CPU Count",
                    "value": "16"
                },
                {
                    "name": "Celery Queue",
                    "value": "training_queue"
                },
                {
                    "name": "Celery Task ID",
                    "value": "a088d42e-c592-479a-a5f0-f21e1e55e439"
                },
                {
                    "name": "Celery Task Name",
                    "value": "tasks.run_training"
                },
                {
                    "name": "Disk Usage (MB)",
                    "value": "1031018"
                },
                {
                    "name": "Docker Container ID",
                    "value": "b1a618aac343"
                },
                {
                    "name": "Docker Image ID",
                    "value": "sha256:a296d049f8ca5b07848c2e6a957a5fa186aa260269b2386aba47fef2b1ff5862"
                },
                {
                    "name": "Docker Image Name",
                    "value": "aibomgen-worker:latest"
                },
                {
                    "name": "GPU Memory Total (MB)",
                    "value": "6144"
                },
                {
                    "name": "GPU Memory Used (MB)",
                    "value": "5697"
                },
                {
                    "name": "GPU Name",
                    "value": "NVIDIA GeForce RTX 3060 Laptop GPU"
                },
                {
                    "name": "Job ID",
                    "value": "a088d42e-c592-479a-a5f0-f21e1e55e439"
                },
                {
                    "name": "Memory Total (MB)",
                    "value": "15922"
                },
                {
                    "name": "OS",
                    "value": "Linux 5.15.167.4-microsoft-standard-WSL2"
                },
                {
                    "name": "Python Version",
                    "value": "3.11.0rc1"
                },
                {
                    "name": "Request Time",
                    "value": "2025-05-05 14:35:18"
                },
                {
                    "name": "Start AIBoM Time",
                    "value": "2025-05-05 14:35:30"
                },
                {
                    "name": "Start Training Time",
                    "value": "2025-05-05 14:35:20"
                },
                {
                    "name": "TensorFlow Version",
                    "value": "2.16.1"
                },
                {
                    "name": "Training Time (seconds)",
                    "value": "9.258692264556885"
                },
                {
                    "name": "Unique Directory",
                    "value": "429cb678-e5d3-439c-8436-57e9e0e718f3"
                },
                {
                    "name": "Vulnerability Scan Error",
                    "value": "No vulnerability scan files found."
                }
            ],
            "type": "container"
        },
        {
            "bom-ref": "training-dataset@1.0",
            "description": "Dataset and dataset definition used for training",
            "hashes": [
                {
                    "alg": "SHA-256",
                    "content": "8d4e0f16706071c14d8a508299c9642df8dc92ab13b359d18beaf510938ee57f"
                },
                {
                    "alg": "SHA-256",
                    "content": "eb434d36856dd0489f8581a3bfa75965e39e86eceabeef62f1c720390c7a54d2"
                }
            ],
            "name": "Training Dataset",
            "properties": [
                {
                    "name": "Dataset Definition Hash",
                    "value": "eb434d36856dd0489f8581a3bfa75965e39e86eceabeef62f1c720390c7a54d2"
                },
                {
                    "name": "Dataset Hash",
                    "value": "8d4e0f16706071c14d8a508299c9642df8dc92ab13b359d18beaf510938ee57f"
                },
                {
                    "name": "Dataset MinIO Path",
                    "value": "429cb678-e5d3-439c-8436-57e9e0e718f3/dataset/image_dataset.zip"
                },
                {
                    "name": "Input Shape",
                    "value": "[64, 64, 3]"
                },
                {
                    "name": "Output Shape",
                    "value": "[3]"
                },
                {
                    "name": "Preprocessing",
                    "value": "{\n    \"normalize\": true\n}"
                }
            ],
            "type": "data"
        },
        {
            "bom-ref": "trained-model@1.0",
            "description": "a image classifier",
            "hashes": [
                {
                    "alg": "SHA-256",
                    "content": "9a716018bae617ab72757db2b3631e3f41e8874571d62622ee054fa009a57892"
                },
                {
                    "alg": "SHA-256",
                    "content": "f317d78e75bdc86f40ac0f12f42e32388e71242b46dfabaad83b6893bd84c4f8"
                }
            ],
            "name": "basic CNN",
            "properties": [
                {
                    "name": "Architecture Summary",
                    "value": "Name\tType\tShape\nconv2d\tConv2D\t(None, 62, 62, 32)\nmax_pooling2d\tMaxPooling2D\t(None, 31, 31, 32)\nconv2d_1\tConv2D\t(None, 29, 29, 64)\nmax_pooling2d_1\tMaxPooling2D\t(None, 14, 14, 64)\nflatten\tFlatten\t(None, 12544)\ndense\tDense\t(None, 128)\ndense_1\tDense\t(None, 3)"
                },
                {
                    "name": "Fit Param: batch_size",
                    "value": "32"
                },
                {
                    "name": "Fit Param: epochs",
                    "value": "30"
                },
                {
                    "name": "Fit Param: initial_epoch",
                    "value": "3"
                },
                {
                    "name": "Fit Param: steps_per_epoch",
                    "value": "Unknown"
                },
                {
                    "name": "Fit Param: validation_freq",
                    "value": "1"
                },
                {
                    "name": "Fit Param: validation_split",
                    "value": "0.3"
                },
                {
                    "name": "Fit Param: validation_steps",
                    "value": "Unknown"
                },
                {
                    "name": "Framework",
                    "value": "TensorFlow 2.16.1"
                },
                {
                    "name": "License",
                    "value": "Unknown"
                },
                {
                    "name": "Metric: accuracy",
                    "value": "[0.3392857015132904, 0.34375, 0.4285714328289032, 0.5714285969734192, 0.75, 0.8392857313156128, 0.9241071343421936, 0.9508928656578064, 0.9866071343421936, 0.9955357313156128, 0.9910714030265808, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]"
                },
                {
                    "name": "Metric: loss",
                    "value": "[272.05072021484375, 20.850217819213867, 1.1607776880264282, 0.9499340057373047, 0.6839848756790161, 0.4668533504009247, 0.3340912163257599, 0.19409121572971344, 0.12332673370838165, 0.07467357814311981, 0.05655582621693611, 0.028106870129704475, 0.022720875218510628, 0.013433614745736122, 0.008426054380834103, 0.0048513212241232395, 0.004452594555914402, 0.0028194859623908997, 0.002102575032040477, 0.0015230762073770165, 0.0012308150762692094, 0.0009765354334376752, 0.0007871970301494002, 0.0006555250729434192, 0.0005347729311324656, 0.00045605743071064353, 0.0003456018748693168]"
                },
                {
                    "name": "Metric: val_accuracy",
                    "value": "[0.34210526943206787, 0.3815789520740509, 0.5, 0.7236841917037964, 0.7894737124443054, 0.9342105388641357, 0.9736841917037964, 0.9868420958518982, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]"
                },
                {
                    "name": "Metric: val_loss",
                    "value": "[57.45112228393555, 1.680700659751892, 0.9799570441246033, 0.7485001683235168, 0.5788888931274414, 0.3842359483242035, 0.2155441790819168, 0.13610731065273285, 0.08210418373346329, 0.040581706911325455, 0.03989814221858978, 0.02649739198386669, 0.01596887595951557, 0.010236508212983608, 0.005263058468699455, 0.0059152934700250626, 0.0026273634284734726, 0.002331630326807499, 0.0017089401371777058, 0.0012887170305475593, 0.0011813017772510648, 0.0007893852889537811, 0.0008414497715421021, 0.0005072183557786047, 0.0005000683013349771, 0.00031583747477270663, 0.0003850734792649746]"
                },
                {
                    "name": "Metrics Hash",
                    "value": "f317d78e75bdc86f40ac0f12f42e32388e71242b46dfabaad83b6893bd84c4f8"
                },
                {
                    "name": "Optional Param: author",
                    "value": "Wiebe Vandendriessche"
                },
                {
                    "name": "Optional Param: framework",
                    "value": "TensorFlow 2.16.1"
                },
                {
                    "name": "Optional Param: license_name",
                    "value": "Unknown"
                },
                {
                    "name": "Optional Param: model_description",
                    "value": "a image classifier"
                },
                {
                    "name": "Optional Param: model_name",
                    "value": "basic CNN"
                },
                {
                    "name": "Optional Param: model_version",
                    "value": "version 1"
                },
                {
                    "name": "Trained Model Hash",
                    "value": "9a716018bae617ab72757db2b3631e3f41e8874571d62622ee054fa009a57892"
                }
            ],
            "type": "machine-learning-model",
            "version": "version 1"
        }
    ],
    "dependencies": [
        {
            "dependsOn": [
                "training-dataset@1.0",
                "training-environment@1.0"
            ],
            "ref": "trained-model@1.0"
        },
        {
            "ref": "training-dataset@1.0"
        },
        {
            "ref": "training-environment@1.0"
        }
    ],
    "externalReferences": [
        {
            "comment": "in-toto .link file for artifact integrity verification",
            "type": "attestation",
            "url": "429cb678-e5d3-439c-8436-57e9e0e718f3/output/run_training.8a98b077.link"
        }
    ],
    "metadata": {
        "authors": [
            {
                "email": "wiebe.vandendriessche@ugent.be",
                "name": "AIBoMGen by Wiebe Vandendriessche"
            }
        ],
        "manufacturer": {
            "name": "IDLab from Imec, Ghent University",
            "url": [
                "https://www.idlab.ugent.be"
            ]
        },
        "properties": [
            {
                "name": "BOM Signature",
                "value": "AVvAiMe3YSIi+x6PQpAKvgO6e5/lW0IPU87YUjmbkAX/f9T39XUyilCvblKMUYEcwmc+kJfIgyJbdyAilrXWBg=="
            }
        ],
        "supplier": {
            "name": "IDLab from Imec, Ghent University",
            "url": [
                "https://www.idlab.ugent.be"
            ]
        },
        "tools": {
            "components": [
                {
                    "description": "Python library for CycloneDX",
                    "externalReferences": [
                        {
                            "type": "build-system",
                            "url": "https://github.com/CycloneDX/cyclonedx-python-lib/actions"
                        },
                        {
                            "type": "distribution",
                            "url": "https://pypi.org/project/cyclonedx-python-lib/"
                        },
                        {
                            "type": "documentation",
                            "url": "https://cyclonedx-python-library.readthedocs.io/"
                        },
                        {
                            "type": "issue-tracker",
                            "url": "https://github.com/CycloneDX/cyclonedx-python-lib/issues"
                        },
                        {
                            "type": "license",
                            "url": "https://github.com/CycloneDX/cyclonedx-python-lib/blob/main/LICENSE"
                        },
                        {
                            "type": "release-notes",
                            "url": "https://github.com/CycloneDX/cyclonedx-python-lib/blob/main/CHANGELOG.md"
                        },
                        {
                            "type": "vcs",
                            "url": "https://github.com/CycloneDX/cyclonedx-python-lib"
                        },
                        {
                            "type": "website",
                            "url": "https://github.com/CycloneDX/cyclonedx-python-lib/#readme"
                        }
                    ],
                    "group": "CycloneDX",
                    "licenses": [
                        {
                            "license": {
                                "acknowledgement": "declared",
                                "id": "Apache-2.0"
                            }
                        }
                    ],
                    "name": "cyclonedx-python-lib",
                    "type": "library",
                    "version": "10.0.0"
                },
                {
                    "bom-ref": "aibomgen@0.1.0",
                    "description": "A platform for AI training and generating trusted AIBOMs",
                    "group": "IDLab from Imec and Ghent University",
                    "licenses": [
                        {
                            "license": {
                                "id": "MIT"
                            }
                        }
                    ],
                    "name": "AIBoMGen",
                    "supplier": {
                        "contact": [
                            {
                                "email": "wiebe.vandendriessche@ugent.be",
                                "name": "Wiebe Vandendriessche",
                                "phone": "+32 9 264 92 00"
                            }
                        ],
                        "name": "IDLab from Imec, Ghent University",
                        "url": [
                            "https://www.idlab.ugent.be"
                        ]
                    },
                    "type": "platform",
                    "version": "0.1.0"
                }
            ]
        }
    },
    "serialNumber": "urn:uuid:6d071d0b-f0fa-4f3d-b11c-76db0ec5a2f7",
    "version": 1,
    "$schema": "http://cyclonedx.org/schema/bom-1.6.schema.json",
    "bomFormat": "CycloneDX",
    "specVersion": "1.6"
}
```