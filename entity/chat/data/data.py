from common.config.config import MAX_ITERATION, RANDOM_AI_API

DESIGN_PLEASE_WAIT = "⚙️ Generating your Cyoda design... please wait a moment! ⏳"
APPROVE_WARNING = "Sorry, you cannot skip this question. If you're unsure about anything, please refer to the example answers for guidance. If you need further help, just let us know! 😊 Apologies for the inconvenience!🙌"
OPERATION_FAILED_WARNING = "⚠️ Sorry, this action is not available right now. Please try again or wait for new questions ⚠️"

DESIGN_IN_PROGRESS_WARNING = "Sorry, you cannot submit answer right now. We are working on Cyoda design. Could you please wait  a little"
BRANCH_READY_NOTIFICATION = """🎉 **Your branch is ready!** Please update the project and check it out when you get a chance. 😊

To get started:

1. **Clone the repository** using the following command:  
   `git clone https://github.com/Cyoda-platform/quart-client-template/` 🚀

2. **Checkout your branch** using:  
   `git checkout {chat_id}` 🔄

You can access your branch directly on GitHub here: [Cyoda Platform GitHub](https://github.com/Cyoda-platform/quart-client-template/tree/{chat_id}) 😄

This repository is a **starter template** for your app and has two main modules:

- **Common Module**: This is all about integration with Cyoda! You don’t need to edit it unless you want to – it’s all done for you! 🎉  
- **Entity Module**: This is where your business logic and custom files will go. We'll add your files here, and you can track your progress. 📈 Feel free to **add or edit** anything in the Entity module. I’ll be pulling changes now and then, so just push your updates to let me know! 🚀

You can ask **questions in the chat** or in your project files anytime. When I make changes, I’ll let you know, and you can simply **pull** to sync with me! 🔄💬

Happy coding! 😄🎉"""

PUSHED_CHANGES_NOTIFICATION = """

🎉 **Changes have been pushed!** 🎉

I’ve submitted changes to the file: `{file_name}` in your branch. You can check it out by either:

1. **Pulling or fetching** the changes from the remote repository, or  
2. **Opening the link** to view the file directly: [View changes here]( {repository_url}/tree/{chat_id}/{file_name}) 🔗 (this will open in a new tab).

If you’re happy with the changes, feel free to **modify the file** if needed and click **Approve** so I can pull your updates. 👍

Also, you can use **Canvas** to discuss the changes with me anytime around the app-building flow! 🖌️💬

Let me know if you have any questions or suggestions! 😄"""
FILES_NOTIFICATIONS = {
    "code": {
        "text": "😊 Could you please provide details for the connection functions? It would really help clarify things! Thank you! You can paste all your data right here",
        "file_name": "entity/{entity_name}/connections/connections.py"},
    "doc": {
        "text": "😊 Could you please provide more details for the connection documentation? It would be super helpful! Please provide raw data for each endpoint if the final entity structure is different. You can paste all your data right here. Thanks so much!",
        "file_name": "entity/{entity_name}/connections/connections_input.md"},
    "entity": {
        "text": "😊 Could you please provide an example of the entity JSON? It will help us map the raw data to the entity or save the raw data as is. You can paste all your data right here. Thanks a lot!",
        "file_name": "entity/{entity_name}/{entity_name}.json"}
}

LOGIC_CODE_DESIGN_STR = "Additional logic code design"

WORKFLOW_CODE_DESIGN_STR = "Workflow processors code design"

WORKFLOW_DESIGN_STR = "Workflow design"

ENTITIES_DESIGN_STR = "Entities design"

APPLICATION_DESIGN_STR = "Application design"

GATHERING_REQUIREMENTS_STR = "Gathering requirements"

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
                       "file_name": "entity/chat.json",
                       "max_iteration": 0},
                      {"question": None,
                       "prompt": {},
                       "answer": None,
                       "function": {"name": "finish_flow"},
                       "index": 2,
                       "iteration": 0,
                       "file_name": "entity/chat.json",
                       "notification_text": """
🎉 **Chat flow has been saved!** 🎉

The chat flow has been successfully saved to `entity/chat.json`. Now you can run `app.py` to start the application. 🚀

Once you run it, both the **workflow** and **entities** will be imported to the Cyoda environment automatically. 🌟

Any updates or changes to the entities will trigger the workflow, so you’re all set to go! 🔄

We are available in the **Google Tech Channel** to support you. If you spot any bugs or need additional features, feel free to submit tickets at [GitHub Issues](https://github.com/Cyoda-platform/ai-assistant). You’re also most welcome to contribute to the project! 💻 

For any direct inquiries, reach out to **ksenia.lukonina@cyoda.com**. We’re here to help! 😊
                       """,
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
"additional_prompts": [
                           {
                               "text": """
Using updated Cyoda design json, update the PRD document. Return the updated PRD document only.
                             """,
                               "file_name": "entity/app_design_prd.md"
                           }
                       ],
                       "answer": None,
                       "function": None,
                       "file_name": "entity/app_design.json",
                       "flow_step": APPLICATION_DESIGN_STR,
                       "iteration": 0,
                       "additional_questions": [
                           {"question": "Would you like to improve anything in the design?  Give me thumbs up if you are ready to proceed 👍", "approve": True}],
                       "max_iteration": MAX_ITERATION},
                      # Would you like to change anything in the design?
                      {
                          "question": "😊 Would you like to make any changes to the design? Feel free to let me know! If you are happy with the design please approve 👍 to go to the next iteration",
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "iteration": 0,
                          "approve": True,
                          "example_answers": [
                              "Could you please reduce the number of entities and use only absolutely necessary entities",
                              "Could you please orchestrate the flow with a JOB entity",
                              "Could you please add an entity for ...",
                              "Could you please remove an entity for ..."],
                          "file_name": "entity/app_design.json",
                          "flow_step": APPLICATION_DESIGN_STR,
                          "max_iteration": 0},

                      {"notification": DESIGN_PLEASE_WAIT,
                       "prompt": {},
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "max_iteration": 0
                       },
                      {"question": None,
                       "prompt": {
                           "text": "Generate Cyoda design, based on the requirement. Do not forget to explicitly add the entities that you add in the workflow processors, and use only lowercase underscore for namings. Add workflow only where necessary. If the entity is saved in the workflow of another entity (e.g. JOB) then its source will be ENTITY_EVENT. If you have a JOB entity in the design - usually just one JOB entity is enough.",
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
                       "additional_prompts": [
                           {
                               "text": """
Using Cyoda design json, return human readable prd document that explains the Cyoda design json and explains how it is aligned with the requirement.
Also include markdown mermaid diagrams: sequenceDiagram, flowchart, classDiagram, stateDiagram, entities, graph, erDiagram, journey, mindmap, block-beta.
 Examples:
 ***For each not empty (has transitions) entity workflow let's provide a flowchart***
 ```mermaid
 flowchart TD
    A[Start State] -->|transition: transition_name_1, processor: processor_name_1, processor attributes: sync_process=true/false, new_transaction_for_async=true/false, none_transactional_for_async=true/false| B[State 1]
    B -->|transition: transition_name_2, processor: processor_name_2, processor attributes: sync_process=true/false, new_transaction_for_async=true/false, none_transactional_for_async=true/false| C[State 2]
    C --> D[End State]

    %% Decision point for criteria
    B -->|criteria: criteria_name, entityModelName equals some_value| D1{Decision: Check Criteria}
    D1 -->|true| C
    D1 -->|false| E[Error: Criteria not met]

    class A,B,C,D,D1 automated;
    ```
    ```mermaid
graph TD;
    A[data_ingestion_job] -->|triggers| B[raw_data_entity];
    B -->|transforms into| C[transformed_data_entity];
    C -->|enriches into| D[enriched_data_entity];
    D -->|aggregates into| E[aggregated_data_entity];
    E -->|generates| F[report_entity];
```
```mermaid
sequenceDiagram
    participant User
    participant Scheduler
    participant Data Ingestion Job
...

    User->>Scheduler: Schedule data ingestion job
    Scheduler->>Data Ingestion Job: Trigger scheduled data ingestion
...
``` 
                             """,
                               "file_name": "entity/app_design_prd.md"
                           }
                       ],
                       "answer": None,
                       "file_name": "entity/app_design.json",
                       "flow_step": APPLICATION_DESIGN_STR,
                       "function": None,
                       "iteration": 0,
                       "ui_config": {
                           "format": "json",
                       },
                       "max_iteration": 0},
                      {
                          "notification": """
**While we work on your app design, let me quickly introduce Cyoda...** 😄

**Simplify My Work-Life! 😅**

Most databases only store and retrieve data, but if I want to do more, I need many other tools. More tools = more complexity! 😬 I prefer simpler systems with fewer parts that fit together. But as tech improves, systems get harder to connect. 😕

I love creating things that work quickly. So, how can we simplify? 🤔 Systems really only do three things:
1. Take in information 📨
2. Change, delete, or create info 🔄
3. Make info accessible 🔍

But we need **information**—not just data! 📚

Most systems need a database. But let’s go beyond storage and process data too. Think of it as a "smart" database that does more! 😎

**Entities Make It Easier!**  
We don’t think in tables or numbers—we think in real-world things! 🤔 A database should focus on **entities**—things that have a start, middle, and end, like orders or payments. These entities change over time and follow rules, like a workflow. ⏳

**Why Entity State Machines are Great!**  
Viewing data as "entities" makes it easier to understand and use. It’s like mapping out real-life processes. 🔄 And you can change things without breaking the system. 💪

**The Entity Database (EDBMS)**  
An EDBMS keeps everything simple by managing processes and rules inside the database. It’s like having a smart assistant for your business. 😎 Great for industries like healthcare, manufacturing, or customer management, where data and processes are tightly linked.

Let’s build better, simpler systems! 🚀

For more on entity databases, check out this article by [Paul Schleger](https://medium.com/@paul_42036/whats-an-entity-database-11f8538b631a).
""",
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "iteration": 0,
                          "info": True,
                          "file_name": "entity/app_design.json",
                          "flow_step": APPLICATION_DESIGN_STR,
                          "max_iteration": 0
                      },
                      # Is this requirement sufficient?
                      {"question": None,
                       "prompt": {
                           "text": "Is the requirement clear and sufficient for creating the Cyoda design? At this stage, you do not need API documentation for data ingestion (if applicable), nor do you need to include implementation details. Focus on gathering only the minimum information needed to outline entities and their workflows. Avoid unnecessary details. If you have any questions or uncertainties about the requirement, please list them. If the requirement is sufficient or no further details are required - just let the user know you are ready to proceed. You do need to return design json at this iteration. Please return your response in markdown format. Your response should not contain Cyoda Design JSON! It will break the conversation. Just validate the requirement. User says: "
                       },
                       "file_name": "entity/app_design.json",
                       "answer": None,
                       "function": None,
                       "iteration": 0,
                       "flow_step": GATHERING_REQUIREMENTS_STR,
                       "additional_questions": [],
                       "max_iteration": MAX_ITERATION},
                      {
                          "question": "💡 What kind of application would you like to build? I'd love to hear your ideas! Feel free to share them with me! 😊",
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "iteration": 0,
                          "file_name": "entity/app_design.json",
                          "flow_step": GATHERING_REQUIREMENTS_STR,
                          "approve": False,
                          "example_answers": [
                              """
                              Hello, I would like to download the following data: [London Houses Data](https://raw.githubusercontent.com/Cyoda-platform/cyoda-ai/refs/heads/ai-2.x/data/test-inputs/v1/connections/london_houses.csv), analyze it using **pandas**, and save a report. 📊""",
                              """
                              Hello! 👋
                              I would like to develop an application that:
                              1. Ingests data from a specified data source 📥
                              2. Aggregates the data 🧮
                              3. Saves the aggregated data to a report 📄
                              Once the report is generated, the application should send it to the admin's email 📧. 
                              Additionally, the data ingestion process should be scheduled to run **once a day** ⏰."""],
                          "max_iteration": 0},

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
                       "max_iteration": 0},
                      {
                          "notification": f"""
In this process, we will walk through each stage of building an application, from gathering initial requirements to designing, coding, and implementing the final logic.

The stages of the process are as follows:

{GATHERING_REQUIREMENTS_STR}: {APP_BUILDER_FLOW[0][GATHERING_REQUIREMENTS_STR]},

{APPLICATION_DESIGN_STR}: {APP_BUILDER_FLOW[1][APPLICATION_DESIGN_STR]},

{ENTITIES_DESIGN_STR}: {APP_BUILDER_FLOW[2][ENTITIES_DESIGN_STR]},

{WORKFLOW_DESIGN_STR}: {APP_BUILDER_FLOW[3][WORKFLOW_DESIGN_STR]}, 

{WORKFLOW_CODE_DESIGN_STR}: {APP_BUILDER_FLOW[4][WORKFLOW_CODE_DESIGN_STR]}, 

{LOGIC_CODE_DESIGN_STR}: {APP_BUILDER_FLOW[5][LOGIC_CODE_DESIGN_STR]}

***{GATHERING_REQUIREMENTS_STR}*** --> {APPLICATION_DESIGN_STR} --> {ENTITIES_DESIGN_STR} --> {WORKFLOW_DESIGN_STR} --> {WORKFLOW_CODE_DESIGN_STR} --> {LOGIC_CODE_DESIGN_STR}

Each of these steps is crucial for ensuring that the application is built efficiently and meets the required specifications.""",
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "info": True,
                          "iteration": 0,
                          "file_name": "entity/app_design.json",
                          "flow_step": GATHERING_REQUIREMENTS_STR,
                          "max_iteration": 0},
                      {
                          "notification": """
👋 Welcome to Cyoda Application Builder! We’re excited to build something amazing with you! 😄  

We’re here to help with building and deploying on Cyoda Cloud! Reach out anytime! 🌟 Your branch will be ready soon, and I’ll notify you when I push changes. If you have suggestions, message me or use Canvas! 😊  

In Canvas, you can code, edit, and improve around the main app build flow! It’s a great way to collaborate and make changes! 💻  

If you’re happy with the progress or want me to pull your changes, just give me a thumbs up! 👍  (currently approve button in the top panel)

If something goes wrong, no worries—just roll back! 😬 Your app will be live on Cyoda Platform GitHub soon! 🚀 Let’s build your branch together! 🌿
""",
                          "prompt": {},
                          "answer": None,
                          "function": None,
                          "iteration": 0,
                          "info": True,
                          "file_name": "instruction.txt",
                          "max_iteration": 0
                      }
                      ]

data_ingestion_stack = lambda entities: [
    {
        "question": f"😊✨ Are you ready to move on to the next iteration? Give me thumbs up if you are ready to proceed 👍👍",
        "prompt": {},
        "answer": None,
        "function": None,
        "index": 0,
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "approve": True,
        "max_iteration": 0},
    {
        "question": None,
        "prompt": {},
        "answer": None,
        "function": {"name": "generate_data_ingestion_code",
                     "prompts": {
                         "EXTERNAL_SOURCES_PULL_BASED_RAW_DATA": {
                             "text": "Generate Python code to fetch data from the external data source described in {doc}. The code should ingest the data according to the documentation and return processed (mapped) data without saving to repository. If the data source response differs from the entity {entity_data}, map the raw data to the entity structure. If no mapping is needed, assume the response matches the entity format. Create a public function ingest_data(...) that handles the ingestion process. Also generate tests so that the user can try out the functions right away in isolated environment. No need to mock anything. **Tests should be in the same file with the code**",
                         },
                         "WEB_SCRAPING_PULL_BASED_RAW_DATA": {
                             "text": "Generate Python code to fetch data from the external data source described in {doc}. The code should ingest the data according to the documentation and return processed (mapped) data without saving to repository. If the data source response differs from the entity {entity_data}, map the raw data to the entity structure. If no mapping is needed, assume the response matches the entity format. Create a public function ingest_data(...) that handles the ingestion process. Also generate tests so that the user can try out the functions right away in isolated environment. No need to mock anything.  **Tests should be in the same file with the code**",
                         },
                         "TRANSACTIONAL_PULL_BASED_RAW_DATA": {
                             "text": "Generate Python code to fetch data from the external data source described in {doc}. The code should ingest the data according to the documentation and return processed (mapped) data without saving to repository. If the data source response differs from the entity {entity_data}, map the raw data to the entity structure. If no mapping is needed, assume the response matches the entity format. Create a public function ingest_data(...) that handles the ingestion process. Also generate tests so that the user can try out the functions right away in isolated environment. No need to mock anything.  **Tests should be in the same file with the code**",
                         }
                     }},
        "context": {
            "files": [],
        },
        "entities": entities,
        "files_notifications": FILES_NOTIFICATIONS,
        "notification_text": "🎉 The code for data ingestion has been generated successfully! Please check it out and click 'Approve' if you're ready to move on to the next iteration. Feel free to use Canvas QA to suggest any improvements! 😊",
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "max_iteration": MAX_ITERATION
    },
    {
        "question": f"🚀 Are you ready to start the bulk generation? Give me thumbs up to let me know you're good to go!👍👍 😊",
        "prompt": {},
        "answer": None,
        "approve": True,
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
        "approve": True,
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
            "files": ["entity/app_design.json", "entity/user_requirement.md"],
        },
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "max_iteration": 0},
    {
        "notification": """
We are currently generating templates for your data ingestion entities! 🎉 Once I’m done, you’ll find each entity in a separate folder: `entity/{entity_name}/{entity_name}.json`. 🗂️
Also you’ll find connection folder for each entity where we'll configure code for the data ingestion: `entity/{entity_name}/connections/connection.py`. 🗂️

This file will represent the **entity model** as semi-structured data (think of it as an example). For data ingestion, this model should either be:
- **A golden JSON**: The raw data output from your data source, or
- **A transformed version**: In which case, we’ll automatically handle the mapping for you! 🔄

For now, we just need you to either:
- **Provide your own data example**, or
- **Approve our example** if it works for you! 👍 Once you’re happy with it, we can move forward!

If everything looks good, just give us a thumbs up! 👍  
If you want to make any changes, feel free to edit the file in your IDE and **push the changes** so I can fetch them. Or, you can edit the models directly here, and I’ll save them for you! ✏️

Also, feel free to use **Canvas** to collaborate and edit the models together! 🖌️😊

Looking forward to your feedback! 🌟
""",
        "prompt": {},
        "info": True,
        "answer": None,
        "function": None,
        "iteration": 0,
        "max_iteration": 0
    },
    {
        "notification": f"""Proceeding to {ENTITIES_DESIGN_STR}
        
        
{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> ***{ENTITIES_DESIGN_STR}*** --> {WORKFLOW_DESIGN_STR} --> {WORKFLOW_CODE_DESIGN_STR} --> {LOGIC_CODE_DESIGN_STR}""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0},
]

entity_stack = lambda entities: [
    {
        "question": f"😊✨ Are you ready to move on to the next iteration? Let me know when you're all set! Give me thumbs up 👍👍 if you are ready to proceed",
        "prompt": {},
        "answer": None,
        "function": None,
        "approve": True,
        "index": 0,
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "max_iteration": 0},
    {
        "question": None,
        "prompt": {},
        "answer": None,
        "function": {"name": "generate_entities_template",
                     "prompts": {
                         "ai_question": "Based on the data you have in the context and your understanding of the users requirement please generate json data example for entity {entity_name}. This json data should reflect business logic of the entity - it is not related to entity design schema!!!! it should not have any relevance to Cyoda. {user_data}. Return json with markdown."
                     }},
        "files_notifications": FILES_NOTIFICATIONS,
        "context": {
            "files": [],
        },
        "entities": entities,
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "notification_text": f"😊 Could you please take a look at the generated entity examples? If you have a specific structure in mind, feel free to adjust my suggestions and click 'Approve' 👍. You can also use Canvas to edit the entities together. Thanks so much!",
        "max_iteration": 0},
    {
        "notification": """
We are currently generating templates for your entities! 🎉 Once I’m done, you’ll find each entity in a separate folder: `entity/{entity_name}/{entity_name}.json`. 🗂️

This file will represent the **entity model** as semi-structured data (think of it as an example). Later, we’ll automatically generate the dynamic entity schema based on this JSON data. 🔄

For now, we just need you to either:
- **Provide your own data example**, or
- **Approve our example** if it works for you! 👍 Once you’re happy with it, we’re good to move forward!

If everything looks good, just give us a thumbs up! 👍  
If you want to make any changes, feel free to edit the file in your IDE and **push the changes** so I can fetch them. Or, you can edit the models directly here, and I’ll save them for you! ✏️

Also, feel free to use **Canvas** to collaborate and edit the models together! 🖌️😊

Looking forward to your feedback! 🌟
""",
        "prompt": {},
        "info": True,
        "answer": None,
        "function": None,
        "iteration": 0,
        "file_name": "entity/app_design.json",
        "flow_step": APPLICATION_DESIGN_STR,
        "max_iteration": 0
    },
    {
        "question": f"🚀 We’re all set to start generating the entities! If you have any additional details you'd like me to include, feel free to share. No worries if anything goes wrong – we can always fix it later! 😊 If you are ready to proceed give me a thumbs up! 👍 (currently: approve button)",
        "prompt": {},
        "answer": None,
        "function": None,
        "index": 0,
        "iteration": 0,
        "approve": True,
        "flow_step": ENTITIES_DESIGN_STR,
        "files_notifications": FILES_NOTIFICATIONS,
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
        "notification_text": "",
        "iteration": 0,
        "flow_step": ENTITIES_DESIGN_STR,
        "max_iteration": 0},
]

workflow_stack = lambda entity: [
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
     "additional_questions": [{"question": "Would you like to improve the workflow?", "approve": True}],
     "max_iteration": MAX_ITERATION},
    # Would you like to add any changes to entity workflow
    {
        "question": f"Would you like to add any changes to entity workflow: entity/{entity.get("entity_name")}/workflow/workflow.json . If not - you can just approve and proceed to the next step 👍",
        "prompt": {},
        "answer": None,
        "function": None,
        "approve": True,
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
        "max_iteration": 0},
    {
        "notification": """
**While we work on your app design, let me quickly introduce Cyoda...** 😄

**On Entity Workflows and How an EDBMS Leads to a Horizontally Scalable Event-Driven Architecture (EDA)**

In a previous article, we introduced the Entity Database (EDBMS). Now, let’s dive into how an EDBMS leads to a simpler, horizontally scalable event-driven architecture (EDA), where applications become “thin clients” with fewer moving parts and a smaller codebase. 😎

### Entity Workflow
An Entity Workflow includes:
1. **States**: The logical status of an entity (e.g., LOCKED, UNLOCKED).
2. **Transitions**: Pathways allowing an entity to change from one state to another.
3. **Predicates**: Conditions or rules that decide if a transition can happen.
4. **Actions**: Events triggered by transitions.

### Example: Careful Turnstile
A turnstile can have states like LOCKED and UNLOCKED. When a coin is added, it transitions to UNLOCKED. We can add actions to lock or unlock the turnstile based on the state. 🔒

#### Automating Transitions
We can automate transitions based on safety checks, like ensuring it's safe to pass before unlocking the turnstile. This makes the workflow smarter and more automated. 🤖

#### Adding More Features
You can further enhance workflows by adding states like OFFLINE or controlling status lights. By adding predicates and actions, we can easily update the turnstile’s behavior as needed. 🚦

### Workflow Diagram
Here’s a textual depiction of the turnstile workflow:

None --> New --> LOCKED --> Coin --> UNLOCKED --> Coin --> LOCKED

- The flow starts at **None** when the turnstile is first created.
- Then, it transitions to **LOCKED** via the **New** transition.
- From **LOCKED**, inserting a **Coin** moves it to **UNLOCKED**.
- From **UNLOCKED**, pressing the **Push** button brings it back to **LOCKED**.
- Inserting a **Coin** again when it's **LOCKED** keeps it in a loop between **LOCKED** and **UNLOCKED**.

### Why This Works
Entity workflows are intuitive and iterative. They break complex tasks into smaller, manageable actions and rules that can be reused, making systems more adaptable to change and easier to maintain. 🔄

For more on Entity Workflows and EDA, check out this article by [Paul Schleger](https://medium.com/@paul_42036/entity-workflows-for-event-driven-architectures-4d491cf898a5).
""",
        "prompt": {},
        "info": True,
        "answer": None,
        "function": None,
        "iteration": 0,
        "file_name": "entity/app_design.json",
        "flow_step": APPLICATION_DESIGN_STR,
        "max_iteration": 0
    },
    {
        "notification": f"""Proceeding to {WORKFLOW_DESIGN_STR}
        
        
{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> {ENTITIES_DESIGN_STR} --> ***{WORKFLOW_DESIGN_STR}*** --> {WORKFLOW_CODE_DESIGN_STR} --> {LOGIC_CODE_DESIGN_STR}""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0},
]

processors_stack = lambda entity: [
    # Would you like to edit the model
    # Generate the processor functions
    {"question": None,
     "prompt": {
         "text": f"Please, generate the processor functions for {entity.get('entity_name')} "
                 f"call public functions by the name of each processor: "
                 f"{', '.join([transition.get('process', {}).get('name', '') for transition in entity.get('entity_workflow', {}).get('transitions', [])])}. "
                 f" Reuse functions that are available in the code base, including logic.app_init import entity_service, connections.py (ingest_data public function) and any other existing function that is related to your purpose."
                 f" Make sure you include logic to save any dependant entities: {', '.join([transition.get('process', {}).get('adds_new_entites', '') for transition in entity.get('entity_workflow', {}).get('transitions', [])])}."
                 f" Also generate tests with mocks for external services or functions so that the user can try out the functions right away in isolated environment. **Tests should be in the same file with the code**"
                 f"{entity.get('entity_name')}. Based on the user suggestions if there are any. "
                 f" Please make sure you are re-using all raw_data_*/connections/connection.py ingest_data functions. This is very important not to re-implement ingest_data but reuse it. You should import and reuse all ingest_data functions, use 'as' to avoid names duplicates. Make sure the result of data ingestion is saved to the corresponding raw data entity."
                 f" Please also make sure that you understand that argument 'data' that you pass to each function corresponds to entity/{entity.get('entity_name')}/{entity.get('entity_name')}.json data and not to any other entity!"
                 f" User says: ",
     },
     "answer": None,
     "function": None,
     "entity": entity,
     "index": 0,
     "iteration": 0,
     "file_name": f"entity/{entity.get("entity_name")}/workflow/workflow.py",
     "flow_step": WORKFLOW_CODE_DESIGN_STR,
     "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
     "max_iteration": MAX_ITERATION
     },
    # Would you like to specify any details for generating processors
    {
        "question": f"Would you like to share any comments or suggestions for these functions: {', '.join([transition.get('process', {}).get('name', '') for transition in entity.get('entity_workflow', {}).get('transitions', [])])}? 🤔 We’d love to hear your ideas to make it even better! 😄",
        "prompt": {},
        "answer": None,
        "function": None,
        "index": 0,
        "iteration": 0,
        "flow_step": WORKFLOW_CODE_DESIGN_STR,
        "approve": False,
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
    {
        "notification": f"""
Now it’s time to give life to {entity.get('entity_name')} workflow! 🎉

Our workflow will have a set of functions 🛠️ (think of them as isolated functions that will receive your entity as an argument). These functions can perform various actions on your entity. It’s a bit like AWS Lambda's **FaaS** (Function as a Service) in a way 💻⚡
""",
        "prompt": {},
        "answer": None,
        "function": None,
        "iteration": 0,
        "info": True,
        "file_name": "entity/app_design.json",
        "flow_step": APPLICATION_DESIGN_STR,
        "max_iteration": 0
    },
    {
        "notification": f"""Proceeding to {WORKFLOW_CODE_DESIGN_STR}
        
        
{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> {ENTITIES_DESIGN_STR} --> {WORKFLOW_DESIGN_STR} --> ***{WORKFLOW_CODE_DESIGN_STR}*** --> {LOGIC_CODE_DESIGN_STR}""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0},
]

scheduler_stack = lambda entity: [
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
     "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
     "max_iteration": MAX_ITERATION
     },
    {
        "question": f"Let's generate the logic to schedule saving the entity {entity.get("entity_name")}. Would you like to specify any details?",
        "prompt": {},
        "approve": False,
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
    {
        "notification": f"""Proceeding to {LOGIC_CODE_DESIGN_STR}
        
        
{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> {ENTITIES_DESIGN_STR} --> {WORKFLOW_DESIGN_STR} --> {WORKFLOW_CODE_DESIGN_STR} --> ***{LOGIC_CODE_DESIGN_STR}***""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0},
]

form_submission_stack = lambda entity: [
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
     "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
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
     "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
     "max_iteration": MAX_ITERATION
     },
    {
        "question": f"Let's generate the logic to process the form application and saving the entity {entity.get("entity_name")} with the form entity. Would you like to specify any details?",
        "prompt": {},
        "answer": None,
        "approve": False,
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
    {
        "notification": f"""Proceeding to {WORKFLOW_CODE_DESIGN_STR}
        
        
{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> {ENTITIES_DESIGN_STR} --> {WORKFLOW_DESIGN_STR} --> {WORKFLOW_CODE_DESIGN_STR} --> ***{LOGIC_CODE_DESIGN_STR}***""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0},
]

file_upload_stack = lambda entity: [
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
     "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
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
     "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
     "max_iteration": MAX_ITERATION
     },
    {
        "question": f"Let's generate the logic to upload the file and saving the entity {entity.get("entity_name")} based on the file contents. Would you like to specify any details?",
        "prompt": {},
        "answer": None,
        "function": None,
        "approve": False,
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
    {
        "notification": f"""Proceeding to {WORKFLOW_CODE_DESIGN_STR}
        
        
{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> {ENTITIES_DESIGN_STR} --> {WORKFLOW_DESIGN_STR} --> {WORKFLOW_CODE_DESIGN_STR} --> ***{LOGIC_CODE_DESIGN_STR}***""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0},
]

api_request_stack = lambda entity: [
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
     "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
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
     "additional_questions": [{"question": QUESTION_OR_VALIDATE, "approve": True}],
     "max_iteration": MAX_ITERATION
     },
    {
        "question": f"Let's generate the api for processing entity and saving the entity {entity.get("entity_name")}. Would you like to specify any details?",
        "prompt": {},
        "answer": None,
        "approve": False,
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
    {
        "notification": f"""Proceeding to {WORKFLOW_CODE_DESIGN_STR}
        
        
{GATHERING_REQUIREMENTS_STR} --> {APPLICATION_DESIGN_STR} --> {ENTITIES_DESIGN_STR} --> {WORKFLOW_DESIGN_STR} --> {WORKFLOW_CODE_DESIGN_STR} --> ***{LOGIC_CODE_DESIGN_STR}***""",
        "prompt": {},
        "answer": None,
        "function": None,
        "info": True,
        "iteration": 0,
        "max_iteration": 0},
]
