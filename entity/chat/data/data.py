from common.config.config import MAX_ITERATION

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
                "enum": ["RAW_DATA", "DERIVED_DATA", "JOB"]
            },
            "entity_entry_point": {
                "type": "string",
                "enum": ["SCHEDULER", "API_REQUEST", "FORM_SUBMISSION", "FILE_UPLOAD", "EXTERNAL_DATA_SOURCE",
                         "ENTITY_UPDATE", "JOB"]
            },
            "depends_on_entity": {
                "type": "string"
            },
            "entity_workflow": ENTITY_WORKFLOW
        },
        "required": [
            "entity_name",
            "entity_type",
            "entity_entry_point",
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
                           "text": "Return the final version of Cyoda design",
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
              "text": "Generate Cyoda design, based on the requirement. Do not forget to explicitly add the entities that you add in the workflow processors, and use only lowercase underscore for namings.",
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
         {"question": "Hello! What application would you like to build? Could you, please, share your ideas?",
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
entity_stack = lambda entity: [{"question": None,
                                "prompt": None,
                                "answer": None,
                                "entity": entity,
                                "function": {"name": "save_entity_to_file",
                                             "prompt": {
                                                 "text": f"Return final entity for the {entity.get("entity_name")}. Return only json.",
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
                                                 },
                                                 "iteration": 0,
                                                 "max_iteration": 0}
                                             }
                                },
                               # please wait
                               {"notification": "Generating Cyoda design: please wait",
                                "prompt": "",
                                "answer": None,
                                "function": None,
                                "iteration": 0,
                                "max_iteration": 0
                                },
                               # Improve the entity model
                               {"question": None,
                                "prompt": {
                                    "text": f"Improve the entity model for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
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
                                    "text": f"Generate entity entity (entity example json) for entity {entity.get("entity_name")} based on the user input if any: ",
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
workflow_stack = lambda entity: [{"question": None,
                                  "prompt": None,
                                  "answer": None,
                                  "entity": entity,
                                  "function": {"name": "save_processors_code_to_file",
                                               "prompt": {
                                                   "text": f"Return final processors code for the {entity.get("entity_name")}. Return only code.",
                                                   "schema": {
                                                       "$schema": "http://json-schema.org/draft-07/schema#",
                                                       "title": "Entity entity",
                                                       "type": "object",
                                                       "properties": {
                                                           "code": {
                                                               "type": "string",
                                                               "description": "formatted text that represents processors code"
                                                           }
                                                       },
                                                       "required": [
                                                           "code"
                                                       ]
                                                   },
                                                   "iteration": 0,
                                                   "max_iteration": 0}
                                               },
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
                                      "text": f"Improve the functions code for {entity.get("entity_name")}  based on the user suggestions if there are any, if not you can proceed. User says: ",
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
                                      "text": f"Generate the processor functions for {entity.get("entity_name")} {entity.get("entity_workflow", {}).get("transitions")}. (!!Make sure you include logic for working with all other entities which depend on {entity.get("entity_name")})  based on the user suggestions if there are any. User says: ",
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
                                  "index": 0,
                                  "iteration": 0,
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
                                     "max_iteration": 0},
                                 # export_workflow
                                 {"question": None,
                                  "prompt": None,
                                  "answer": None,
                                  "entity": entity,
                                  "function": {"name": "export_workflow",
                                               "prompt": {
                                                   "text": f"Return the workflow final workflow json for the {entity.get("entity_name")}. Return only json.",
                                                   "schema": {
                                                       "$schema": "http://json-schema.org/draft-07/schema#",
                                                       "title": "Re-generate workflow based on the user input",
                                                       "type": "object",
                                                       "properties": {
                                                           "entity_workflow": ENTITY_WORKFLOW
                                                       },
                                                       "required": [
                                                           "entity_workflow"
                                                       ]
                                                   },
                                                   "iteration": 0,
                                                   "max_iteration": 0}
                                               },
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
                                 # ========================================================================================================
                                 {"question": None,
                                  "prompt": {
                                      "text": f"Improve the workflow for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
                                      "schema": {
                                          "$schema": "http://json-schema.org/draft-07/schema#",
                                          "title": "Improved functions code",
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
                                  "index": 0,
                                  "iteration": 0,
                                  "max_iteration": MAX_ITERATION},
                                 # Would you like to edit the model
                                 {"question": "Would you like to edit the workflow?",
                                  "prompt": None,
                                  "answer": None,
                                  "function": None,
                                  "index": 0,
                                  "iteration": 0,
                                  "max_iteration": 0},
                                 # ========================================================================================================
                                 # Re-generate workflow based on the user input
                                 {"question": None,
                                  "prompt": {
                                      "text": f"Re-generate workflow for {entity.get("entity_name")} based on the user input if any. If user doesn't have any suggestions return the existing workflow and set proceed to true. User input: ",
                                      "schema": {
                                          "$schema": "http://json-schema.org/draft-07/schema#",
                                          "title": "Re-generate workflow based on the user input",
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

scheduler_stack = lambda entity: [{"question": None,
                                   "prompt": None,
                                   "answer": None,
                                   "entity": entity,
                                   "function": {"name": "save_logic_code_to_file",
                                                "prompt": {
                                                    "text": f"Return final scheduler code for the {entity.get("entity_name")}. Return only code.",
                                                    "schema": {
                                                        "$schema": "http://json-schema.org/draft-07/schema#",
                                                        "title": "Entity entity",
                                                        "type": "object",
                                                        "properties": {
                                                            "code": {
                                                                "type": "string",
                                                                "description": "formatted text that represents processors code"
                                                            }
                                                        },
                                                        "required": [
                                                            "code"
                                                        ]
                                                    },
                                                    "iteration": 0,
                                                    "max_iteration": 0}
                                                },
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
                                  # ========================================================================================================
                                  {"question": None,
                                   "prompt": {
                                       "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
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
                                       "text": f"Generate the scheduler file for {entity.get("entity_name")}  based on the user suggestions if there are any, if not you can proceed. User says: ",
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
                                   "index": 0,
                                   "iteration": 0,
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

form_submission_stack = lambda entity: [{"question": None,
                                         "prompt": None,
                                         "answer": None,
                                         "entity": entity,
                                         "function": {"name": "save_logic_code_to_file",
                                                      "prompt": {
                                                          "text": f"Return final form processing code for the {entity.get("entity_name")}. Return only code.",
                                                          "schema": {
                                                              "$schema": "http://json-schema.org/draft-07/schema#",
                                                              "title": "Entity entity",
                                                              "type": "object",
                                                              "properties": {
                                                                  "code": {
                                                                      "type": "string",
                                                                      "description": "formatted text that represents processors code"
                                                                  }
                                                              },
                                                              "required": [
                                                                  "code"
                                                              ]
                                                          },
                                                          "iteration": 0,
                                                          "max_iteration": 0}
                                                      },
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
                                        # ========================================================================================================
                                        {"question": None,
                                         "prompt": {
                                             "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
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
                                             "text": f"Generate the logic file to process the form application and saving the entity {entity.get("entity_name")}  based on the user suggestions if there are any, if not you can proceed. User says: ",
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
                                         "index": 0,
                                         "iteration": 0,
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

file_upload_stack = lambda entity: [{"question": None,
                                     "prompt": None,
                                     "answer": None,
                                     "entity": entity,
                                     "function": {"name": "save_logic_code_to_file",
                                                  "prompt": {
                                                      "text": f"Return final file processing code for the {entity.get("entity_name")}. Return only code.",
                                                      "schema": {
                                                          "$schema": "http://json-schema.org/draft-07/schema#",
                                                          "title": "Entity entity",
                                                          "type": "object",
                                                          "properties": {
                                                              "code": {
                                                                  "type": "string",
                                                                  "description": "formatted text that represents processors code"
                                                              }
                                                          },
                                                          "required": [
                                                              "code"
                                                          ]
                                                      },
                                                      "iteration": 0,
                                                      "max_iteration": 0}
                                                  },
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
                                    # ========================================================================================================
                                    {"question": None,
                                     "prompt": {
                                         "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
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
                                         "text": f"Generate the logic file to upload the file and saving the entity {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
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
                                     "index": 0,
                                     "iteration": 0,
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

api_request_stack = lambda entity: [{"question": None,
                                     "prompt": None,
                                     "answer": None,
                                     "entity": entity,
                                     "function": {"name": "save_logic_code_to_file",
                                                  "prompt": {
                                                      "text": f"Return final api code for the {entity.get("entity_name")}. Return only code.",
                                                      "schema": {
                                                          "$schema": "http://json-schema.org/draft-07/schema#",
                                                          "title": "Entity entity",
                                                          "type": "object",
                                                          "properties": {
                                                              "code": {
                                                                  "type": "string",
                                                                  "description": "formatted text that represents processors code"
                                                              }
                                                          },
                                                          "required": [
                                                              "code"
                                                          ]
                                                      },
                                                      "iteration": 0,
                                                      "max_iteration": 0}
                                                  },
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
                                    # ========================================================================================================
                                    {"question": None,
                                     "prompt": {
                                         "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
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
                                         "text": f"Generate the api file to upload the file and saving the entity {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
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
                                     "index": 0,
                                     "iteration": 0,
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
                                             "function": {"name": "save_logic_code_to_file",
                                                          "prompt": {
                                                              "text": f"Return final the entity ingestion code for the {entity.get("entity_name")}. Return only code.",
                                                              "schema": {
                                                                  "$schema": "http://json-schema.org/draft-07/schema#",
                                                                  "title": "Entity entity",
                                                                  "type": "object",
                                                                  "properties": {
                                                                      "code": {
                                                                          "type": "string",
                                                                          "description": "formatted text that represents processors code"
                                                                      }
                                                                  },
                                                                  "required": [
                                                                      "code"
                                                                  ]
                                                              },
                                                              "iteration": 0,
                                                              "max_iteration": 0}
                                                          },
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
                                            # ========================================================================================================
                                            {"question": None,
                                             "prompt": {
                                                 "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
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
                                                 "text": f"Generate the entity ingestion file to ingest entity from the external entity source and saving the entity {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
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
                                             "index": 0,
                                             "iteration": 0,
                                             "max_iteration": MAX_ITERATION
                                             },
                                            {
                                                "question": f"Let's generate the entity ingestion logic for ingesting and transforming the entity and saving the entity {entity.get("entity_name")}. Would you like to specify any details?",
                                                "prompt": None,
                                                "answer": None,
                                                "function": None,
                                                "index": 0,
                                                "iteration": 0,
                                                "max_iteration": 0}
                                            ]
