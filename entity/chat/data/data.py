from common.config.config import MAX_ITERATION, RANDOM_AI_API

DESIGN_PLEASE_WAIT = "⚙️ Generating your Cyoda design... please wait a moment! ⏳"

FILES_NOTIFICATIONS = {
    "raw_data": {"text": "😊 Could you please provide an example of the raw data? It would be super helpful! Thanks!",
                 "file_name": "entity/{entity_name}/connections/raw_data.json"},
    "code": {"text": "😊 Could you please provide details for the connection functions? It would really help clarify things! Thank you!",
             "file_name": "entity/{entity_name}/connections/connections.py"},
    "doc": {"text": "😊 Could you please provide more details for the connection documentation? It would be super helpful! Thanks so much!",
            "file_name": "entity/{entity_name}/connections/connections_input.md"},
    "entity": {
        "text": "😊 Could you please provide an example of the entity JSON? It will help us map the raw data to the entity or save the raw data as is. Thanks a lot!",
        "file_name": "entity/{entity_name}/{entity_name}.json"}
}

LOGIC_CODE_DESIGN_STR = "additional logic code design"

WORKFLOW_CODE_DESIGN_STR = "workflow code design"

WORKFLOW_DESIGN_STR = "workflow design"

ENTITIES_DESIGN_STR = "entities design"

APPLICATION_DESIGN_STR = "application design"

GATHERING_REQUIREMENTS_STR = "gathering requirements"

QUESTION_OR_VALIDATE = "Could you please help me review my output and approve it you are happy with the result 😸"

APP_BUILDER_FLOW = [
    {GATHERING_REQUIREMENTS_STR: "Let's collect all the necessary details."},
    {
        APPLICATION_DESIGN_STR: "Let's design the application using diagrams and chat. You'll receive a text document with the PRD as the output. Output documents: entity/app_design.json"},
    {ENTITIES_DESIGN_STR: "Let's define the JSON data structure for each entity."},
    {WORKFLOW_DESIGN_STR: "Let's ensure our entity workflow is correctly defined."},
    {WORKFLOW_CODE_DESIGN_STR: "Let's implement the workflow processors."},
    {LOGIC_CODE_DESIGN_STR: "Let's develop any additional business logic."}
]

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
                    # "criteria": {
                    #     "type": "object",
                    #     "properties": {
                    #         "name": {
                    #             "type": "string"
                    #         },
                    #         "description": {
                    #             "type": "string"
                    #         }
                    #     },
                    #     "required": [
                    #         "name",
                    #         "description"
                    #     ]
                    # },
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
                    "start_state",
                    "end_state",
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
                       "prompt": {},
                       "answer": None,
                       "function": None,
                       "index": 2,
                       "iteration": 0,
                       "max_iteration": 0},
                      # add_design_stack
                      {"question": None,
                       "prompt": {},
                       "answer": None,
                       "function": {"name": "add_design_stack"},
                       "file_name": "entity/app_design.json",
                       "flow_step": APPLICATION_DESIGN_STR,
                       "iteration": 0,
                       "fills_stack": True,
                       "max_iteration": 0},
                      {"question": None,
                       "prompt": {},
                       "answer": None,
                       "function": {"name": "add_user_requirement"},
                       "file_name": "entity/user_requirement.md",
                       "flow_step": APPLICATION_DESIGN_STR,
                       "iteration": 0,
                       "max_iteration": 0},
                      # please wait
                      {"notification": DESIGN_PLEASE_WAIT,
                       "prompt": {},
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "file_name": "entity/app_design.json",
                       "flow_step": APPLICATION_DESIGN_STR,
                       "max_iteration": 0
                       },
                      # Improve the Cyoda design based on the user answer if the user wants any improvements
                      {"question": None,
                       "prompt": {
                           "text": "Improve the Cyoda design based on the user answer if the user wants any improvements. Return Cyoda design json only",
                           "schema": {
                               "$schema": "http://json-schema.org/draft-07/schema#",
                               "title": "Improved Cyoda design",
                               "type": "object",
                               "properties": {
                                   "can_proceed": {
                                       "type": "boolean",
                                       "description": "Return false"},
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
                       "file_name": "entity/app_design.json",
                       "flow_step": APPLICATION_DESIGN_STR,
                       "iteration": 0,
                       "additional_questions": ["Would you like to improve anything in the design?"],
                       "max_iteration": MAX_ITERATION},
                      # Would you like to change anything in the design?
                      {"question": "😊 Would you like to make any changes to the design? Feel free to let me know!",
                       "prompt": {},
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "example_answers": [
                           "Could you please reduce the number of entities and use only absolutely necessary entities",
                           "Could you please orchestrate the flow with a JOB entity",
                           "Could you please add an entity for ...",
                           "Could you please remove an entity for ..."],
                       "file_name": "entity/app_design.json",
                       "flow_step": APPLICATION_DESIGN_STR,
                       "max_iteration": 0},
                      # Generate Cyoda design, based on the requirement
                      # {"question": None,
                      #  "prompt": {
                      #      "text": "Using Cyoda design json, return human readable prd document that explains the Cyoda design json and explains how it is aligned with the requirement. You not only need to translate the json, but explain what is Cyoda entity data base, how event driven approach works for the specific requirement - why we do what we do, as the user will be completely new to Cyoda.",
                      #  },
                      #  "answer": None,
                      #  "file_name": "entity/app_design_prd.md",
                      #  "flow_step": APPLICATION_DESIGN_STR,
                      #  "function": None,
                      #  "iteration": 0,
                      #  "max_iteration": 0},
                      {"question": None,
                       "prompt": {
                           "text": "Generate Cyoda design, based on the requirement. Do not forget to explicitly add the entities that you add in the workflow processors, and use only lowercase underscore for namings. Add workflow only where necessary. If the entity is saved in the workflow of another entity (e.g. JOB) then its source will be ENTITY_EVENT. Use minimal number of entities.",
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
                       "file_name": "entity/app_design.json",
                       "flow_step": APPLICATION_DESIGN_STR,
                       "function": None,
                       "iteration": 0,
                       "max_iteration": 0},
                      # please wait
                      {"notification": DESIGN_PLEASE_WAIT,
                       "prompt": {},
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "file_name": "entity/app_design.json",
                       "flow_step": GATHERING_REQUIREMENTS_STR,
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
                                       "description": "Return false"},
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
                       "ui_config": {
                           "display_keys": [{
                               "questions_to_answer": "😊 Could you please help me with these questions? If you're ready to move on to the next iteration or skip this one, just click 'Approve'! 👍 : "}],
                       },
                       "file_name": "entity/app_design.json",
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "additional_questions": [],
                       "max_iteration": MAX_ITERATION},
                      # What application would you like to build
                      {
                          "question": "💡 What kind of application would you like to build? I'd love to hear your ideas! Feel free to share them with me! 😊",
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "iteration": 0,
                          "file_name": "entity/app_design.json",
                          "flow_step": GATHERING_REQUIREMENTS_STR,
                          "example_answers": [
                              "Hello, I would like to download the following data: https://raw.githubusercontent.com/Cyoda-platform/cyoda-ai/refs/heads/ai-2.x/data/test-inputs/v1/connections/london_houses.csv, analyze it using pandas, and save a report.",
                              "Hello! I would like to develop an application that ingests data from a specified data source, aggregates the data, and saves it to a report. Afterward, the application should send the report to the admin's email. The data ingestion process should be scheduled to run once a day."],
                          "max_iteration": 0},
                      {
                          "notification": "🚀 Let's kick off our journey! 😊 I'm excited to get started! ))",
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "iteration": 0,
                          "file_name": "instruction.txt",
                          "flow_step": GATHERING_REQUIREMENTS_STR,
                          "max_iteration": 0
                      },

                      # add_instruction
                      {"question": None,
                       "prompt": {},
                       "answer": None,
                       "function": {"name": "add_instruction"},
                       "file_name": "instruction.txt",
                       "iteration": 0,
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "max_iteration": 0},

                      # init_chats
                      {"question": None,
                       "prompt": {},
                       "answer": None,
                       "function": {"name": "init_chats"},
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "iteration": 0,
                       "max_iteration": 0},
                      # clone_repo
                      {"question": None,
                       "prompt": {},
                       "answer": None,
                       "function": {"name": "clone_repo"},
                       "iteration": 0,
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "max_iteration": 0}
                      ]

data_ingestion_stack = lambda entities: [
    {
        "question": None,
        "prompt": {},
        "answer": None,
        "function": {"name": "generate_data_ingestion_code",
                     "prompts": [
                         {"EXTERNAL_SOURCES_PULL_BASED_RAW_DATA": {
                             "text": f"Generate python code to get data from this external data source. The code should contain functions for each of the specified endpoints. Each function takes request parameters as input parameters and returns raw data as a response. Call the public function ingest_data(...). Provide a main method to test the ingest_data.",
                             "api": RANDOM_AI_API,
                         }
                         },
                         {"WEB_SCRAPING_PULL_BASED_RAW_DATA": {
                             "text": f"Generate python code for a webscraper that collects data from this data source. Call the public function ingest_data(...). Provide a main method to test the ingest_data.",
                             "api": RANDOM_AI_API
                         }
                         },
                         {"TRANSACTIONAL_PULL_BASED_RAW_DATA": {
                             "text": f"Generate python code to get data from this external data source. The code should contain functions for each of the specified endpoints. Each function takes request parameters as input parameters and returns raw data as a response. Call the public function ingest_data(...). Provide a main method to test the ingest_data.",
                             "api": RANDOM_AI_API
                         }
                         }
                     ]
                     },
        "context": {
            "files": [],
        },
        "entities": entities,
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "max_iteration": MAX_ITERATION
    },
    {
        "question": f"🚀 Are you ready to start the bulk generation? Let me know when you're good to go! 😊",
        "prompt": {},
        "answer": None,
        "function": None,
        "index": 0,
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "files_notifications": FILES_NOTIFICATIONS,
        "max_iteration": 0},
    {
        "question": None,
        "prompt": {},
        "answer": None,
        "function": {"name": "check_entity_definitions"},
        "notification_text": "Please update the file contents for {file_name}",
        "files_notifications": FILES_NOTIFICATIONS,
        "context": {
            "files": [],
        },
        "entities": entities,
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "max_iteration": 0},
    {
        "question": f"😊 Could you please update the files with the necessary information? Once you're done, just click 'Approve' 👍. Thanks so much!",
        "prompt": {},
        "answer": None,
        "function": None,
        "index": 0,
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "max_iteration": 0},
    {
        "question": None,
        "prompt": {},
        "answer": None,
        "function": {"name": "generate_data_ingestion_entities_template"},
        "files_notifications": FILES_NOTIFICATIONS,
        "context": {
            "files": [],
        },
        "entities": entities,
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "max_iteration": 0},
    {
        "question": None,
        "prompt": {},
        "answer": None,
        "function": {"name": "refresh_context"},
        "context": {
            "files": [],
        },
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "max_iteration": 0},
]

entity_stack = lambda entity: [{"notification": DESIGN_PLEASE_WAIT,
                                "prompt": {},
                                "answer": None,
                                "function": None,
                                "iteration": 0,
                                "file_name": f"entity/{entity.get("entity_name")}/{entity.get("entity_name")}.json",
                                "flow_step": ENTITIES_DESIGN_STR,
                                "max_iteration": 0
                                },
                               # Improve the entity model
                               {"question": None,
                                "prompt": {
                                    "text": f"Improve the data model for {entity.get("entity_name")} based on the user suggestions if there are any. Return only json, any non json value will result in error, no comments required. **User requirement has the highest priority** If the user formulates data model themselves, just apply user input with correct formatting. User's requirement: ",

                                },
                                "answer": None,
                                "function": None,
                                "entity": entity,
                                "index": 0,
                                "iteration": 0,
                                "file_name": f"entity/{entity.get("entity_name")}/{entity.get("entity_name")}.json",
                                "flow_step": ENTITIES_DESIGN_STR,
                                "additional_questions": ["Would you like to improve the data model? "],
                                "max_iteration": MAX_ITERATION},
                               # Would you like to edit the model
                               {"question": "Would you like to edit the model?",
                                "prompt": {},
                                "answer": None,
                                "function": None,
                                "index": 0,
                                "iteration": 0,
                                "example_answers": ["Yes, I would like to edit the model",
                                                    "No, I would like to proceed with the current model"],
                                "file_name": f"entity/{entity.get("entity_name")}/{entity.get("entity_name")}.json",
                                "flow_step": ENTITIES_DESIGN_STR,
                                "max_iteration": 0},
                               # Generate example data json (data model)
                               {"question": None,
                                "prompt": {
                                    "text": f"Generate example data json (data model) for entity {entity.get("entity_name")}. This is NOT related to entity design and should be random sample data that can be mock data returned from a datasource or data that reflects business logic or the data that is specified by the user. Return only json, any non json value will result in error, no comments required. Base your answer on the user input if any: "
                                },
                                "answer": None,
                                "function": None,
                                "entity": entity,
                                "index": 0,
                                "iteration": 0,
                                "file_name": f"entity/{entity.get("entity_name")}/{entity.get("entity_name")}.json",
                                "flow_step": ENTITIES_DESIGN_STR,
                                "max_iteration": 0},
                               # Would you like to specify the entity
                               {
                                   "question": f"Let's generate the entity schema. Would you like to specify the data for entity: {entity}",
                                   "prompt": {},
                                   "answer": None,
                                   "function": None,
                                   "index": 0,
                                   "iteration": 0,
                                   "file_name": f"entity/{entity.get("entity_name")}/{entity.get("entity_name")}.json",
                                   "flow_step": ENTITIES_DESIGN_STR,
                                   "example_answers": ["Could you please take into account ...",
                                                       "What would you recommend?",
                                                       "I've already provided all the necessary details in the session context"],
                                   "max_iteration": 0},
                               {
                                   "question": None,
                                   "prompt": {},
                                   "answer": None,
                                   "function": {"name": "refresh_context"},
                                   "context": {
                                       "files": ["entity/**"],
                                       "excluded_files": ["entity/workflow.py", "entity/__init__.py"],
                                   },
                                   "iteration": 0,
                                   "flow_step": ENTITIES_DESIGN_STR,
                                   "max_iteration": 0},
                               ]

workflow_stack = lambda entity: [{"notification": DESIGN_PLEASE_WAIT,
                                  "prompt": {},
                                  "answer": None,
                                  "function": None,
                                  "iteration": 0,
                                  "max_iteration": 0,
                                  "flow_step": WORKFLOW_DESIGN_STR,
                                  "file_name": f"entity/{entity.get("entity_name")}/workflow/workflow.json",
                                  },
                                 # ========================================================================================================
                                 {"question": None,
                                  "prompt": {
                                      "text": f"Improve the workflow for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
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
                                  "file_name": f"entity/{entity.get("entity_name")}/workflow/workflow.json",
                                  "flow_step": WORKFLOW_DESIGN_STR,
                                  "additional_questions": ["Would you like to improve the workflow? "],
                                  "max_iteration": MAX_ITERATION},
                                 # Would you like to add any changes to entity workflow
                                 {
                                     "question": f"Would you like to add any changes to entity workflow: entity/{entity.get("entity_name")}/workflow/workflow.json",
                                     "prompt": {},
                                     "answer": None,
                                     "function": None,
                                     "index": 0,
                                     "iteration": 0,
                                     "file_name": f"entity/{entity.get("entity_name")}/workflow/workflow.json",
                                     "flow_step": WORKFLOW_DESIGN_STR,
                                     "max_iteration": 0},
                                 {"question": None,
                                  "prompt": {},
                                  "answer": None,
                                  "function": {"name": "generate_cyoda_workflow"},
                                  "file_name": f"entity/{entity.get("entity_name")}/workflow/workflow.json",
                                  "entity": entity,
                                  "iteration": 0,
                                  "flow_step": WORKFLOW_DESIGN_STR,
                                  "max_iteration": 0},
                                 {
                                     "question": None,
                                     "prompt": {},
                                     "answer": None,
                                     "function": {"name": "refresh_context"},
                                     "context": {
                                         "files": ["entity/app_design.json", "entity/user_requirement.md"],
                                     },
                                     "iteration": 0,
                                     "flow_step": WORKFLOW_DESIGN_STR,
                                     "max_iteration": 0}
                                 ]

processors_stack = lambda entity: [{"notification": DESIGN_PLEASE_WAIT,
                                    "prompt": {},
                                    "answer": None,
                                    "function": None,
                                    "iteration": 0,
                                    "max_iteration": 0,
                                    "flow_step": WORKFLOW_CODE_DESIGN_STR,
                                    "file_name": f"entity/{entity.get("entity_name")}/workflow/workflow.py"
                                    },
                                   # Would you like to edit the model
                                   # Generate the processor functions
                                   {"question": None,
                                    "prompt": {
                                        "text": f"Generate the processor functions for {entity.get('entity_name')} "
                                                f"call public functions by the name of each processor: "
                                                f"{', '.join([transition.get('process', {}).get('name', '') for transition in entity.get('entity_workflow', {}).get('transitions', [])])}. "
                                                f" Reuse functions that are available in the code base, including logic.app_init import entity_service, connections.py and any other existing function that is related to your purpose."
                                                f" Make sure you include logic to save any dependant entities: {', '.join([transition.get('process', {}).get('adds_new_entites', '') for transition in entity.get('entity_workflow', {}).get('transitions', [])])}."
                                                f" Also generate tests with mocks for external services or functions so that the user can try out the functions right away in isolated environment. **Tests should be in the same file with the code**"
                                                f"{entity.get('entity_name')}. Based on the user suggestions if there are any. "
                                                f" User says: ",
                                    },
                                    "answer": None,
                                    "function": None,
                                    "entity": entity,
                                    "index": 0,
                                    "iteration": 0,
                                    "file_name": f"entity/{entity.get("entity_name")}/workflow/workflow.py",
                                    "flow_step": WORKFLOW_CODE_DESIGN_STR,
                                    "additional_questions": [QUESTION_OR_VALIDATE],
                                    "max_iteration": MAX_ITERATION
                                    },
                                   # Would you like to specify any details for generating processors
                                   {
                                       "question": "Would you like to specify any details for generating processors functions?",
                                       "prompt": {},
                                       "answer": None,
                                       "function": None,
                                       "index": 0,
                                       "iteration": 0,
                                       "flow_step": WORKFLOW_CODE_DESIGN_STR,
                                       "example_answers": ["Could you please take into account ...",
                                                           "What would you recommend?",
                                                           "I've already provided all the necessary details in the session context"],
                                       "file_name": f"entity/{entity.get("entity_name")}/workflow/workflow.py",
                                       "max_iteration": 0},
                                   {
                                       "question": None,
                                       "prompt": {},
                                       "answer": None,
                                       "function": {"name": "refresh_context"},
                                       "context": {
                                           "files": ["common/service/entity_service_interface.py",
                                                     "common/service/trino_service.py",
                                                     "common/ai/ai_assistant_service.py",
                                                     "processor_instruction.txt", "entity/**"],
                                           "excluded_files": ["entity/workflow.py", "entity/__init__.py"],
                                       },
                                       "iteration": 0,
                                       "flow_step": WORKFLOW_CODE_DESIGN_STR,
                                       "max_iteration": 0},
                                   ]

scheduler_stack = lambda entity: [{"notification": DESIGN_PLEASE_WAIT,
                                   "prompt": {},
                                   "answer": None,
                                   "function": None,
                                   "iteration": 0,
                                   "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                   "flow_step": LOGIC_CODE_DESIGN_STR,
                                   "max_iteration": 0
                                   },
                                  # ========================================================================================================
                                  # {"question": None,
                                  #  "prompt": {
                                  #      "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",
                                  #  },
                                  #  "answer": None,
                                  #  "function": None,
                                  #  "entity": entity,
                                  #  "index": 0,
                                  #  "iteration": 0,
                                  #  "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                  #  "flow_step": LOGIC_CODE_DESIGN_STR,
                                  #  "additional_questions": [QUESTION_OR_VALIDATE],
                                  #  "max_iteration": MAX_ITERATION},
                                  # Would you like to edit the model
                                  # {"question": "Would you like to edit the code?",
                                  #  "prompt": {},
                                  #  "answer": None,
                                  #  "function": None,
                                  #  "index": 0,
                                  #  "iteration": 0,
                                  #  "example_answers": ["Yes, I'd like to change ...",
                                  #                      "No, I'd like to proceed with the current version"],
                                  #  "flow_step": LOGIC_CODE_DESIGN_STR,
                                  #  "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                  #  "max_iteration": 0},
                                  # ========================================================================================================
                                  # Generate the processor functions
                                  {"question": None,
                                   "prompt": {
                                       "text": f"Generate the scheduler file for {entity.get("entity_name")}  based on the user suggestions if there are any, if not you can proceed. This function should save a job entity with data model $data to cyoda. Besides, it should not do any logic. Also generate main function with entry point so that the user can do end-to-end test. User says: ",
                                   },
                                   "answer": None,
                                   "function": None,
                                   "entity": entity,
                                   "index": 0,
                                   "iteration": 0,
                                   "context": {"prompt": {"data": [entity.get("entity_name"), "data"]}},
                                   "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                   "flow_step": LOGIC_CODE_DESIGN_STR,
                                   "additional_questions": [QUESTION_OR_VALIDATE],
                                   "max_iteration": MAX_ITERATION
                                   },
                                  {
                                      "question": f"Let's generate the logic to schedule saving the entity {entity.get("entity_name")}. Would you like to specify any details?",
                                      "prompt": {},
                                      "answer": None,
                                      "function": None,
                                      "index": 0,
                                      "iteration": 0,
                                      "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                      "flow_step": LOGIC_CODE_DESIGN_STR,
                                      "example_answers": ["Could you please take into account ...",
                                                          "What would you recommend?",
                                                          "I've already provided all the necessary details in the session context"],
                                      "max_iteration": 0},
                                  {
                                      "question": None,
                                      "prompt": {},
                                      "answer": None,
                                      "function": {"name": "refresh_context"},
                                      "context": {
                                          "files": ["common/service/entity_service_interface.py",
                                                    "common/service/trino_service.py",
                                                    "common/ai/ai_assistant_service.py",
                                                    "logic_instruction.txt",
                                                    "entity/app_design.json",
                                                    "entity/user_requirement.md",
                                                    f"entity/{entity.get("entity_name")}/{entity.get("entity_name")}.json"],
                                      },
                                      "iteration": 0,
                                      "flow_step": LOGIC_CODE_DESIGN_STR,
                                      "max_iteration": 0},
                                  ]

form_submission_stack = lambda entity: [{"notification": DESIGN_PLEASE_WAIT,
                                         "prompt": {},
                                         "answer": None,
                                         "function": None,
                                         "iteration": 0,
                                         "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                         "flow_step": LOGIC_CODE_DESIGN_STR,
                                         "max_iteration": 0
                                         },
                                        # ========================================================================================================
                                        {"question": None,
                                         "prompt": {
                                             "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",

                                         },
                                         "answer": None,
                                         "function": None,
                                         "entity": entity,
                                         "index": 0,
                                         "iteration": 0,
                                         "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                         "flow_step": LOGIC_CODE_DESIGN_STR,
                                         "additional_questions": [QUESTION_OR_VALIDATE],
                                         "max_iteration": MAX_ITERATION},
                                        # Would you like to edit the model
                                        # {"question": "Would you like to edit the code?",
                                        #  "prompt": {},
                                        #  "answer": None,
                                        #  "function": None,
                                        #  "index": 0,
                                        #  "iteration": 0,
                                        #  "example_answers": ["Yes, I'd like to change ...",
                                        #                      "No, I'd like to proceed with the current version"],
                                        #  "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                        #  "flow_step": LOGIC_CODE_DESIGN_STR,
                                        #  "max_iteration": 0},
                                        # ========================================================================================================
                                        # Generate the processor functions
                                        {"question": None,
                                         "prompt": {
                                             "text": f"Generate the logic file to process the form application and saving the entity {entity.get("entity_name")}  based on the user suggestions if there are any, if not you can proceed. Also generate tests with mocks for external services or functions so that the user can try out the functions right away in isolated environment. **Tests should be in the same file with the code** User says: ",

                                         },
                                         "answer": None,
                                         "function": None,
                                         "entity": entity,
                                         "index": 0,
                                         "iteration": 0,
                                         "context": {"prompt": {"data": [entity.get("entity_name"), "data"]}},
                                         "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                         "flow_step": LOGIC_CODE_DESIGN_STR,
                                         "additional_questions": [QUESTION_OR_VALIDATE],
                                         "max_iteration": MAX_ITERATION
                                         },
                                        {
                                            "question": f"Let's generate the logic to process the form application and saving the entity {entity.get("entity_name")} with the form entity. Would you like to specify any details?",
                                            "prompt": {},
                                            "answer": None,
                                            "function": None,
                                            "index": 0,
                                            "iteration": 0,
                                            "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                            "flow_step": LOGIC_CODE_DESIGN_STR,
                                            "example_answers": ["Could you please take into account ...",
                                                                "What would you recommend?",
                                                                "I've already provided all the necessary details in the session context"],
                                            "max_iteration": 0},
                                        {
                                            "question": None,
                                            "prompt": {},
                                            "answer": None,
                                            "function": {"name": "refresh_context"},
                                            "context": {
                                                "files": ["common/service/entity_service_interface.py",
                                                          "common/service/trino_service.py",
                                                          "common/ai/ai_assistant_service.py",
                                                          "logic_instruction.txt",
                                                          "entity/app_design.json",
                                                          "entity/user_requirement.md"
                                                          f"entity/{entity.get("entity_name")}/{entity.get("entity_name")}.json"],
                                            },
                                            "iteration": 0,
                                            "flow_step": LOGIC_CODE_DESIGN_STR,
                                            "max_iteration": 0},
                                        ]

file_upload_stack = lambda entity: [{"notification": DESIGN_PLEASE_WAIT,
                                     "prompt": {},
                                     "answer": None,
                                     "function": None,
                                     "iteration": 0,
                                     "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                     "flow_step": LOGIC_CODE_DESIGN_STR,
                                     "max_iteration": 0
                                     },
                                    # ========================================================================================================
                                    {"question": None,
                                     "prompt": {
                                         "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",

                                     },
                                     "answer": None,
                                     "function": None,
                                     "entity": entity,
                                     "index": 0,
                                     "iteration": 0,
                                     "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                     "flow_step": LOGIC_CODE_DESIGN_STR,
                                     "additional_questions": [QUESTION_OR_VALIDATE],
                                     "max_iteration": MAX_ITERATION},
                                    # Would you like to edit the model
                                    # {"question": "Would you like to edit the code?",
                                    #  "prompt": {},
                                    #  "answer": None,
                                    #  "function": None,
                                    #  "index": 0,
                                    #  "iteration": 0,
                                    #  "example_answers": ["Yes, I'd like to change ...",
                                    #                      "No, I'd like to proceed with the current version"],
                                    #  "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                    #  "flow_step": LOGIC_CODE_DESIGN_STR,
                                    #  "max_iteration": 0},
                                    # ========================================================================================================
                                    # Generate the processor functions
                                    {"question": None,
                                     "prompt": {
                                         "text": f"Generate the logic file to upload the file and saving the entity {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. Also generate tests with mocks for external services or functions so that the user can try out the functions right away in isolated environment. **Tests should be in the same file with the code** User says: ",

                                     },
                                     "answer": None,
                                     "function": None,
                                     "entity": entity,
                                     "index": 0,
                                     "iteration": 0,
                                     "context": {"prompt": {"data": [entity.get("entity_name"), "data"]}},
                                     "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                     "flow_step": LOGIC_CODE_DESIGN_STR,
                                     "additional_questions": [QUESTION_OR_VALIDATE],
                                     "max_iteration": MAX_ITERATION
                                     },
                                    {
                                        "question": f"Let's generate the logic to upload the file and saving the entity {entity.get("entity_name")} based on the file contents. Would you like to specify any details?",
                                        "prompt": {},
                                        "answer": None,
                                        "function": None,
                                        "index": 0,
                                        "iteration": 0,
                                        "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                        "flow_step": LOGIC_CODE_DESIGN_STR,
                                        "example_answers": ["Could you please take into account ...",
                                                            "What would you recommend?",
                                                            "I've already provided all the necessary details in the session context"],
                                        "max_iteration": 0},
                                    {
                                        "question": None,
                                        "prompt": {},
                                        "answer": None,
                                        "function": {"name": "refresh_context"},
                                        "context": {
                                            "files": ["common/service/entity_service_interface.py",
                                                      "common/service/trino_service.py",
                                                      "common/ai/ai_assistant_service.py",
                                                      "logic_instruction.txt",
                                                      "entity/app_design.json",
                                                      "entity/user_requirement.md"
                                                      f"entity/{entity.get("entity_name")}/{entity.get("entity_name")}.json"],
                                        },
                                        "iteration": 0,
                                        "flow_step": LOGIC_CODE_DESIGN_STR,
                                        "max_iteration": 0},
                                    ]

api_request_stack = lambda entity: [{"notification": DESIGN_PLEASE_WAIT,
                                     "prompt": {},
                                     "answer": None,
                                     "function": None,
                                     "iteration": 0,
                                     "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                     "flow_step": LOGIC_CODE_DESIGN_STR,
                                     "max_iteration": 0
                                     },
                                    # ========================================================================================================
                                    {"question": None,
                                     "prompt": {
                                         "text": f"Improve the code for {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. User says: ",

                                     },
                                     "answer": None,
                                     "function": None,
                                     "entity": entity,
                                     "index": 0,
                                     "iteration": 0,
                                     "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                     "flow_step": LOGIC_CODE_DESIGN_STR,
                                     "additional_questions": [QUESTION_OR_VALIDATE],
                                     "max_iteration": MAX_ITERATION},
                                    # Would you like to edit the model
                                    # {"question": "Would you like to edit the code?",
                                    #  "prompt": {},
                                    #  "answer": None,
                                    #  "function": None,
                                    #  "index": 0,
                                    #  "iteration": 0,
                                    #  "example_answers": ["Yes, I'd like to change ...",
                                    #                      "No, I'd like to proceed with the current version"],
                                    #  "flow_step": LOGIC_CODE_DESIGN_STR,
                                    #  "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                    #  "max_iteration": 0},
                                    # ========================================================================================================
                                    # Generate the processor functions
                                    {"question": None,
                                     "prompt": {
                                         "text": f"Generate the api file to save the entity {entity.get("entity_name")} based on the user suggestions if there are any, if not you can proceed. Also generate tests with mocks for external services or functions so that the user can try out the functions right away in isolated environment. **Tests should be in the same file with the code** User says: ",
                                     },
                                     "answer": None,
                                     "function": None,
                                     "entity": entity,
                                     "index": 0,
                                     "iteration": 0,
                                     "context": {"prompt": {"data": [entity.get("entity_name"), "data"]}},
                                     "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                     "flow_step": LOGIC_CODE_DESIGN_STR,
                                     "additional_questions": [QUESTION_OR_VALIDATE],
                                     "max_iteration": MAX_ITERATION
                                     },
                                    {
                                        "question": f"Let's generate the api for processing entity and saving the entity {entity.get("entity_name")}. Would you like to specify any details?",
                                        "prompt": {},
                                        "answer": None,
                                        "function": None,
                                        "index": 0,
                                        "iteration": 0,
                                        "file_name": f"entity/{entity.get("entity_name")}/logic.py",
                                        "flow_step": LOGIC_CODE_DESIGN_STR,
                                        "example_answers": ["Could you please take into account ...",
                                                            "What would you recommend?",
                                                            "I've already provided all the necessary details in the session context"],
                                        "max_iteration": 0},
                                    {
                                        "question": None,
                                        "prompt": {},
                                        "answer": None,
                                        "function": {"name": "refresh_context"},
                                        "context": {
                                            "files": ["common/service/entity_service_interface.py",
                                                      "common/service/trino_service.py",
                                                      "common/ai/ai_assistant_service.py",
                                                      "logic_instruction.txt",
                                                      "entity/app_design.json",
                                                      "entity/user_requirement.md"
                                                      f"entity/{entity.get("entity_name")}/{entity.get("entity_name")}.json"],
                                        },
                                        "iteration": 0,
                                        "flow_step": LOGIC_CODE_DESIGN_STR,
                                        "max_iteration": 0},
                                    ]
