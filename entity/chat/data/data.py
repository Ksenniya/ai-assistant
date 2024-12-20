from common.config.config import MAX_ITERATION, RANDOM_AI_API

ENTITY_WORKFLOW = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "class_name": {
            "type": "string",
            "enum": ["com.cyoda.tdb.model.treenode.TreeNodeEntity"]
        },
        "transitions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "start_state": {
                        "type": "string"
                    },
                    "start_state_description": {
                        "type": "string"
                    },
                    "end_state": {
                        "type": "string"
                    },
                    "end_state_description": {
                        "type": "string"
                    },
                    "criteria": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "name",
                            "description"
                        ]
                    },
                    "process": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            },
                            "adds_new_entites": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "name",
                            "description",
                            "adds_new_entites"
                        ]
                    }
                },
                "required": [
                    "name",
                    "description",
                    "start_state",
                    "start_state_description",
                    "end_state",
                    "end_state_description",
                    "criteria",
                    "process"
                ]
            }
        }
    },
    "required": [
        "name",
        "class_name",
        "transitions"
    ]
}

ENTITIES_DESIGN = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "entity_name": {
                "type": "string"
            },
            "entity_type": {
                "type": "string",
                "enum": ["JOB", "EXTERNAL_SOURCES_PULL_BASED_RAW_DATA", "WEB_SCRAPING_PULL_BASED_RAW_DATA",
                         "TRANSACTIONAL_PULL_BASED_RAW_DATA", "EXTERNAL_SOURCES_PUSH_BASED_RAW_DATA",
                         "WEB_SCRAPING_PUSH_BASED_RAW_DATA", "TRANSACTIONAL_PUSH_BASED_RAW_DATA", "SECONDARY_DATA",
                         "UTIL", "CONFIG", "BUSINESS_ENTITY"]
            },
            "entity_source": {
                "type": "string",
                "enum": ["API_REQUEST", "SCHEDULED", "ENTITY_EVENT"]
            },
            "depends_on_entity": {
                "type": "string"
            },
            "entity_workflow": ENTITY_WORKFLOW
        },
        "required": [
            "entity_name",
            "entity_type",
            "entity_source",
            "depends_on_entity",
            "entity_workflow"
        ]
    }
}

# Finished
app_building_stack = [{"question": "Finished",
                       "prompt": None,
                       "answer": None,
                       "function": None,
                       "index": 2,
                       "iteration": 0,
                       "max_iteration": 0},
                      # add_design_stack
                      {"question": None,
                       "prompt": None,
                       "answer": None,
                       "function": {"name": "add_design_stack",
                                    "prompt": {
                                        "text": "Return the final version of Cyoda design, which was approved by user. Do not add anything else.",
                                        "schema": {
                                            "$schema": "http://json-schema.org/draft-07/schema#",
                                            "title": "Cyoda design",
                                            "type": "object",
                                            "properties": {
                                                "entities": ENTITIES_DESIGN
                                            },
                                            "required": [
                                                "entities"
                                            ]
                                        }
                                    }},
                       "iteration": 0,
                       "max_iteration": 0},
                      # please wait
                      {"notification": "Generating Cyoda design: please wait",
                       "prompt": "",
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "max_iteration": 0
                       },
                      # Improve the Cyoda design based on the user answer if the user wants any improvements
                      {"question": None,
                       "prompt": {
                           "text": "Improve the Cyoda design based on the user answer if the user wants any improvements",
                           "function": {"name": "save_design_stack"},
                           "schema": {
                               "$schema": "http://json-schema.org/draft-07/schema#",
                               "title": "Improved Cyoda design",
                               "type": "object",
                               "properties": {
                                   "can_proceed": {
                                       "type": "boolean",
                                       "description": "Return false if the user had any suggestions to improve the design and you need the user to validate the new design.  Return false if this is the first time the user was asked this question and needs to be asked to validate your design - maybe the user can contribute to your design. Return true if the user explicitly approves your design."
                                   },
                                   "entities": ENTITIES_DESIGN
                               },
                               "required": [
                                   "can_proceed",
                                   "entities"
                               ]
                           }
                       },
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "max_iteration": MAX_ITERATION},
                      # Would you like to change anything in the design?
                      {"question": "Would you like to change anything in the design?",
                       "prompt": None,
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "max_iteration": 0},
                      # Generate Cyoda design, based on the requirement
                      {"question": None,
                       "prompt": {
                           "text": "Generate Cyoda design, based on the requirement. Do not forget to explicitly add the entities that you add in the workflow processors, and use only lowercase underscore for namings. Add workflow only where necessary. If the entity is saved in the workflow of another entity (e.g. JOB) then its source will be ENTITY_EVENT.",
                           "function": {"name": "save_design_stack"},
                           "schema": {
                               "$schema": "http://json-schema.org/draft-07/schema#",
                               "title": "Cyoda design",
                               "type": "object",
                               "properties": {
                                   "entities": ENTITIES_DESIGN
                               },
                               "required": [
                                   "entities"
                               ]
                           }
                       },
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "max_iteration": 0},
                      # please wait
                      {"notification": "Generating Cyoda design: please wait",
                       "prompt": "",
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "max_iteration": 0},
                      # Is this requirement sufficient?
                      {"question": None,
                       "prompt": {
                           "text": "Is this requirement sufficient?",
                           "function": {"name": "save_design_stack"},
                           "schema": {
                               "$schema": "http://json-schema.org/draft-07/schema#",
                               "title": "Answer schema",
                               "type": "object",
                               "properties": {
                                   "can_proceed": {
                                       "type": "boolean",
                                       "description": "Return true if this requirement is sufficient. Return false if you have more questions to ask"
                                   },
                                   "questions_to_answer": {
                                       "type": "array",
                                       "items": {
                                           "type": "string",
                                           "description": "Add questions about the requirement if you have any. Leave empty if the requirement is sufficient or if the human doesn't want to specify any more details."
                                       }
                                   }
                               },
                               "required": [
                                   "can_proceed",
                                   "questions_to_answer"
                               ]
                           }
                       },
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "max_iteration": MAX_ITERATION},
                      # What application would you like to build
                      {
                          "question": "Hello! What application would you like to build? Could you, please, share your ideas?",
                          "prompt": None,
                          "answer": None,
                          "function": None,
                          "iteration": 0,
                          "max_iteration": 0},
                      # add_instruction
                      {"question": None,
                       "prompt": None,
                       "answer": None,
                       "function": {"name": "add_instruction"},
                       "iteration": 0,
                       "max_iteration": 0},
                      # init_chats
                      {"question": None,
                       "prompt": None,
                       "answer": None,
                       "function": {"name": "init_chats"},
                       "iteration": 0,
                       "max_iteration": 0},
                      # clone_repo
                      {"question": None,
                       "prompt": None,
                       "answer": None,
                       "function": {"name": "clone_repo"},
                       "iteration": 0,
                       "max_iteration": 0}
                      ]
# save_entity_to_file
entity_stack = lambda entity: [{"notification": "Generating Cyoda design: please wait",
                                "prompt": "",
                                "answer": None,
                                "function": None,
                                "iteration": 0,
                                "max_iteration": 0
                                },
                               # Improve the entity model
                               {"question": None,
                                "prompt": {
                                    "text": f"Improve the data model for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
                                    "function": {"name": "save_entity_to_file"},
                                    "schema": {
                                        "$schema": "http://json-schema.org/draft-07/schema#",
                                        "title": "Improved Entity entity",
                                        "type": "object",
                                        "properties": {
                                            "can_proceed": {
                                                "type": "boolean",
                                                "description": "Return true if the user liked your entity design and is ok to proceed to the next step. Return false if the user asked for any improvements - you incorporated them and now need validation from the user."
                                            },
                                            "entity": {
                                                "type": "object",
                                                "properties": {},
                                                "required": []
                                            }
                                        },
                                        "required": [
                                            "can_proceed",
                                            "entity"
                                        ]
                                    }
                                },
                                "answer": None,
                                "function": None,
                                "entity": entity,
                                "index": 0,
                                "iteration": 0,
                                "max_iteration": MAX_ITERATION},
                               # Would you like to edit the model
                               {"question": "Would you like to edit the model?",
                                "prompt": None,
                                "answer": None,
                                "function": None,
                                "index": 0,
                                "iteration": 0,
                                "max_iteration": 0},
                               # Generate entity entity (entity example json) based on the user input
                               {"question": None,
                                "prompt": {
                                    "text": f"Generate example data json (data model) for entity {entity.get("entity_name")}. This is not related to entity schema and should be random sample data that reflects the purpose of the entity or the data that is specified by the user. Base your answer on the user input if any: ",
                                    "function": {"name": "save_entity_to_file"},
                                    "schema": {
                                        "$schema": "http://json-schema.org/draft-07/schema#",
                                        "title": "Entity entity",
                                        "type": "object",
                                        "properties": {
                                            "entity": {
                                                "type": "object",
                                                "description": "json object that represents entity entity example"
                                            }
                                        },
                                        "required": [
                                            "entity"
                                        ]
                                    }
                                },
                                "answer": None,
                                "function": None,
                                "entity": entity,
                                "index": 0,
                                "iteration": 0,
                                "max_iteration": 0},
                               # Would you like to specify the entity
                               {
                                   "question": f"Let's generate the entity schema. Would you like to specify the data for entity: {entity}",
                                   "prompt": None,
                                   "answer": None,
                                   "function": None,
                                   "index": 0,
                                   "iteration": 0,
                                   "max_iteration": 0},
                               ]
# save_processors_code_to_file
workflow_stack = lambda entity: [{"notification": "Generating Cyoda design: please wait",
                                  "prompt": "",
                                  "answer": None,
                                  "function": None,
                                  "iteration": 0,
                                  "max_iteration": 0
                                  },
                                 # ========================================================================================================
                                 {"question": None,
                                  "prompt": {
                                      "text": f"Improve the workflow for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
                                      "function": {"name": "export_workflow"},
                                      "schema": {
                                          "$schema": "http://json-schema.org/draft-07/schema#",
                                          "title": "Improved workflow design",
                                          "type": "object",
                                          "properties": {
                                              "can_proceed": {
                                                  "type": "boolean"
                                              },
                                              "entity_workflow": ENTITY_WORKFLOW
                                          },
                                          "required": [
                                              "can_proceed",
                                              "entity_workflow"
                                          ]
                                      }
                                  },
                                  "answer": None,
                                  "function": None,
                                  "entity": entity,
                                  "index": 0,
                                  "iteration": 0,
                                  "max_iteration": MAX_ITERATION},
                                 # Would you like to add any changes to entity workflow
                                 {"question": f"Would you like to add any changes to entity workflow {entity}",
                                  "prompt": None,
                                  "answer": None,
                                  "function": None,
                                  "index": 0,
                                  "iteration": 0,
                                  "max_iteration": 0}]

processors_stack = lambda entity: [{"notification": "Generating Cyoda design: please wait",
                                    "prompt": "",
                                    "answer": None,
                                    "function": None,
                                    "iteration": 0,
                                    "max_iteration": 0
                                    },
                                   {"question": None,
                                    "prompt": {
                                        "text": f"Improve the functions code for {entity.get("entity_name")}  based on the user suggestions if there are any, if not you can proceed. User says: ",
                                        "function": {"name": "save_processors_code_to_file"},
                                        "schema": {
                                            "$schema": "http://json-schema.org/draft-07/schema#",
                                            "title": "Improved functions code",
                                            "type": "object",
                                            "properties": {
                                                "can_proceed": {
                                                    "type": "boolean",
                                                    "description": "Return false if the user asked for any improvements - you need to incorporate them and validate with the user first. Return true if user explicitly identifies they are happy with the code and you can proceed to the next step."
                                                },
                                                "code": {
                                                    "type": "string",

                                                }
                                            },
                                            "required": [
                                                "can_proceed",
                                                "code"
                                            ]
                                        }
                                    },
                                    "answer": None,
                                    "function": None,
                                    "entity": entity,
                                    "index": 0,
                                    "iteration": 0,
                                    "max_iteration": MAX_ITERATION},
                                   # Would you like to edit the model
                                   {"question": "Would you like to edit the code?",
                                    "prompt": None,
                                    "answer": None,
                                    "function": None,
                                    "index": 0,
                                    "iteration": 0,
                                    "max_iteration": 0},
                                   # Generate the processor functions
                                   {"question": None,
                                    "prompt": {
                                        "function": {"name": "save_processors_code_to_file"},
                                        "text": f"Generate the processor functions for {entity.get('entity_name')} "
                                                f"with the processors in each transition: "
                                                f"{', '.join([transition.get('process', {}).get('name', '') for transition in entity.get('entity_workflow', {}).get('transitions', [])])}. "
                                                f" For each processor in each transition, generate the processor logic. "
                                                f" Make sure you include logic to save any dependant entities and use all the supplementary code from the context $code ."
                                                f" Also generate tests with mocks for external services or functions so that the user can try out the functions right away in isolated environment."
                                                f"{entity.get('entity_name')}. Based on the user suggestions if there are any. "
                                                f" User says: ",
                                        "schema": {
                                            "$schema": "http://json-schema.org/draft-07/schema#",
                                            "title": "Processors functions",
                                            "type": "object",

                                            "properties": {
                                                "code": {
                                                    "type": "string",

                                                }
                                            },
                                            "required": [
                                                "code"
                                            ]
                                        }
                                    },
                                    "answer": None,
                                    "function": None,
                                    "entity": entity,
                                    "index": 0,
                                    "iteration": 0,
                                    "context": {"code": ["code"]},
                                    "max_iteration": MAX_ITERATION
                                    },
                                   # Would you like to specify any details for generating processors
                                   {
                                       "question": "Would you like to specify any details for generating processors functions?",
                                       "prompt": None,
                                       "answer": None,
                                       "function": None,
                                       "index": 0,
                                       "iteration": 0,
                                       "max_iteration": 0}
                                   ]

scheduler_stack = lambda entity: [{"notification": "Generating Cyoda design: please wait",
                                   "prompt": "",
                                   "answer": None,
                                   "function": None,
                                   "iteration": 0,
                                   "max_iteration": 0
                                   },
                                  # ========================================================================================================
                                  {"question": None,
                                   "prompt": {
                                       "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
                                       "function": {"name": "save_logic_code_to_file"},
                                       "schema": {
                                           "$schema": "http://json-schema.org/draft-07/schema#",
                                           "title": "Improved code",
                                           "type": "object",
                                           "properties": {
                                               "can_proceed": {
                                                   "type": "boolean",
                                                   "description": "Return false if the user asked for any improvements - you need to incorporate them and validate with the user first. Return true if user explicitly identifies they are satisfied with the code and you can proceed to the next step."
                                               },
                                               "code": {
                                                   "type": "string",
                                               }
                                           },
                                           "required": [
                                               "can_proceed",
                                               "code"
                                           ]
                                       }
                                   },
                                   "answer": None,
                                   "function": None,
                                   "entity": entity,
                                   "index": 0,
                                   "iteration": 0,
                                   "max_iteration": MAX_ITERATION},
                                  # Would you like to edit the model
                                  {"question": "Would you like to edit the code?",
                                   "prompt": None,
                                   "answer": None,
                                   "function": None,
                                   "index": 0,
                                   "iteration": 0,
                                   "max_iteration": 0},
                                  # ========================================================================================================
                                  # Generate the processor functions
                                  {"question": None,
                                   "prompt": {
                                       "text": f"Generate the scheduler file for {entity.get("entity_name")}  based on the user suggestions if there are any, if not you can proceed. This function should save a job entity with data model $data to cyoda. Besides, it should not do any logic. Also generate tests with mocks for external services or functions so that the user can try out the functions right away in isolated environment. User says: ",
                                       "function": {"name": "save_logic_code_to_file"},
                                       "schema": {
                                           "$schema": "http://json-schema.org/draft-07/schema#",
                                           "title": "Processors functions",
                                           "type": "object",
                                           "properties": {
                                               "code": {
                                                   "type": "string",
                                               }
                                           },
                                           "required": [
                                               "code"
                                           ]
                                       }
                                   },
                                   "answer": None,
                                   "function": None,
                                   "entity": entity,
                                   "index": 0,
                                   "iteration": 0,
                                   "context": {"data": [entity.get("entity_name"), "data"]},
                                   "max_iteration": MAX_ITERATION
                                   },
                                  {
                                      "question": f"Let's generate the logic to schedule saving the entity {entity.get("entity_name")}. Would you like to specify any details?",
                                      "prompt": None,
                                      "answer": None,
                                      "function": None,
                                      "index": 0,
                                      "iteration": 0,
                                      "max_iteration": 0}
                                  ]

form_submission_stack = lambda entity: [{"notification": "Generating Cyoda design: please wait",
                                         "prompt": "",
                                         "answer": None,
                                         "function": None,
                                         "iteration": 0,
                                         "max_iteration": 0
                                         },
                                        # ========================================================================================================
                                        {"question": None,
                                         "prompt": {
                                             "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
                                             "function": {"name": "save_logic_code_to_file"},
                                             "schema": {
                                                 "$schema": "http://json-schema.org/draft-07/schema#",
                                                 "title": "Improved code",
                                                 "type": "object",
                                                 "properties": {
                                                     "can_proceed": {
                                                         "type": "boolean",
                                                         "description": "Return false if the user asked for any improvements - you need to incorporate them and validate with the user first. Return true if user explicitly identifies they are satisfied with the code and you can proceed to the next step."
                                                     },
                                                     "code": {
                                                         "type": "string",

                                                     }
                                                 },
                                                 "required": [
                                                     "can_proceed",
                                                     "code"
                                                 ]
                                             }
                                         },
                                         "answer": None,
                                         "function": None,
                                         "entity": entity,
                                         "index": 0,
                                         "iteration": 0,
                                         "max_iteration": MAX_ITERATION},
                                        # Would you like to edit the model
                                        {"question": "Would you like to edit the code?",
                                         "prompt": None,
                                         "answer": None,
                                         "function": None,
                                         "index": 0,
                                         "iteration": 0,
                                         "max_iteration": 0},
                                        # ========================================================================================================
                                        # Generate the processor functions
                                        {"question": None,
                                         "prompt": {
                                             "text": f"Generate the logic file to process the form application and saving the entity {entity.get("entity_name")}  based on the user suggestions if there are any, if not you can proceed. Also generate tests with mocks for external services or functions so that the user can try out the functions right away in isolated environment. User says: ",
                                             "function": {"name": "save_logic_code_to_file"},
                                             "schema": {
                                                 "$schema": "http://json-schema.org/draft-07/schema#",
                                                 "title": "Processors functions",
                                                 "type": "object",
                                                 "properties": {
                                                     "code": {
                                                         "type": "string",
                                                     }
                                                 },
                                                 "required": [
                                                     "code"
                                                 ]
                                             }
                                         },
                                         "answer": None,
                                         "function": None,
                                         "entity": entity,
                                         "index": 0,
                                         "iteration": 0,
                                         "context": {"data": [entity.get("entity_name"), "data"]},
                                         "max_iteration": MAX_ITERATION
                                         },
                                        {
                                            "question": f"Let's generate the logic to process the form application and saving the entity {entity.get("entity_name")} with the form entity. Would you like to specify any details?",
                                            "prompt": None,
                                            "answer": None,
                                            "function": None,
                                            "index": 0,
                                            "iteration": 0,
                                            "max_iteration": 0}
                                        ]

file_upload_stack = lambda entity: [{"notification": "Generating Cyoda design: please wait",
                                     "prompt": "",
                                     "answer": None,
                                     "function": None,
                                     "iteration": 0,
                                     "max_iteration": 0
                                     },
                                    # ========================================================================================================
                                    {"question": None,
                                     "prompt": {
                                         "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
                                         "function": {"name": "save_logic_code_to_file"},
                                         "schema": {
                                             "$schema": "http://json-schema.org/draft-07/schema#",
                                             "title": "Improved code",
                                             "type": "object",
                                             "properties": {
                                                 "can_proceed": {
                                                     "type": "boolean",
                                                     "description": "Return false if the user asked for any improvements - you need to incorporate them and validate with the user first. Return true if user explicitly identifies they are satisfied with the code and you can proceed to the next step."
                                                 },
                                                 "code": {
                                                     "type": "string",

                                                 }
                                             },
                                             "required": [
                                                 "can_proceed",
                                                 "code"
                                             ]
                                         }
                                     },
                                     "answer": None,
                                     "function": None,
                                     "entity": entity,
                                     "index": 0,
                                     "iteration": 0,
                                     "max_iteration": MAX_ITERATION},
                                    # Would you like to edit the model
                                    {"question": "Would you like to edit the code?",
                                     "prompt": None,
                                     "answer": None,
                                     "function": None,
                                     "index": 0,
                                     "iteration": 0,
                                     "max_iteration": 0},
                                    # ========================================================================================================
                                    # Generate the processor functions
                                    {"question": None,
                                     "prompt": {
                                         "text": f"Generate the logic file to upload the file and saving the entity {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. Also generate tests with mocks for external services or functions so that the user can try out the functions right away in isolated environment. User says: ",
                                         "function": {"name": "save_logic_code_to_file"},
                                         "schema": {
                                             "$schema": "http://json-schema.org/draft-07/schema#",
                                             "title": "Processors functions",
                                             "type": "object",
                                             "properties": {
                                                 "code": {
                                                     "type": "string",

                                                 }
                                             },
                                             "required": [
                                                 "code"
                                             ]
                                         }
                                     },
                                     "answer": None,
                                     "function": None,
                                     "entity": entity,
                                     "index": 0,
                                     "iteration": 0,
                                     "context": {"data": [entity.get("entity_name"), "data"]},
                                     "max_iteration": MAX_ITERATION
                                     },
                                    {
                                        "question": f"Let's generate the logic to upload the file and saving the entity {entity.get("entity_name")} based on the file contents. Would you like to specify any details?",
                                        "prompt": None,
                                        "answer": None,
                                        "function": None,
                                        "index": 0,
                                        "iteration": 0,
                                        "max_iteration": 0}
                                    ]

api_request_stack = lambda entity: [{"notification": "Generating Cyoda design: please wait",
                                     "prompt": "",
                                     "answer": None,
                                     "function": None,
                                     "iteration": 0,
                                     "max_iteration": 0
                                     },
                                    # ========================================================================================================
                                    {"question": None,
                                     "prompt": {
                                         "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
                                         "function": {"name": "save_logic_code_to_file"},
                                         "schema": {
                                             "$schema": "http://json-schema.org/draft-07/schema#",
                                             "title": "Improved code",
                                             "type": "object",
                                             "properties": {
                                                 "can_proceed": {
                                                     "type": "boolean",
                                                     "description": "Return false if the user asked for any improvements - you need to incorporate them and validate with the user first. Return true if user explicitly identifies they are satisfied with the code and you can proceed to the next step."
                                                 },
                                                 "code": {
                                                     "type": "string",

                                                 }
                                             },
                                             "required": [
                                                 "can_proceed",
                                                 "code"
                                             ]
                                         }
                                     },
                                     "answer": None,
                                     "function": None,
                                     "entity": entity,
                                     "index": 0,
                                     "iteration": 0,
                                     "max_iteration": MAX_ITERATION},
                                    # Would you like to edit the model
                                    {"question": "Would you like to edit the code?",
                                     "prompt": None,
                                     "answer": None,
                                     "function": None,
                                     "index": 0,
                                     "iteration": 0,
                                     "max_iteration": 0},
                                    # ========================================================================================================
                                    # Generate the processor functions
                                    {"question": None,
                                     "prompt": {
                                         "text": f"Generate the api file to save the entity {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. Also generate tests with mocks for external services or functions so that the user can try out the functions right away in isolated environment. User says: ",
                                         "function": {"name": "save_logic_code_to_file"},
                                         "schema": {
                                             "$schema": "http://json-schema.org/draft-07/schema#",
                                             "title": "Processors functions",
                                             "type": "object",
                                             "properties": {
                                                 "code": {
                                                     "type": "string",

                                                 }
                                             },
                                             "required": [
                                                 "code"
                                             ]
                                         }
                                     },
                                     "answer": None,
                                     "function": None,
                                     "entity": entity,
                                     "index": 0,
                                     "iteration": 0,
                                     "context": {"data": [entity.get("entity_name"), "data"]},
                                     "max_iteration": MAX_ITERATION
                                     },
                                    {
                                        "question": f"Let's generate the api for processing entity and saving the entity {entity.get("entity_name")}. Would you like to specify any details?",
                                        "prompt": None,
                                        "answer": None,
                                        "function": None,
                                        "index": 0,
                                        "iteration": 0,
                                        "max_iteration": 0}
                                    ]

external_datasource_stack = lambda entity: [{"question": None,
                                             "prompt": None,
                                             "answer": None,
                                             "entity": entity,
                                             "function": {"name": "save_raw_data_to_entity_file"},
                                             "iteration": 0,
                                             "max_iteration": 0},
                                            {"question": f"Please specify the schema for {entity.get("entity_name")}.",
                                             "prompt": None,
                                             "answer": None,
                                             "function": None,
                                             "iteration": 0,
                                             "max_iteration": 0},
                                            # please wait
                                            {"notification": "Generating Cyoda design: please wait",
                                             "prompt": "",
                                             "answer": None,
                                             "function": None,
                                             "iteration": 0,
                                             "max_iteration": 0
                                             },
                                            {"question": None,
                                             "prompt": {
                                                 "text": f"Generate python code to get data from this external data source. The code should contain functions for each of the specified endpoints. Each function takes request parameters as input parameters and returns raw data as a response. Call the public function ingest_data(...). Provide a main method to test the ingest_data. After you return the result ask the user for validation.",
                                                 "api": RANDOM_AI_API,
                                                 "function": {"name": "save_connections_code_to_file"},
                                                 "schema": {
                                                     "$schema": "http://json-schema.org/draft-07/schema#",
                                                     "title": "External data source configuration code",
                                                     "type": "object",
                                                     "properties": {
                                                         "can_proceed": {
                                                             "type": "boolean",
                                                             "description": "Return false if this is the first time the user was asked this question and needs to be asked to validate your design - maybe the user can contribute to your design. Return true if the user explicitly approves your design."
                                                         },
                                                         "code": {
                                                             "type": "string",

                                                         }
                                                     },
                                                     "required": [
                                                         "can_proceed",
                                                         "code"
                                                     ]
                                                 }
                                             },
                                             "answer": None,
                                             "function": None,
                                             "entity": entity,
                                             "index": 0,
                                             "iteration": 0,
                                             "max_iteration": MAX_ITERATION
                                             },
                                            {"question": None,
                                             "prompt": {
                                                 "text": f"Generate the summary of the connection details specified by the user. After you return the result ask the user for validation.",
                                                 "api": RANDOM_AI_API,
                                                 "schema": {
                                                     "$schema": "http://json-schema.org/draft-07/schema#",
                                                     "title": "Summary of the connection details",
                                                     "type": "object",
                                                     "properties": {
                                                         "can_proceed": {
                                                             "type": "boolean",
                                                             "description": "Return false if this is the first time the user was asked this question and needs to be asked to validate your design - maybe the user can contribute to your design. Return true if the user explicitly approves your design."
                                                         },
                                                         "summary": {
                                                             "type": "string",

                                                         }
                                                     },
                                                     "required": [
                                                         "can_proceed",
                                                         "summary"
                                                     ]
                                                 }
                                             },
                                             "answer": None,
                                             "function": None,
                                             "entity": entity,
                                             "index": 0,
                                             "iteration": 0,
                                             "max_iteration": MAX_ITERATION
                                             },
                                            {
                                                "question": f"Let's set up a connection to ingest data from an external source. Could you please provide the configuration details? You can either share a link to the relevant API documentation (e.g., Swagger or OpenAPI) or offer instructions for configuring the connection. If applicable, please include any additional details such as specific endpoints, default parameters, or other relevant information.",
                                                "prompt": None,
                                                "answer": None,
                                                "function": None,
                                                "index": 0,
                                                "iteration": 0,
                                                "max_iteration": 0}

                                            ]
