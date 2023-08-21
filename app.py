from flask import Flask, request, jsonify
import os
import requests
import json
from dotenv import load_dotenv 
load_dotenv()
from flask_sqlalchemy import SQLAlchemy
from config import DB_PATH
from flask_migrate import Migrate



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=DB_PATH
db = SQLAlchemy(app)
secret_token = os.getenv("secret_token")

class ChatbotUser(db.Model): 
    __tablename__ = "chatbot_users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(15), nullable=False)

class ChatbotMessages(db.Model):
    __tablename__ = "chatbot_messages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(50))
    role = db.Column(db.String(50)) #AI or user
    content = db.Column(db.Text)




@app.route("/")
def home():
    return "project is working"

@app.route("/messages", methods = ["POST", "GET"])
def message():
    if request.method == "GET":
        print("this is working")
        sent_token = str(request.args.get("hub.verify_token")).split(" ")[0]
        print(request.args)
        print("This is my token    " + sent_token, "/n", secret_token)

        if sent_token != secret_token:
            return app.make_response(("forbiden token", 403))
        
        if request.args.get("hub.mode") != "subscribe":
            return app.make_response(("forbidden mode", 403))
        
        res = request.args.get("hub.challenge")
        return app.make_response((str(res), 200))
    
    else:
        url = "https://graph.facebook.com/v17.0/106267549227892/messages"
        headers = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + str(secret_token)}
        incoming_json_data = request.json
        print(incoming_json_data)

            

        #Extracting user id and message from the incoming request data
        if 'contacts' in incoming_json_data['entry'][0]['changes'][0]['value']:
            phone_number = incoming_json_data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
            name = incoming_json_data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']

        elif 'statuses' in incoming_json_data['entry'][0]['changes'][0]['value']:
            phone_number = incoming_json_data['entry'][0]['changes'][0]['value']['statuses'][0]['recipient_id']
        else:
            print("No contacts or statuses found")
            return
        if 'messages'in incoming_json_data['entry'][0]['changes'][0]['value']:
            message_data = incoming_json_data['entry'][0]['changes'][0]['value']['messages'][0]
            #Determine if the message is a text button_reply
            if message_data['type'] == 'text':
                customer_message = message_data['text']['body']
            elif message_data['type'] == 'reaction':
                customer_message = message_data['reaction']['emoji']
        
            # Printing the results
            print("Phone_number:", phone_number)
            print("Message:", customer_message)
            print("Name:", name)
            #print("Timestamp:", timestamp)
            #print("Timestamp (Human Readable):", timestamp_human_readable)
            
            chatbot_user = ChatbotUser.query.filter_by(phone_number=phone_number).first()

            if chatbot_user is None:
                #Save the user to the database
                chatbot_user = ChatbotUser(phone_number=phone_number)
                db.session.add(chatbot_user)

            else:
                new_entry = ChatbotMessages(session_id = phone_number, role = 'human', content = customer_message)
                db.session.add(new_entry) 
                db.session.commit()

        
            from sqlalchemy import create_engine, MetaData
            from config import DB_PATH

            engine = create_engine(DB_PATH)
            metadata_obj = MetaData()

            from llama_index import LLMPredictor, ServiceContext
            from langchain.chat_models import ChatOpenAI
            import os
            from dotenv import load_dotenv
            load_dotenv()

            api_key = os.getenv("openai_api_key")
            llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", max_tokens=-1, openai_api_key=api_key))
            ServiceContext = ServiceContext.from_defaults(llm_predictor=llm_predictor)

            from llama_index import SQLDatabase

            sql_database = SQLDatabase(engine, include_tables=['agents',
            'batch_items',
            'companies',
            'company_roles',
            'counties',
            'event_subscriptions',
            'events',
            'failed_jobs',
            'home_sliders',
            'industries',
            'invoices',
            'ipay_transactions',
            'jobs',
            'logistics',
            'media',
            'messages',
            'migrations',
            'mpesa_operations',
            'notifications',
            'order_items',
            'orders',
            'password_resets',
            'payments',
            'personal_access_tokens',
            'plan_features',
            'plan_subscription_usage',
            'plan_subscriptions',
            'plans',
            'product_categories',
            'product_images',
            'product_reviews',
            'products',
            'rider_deliveries',
            'riders',
            'roles',
            'sessions',
            'shipping_batches',
            'shop_settings',
            'shops',
            'system_settings',
            'transactions',
            'transfers',
            'wallets',
            'withdraw_requests'])

            from llama_index.indices.struct_store.sql_query import SQLTableRetrieverQueryEngine
            from llama_index.objects import SQLTableNodeMapping, ObjectIndex, SQLTableSchema
            from llama_index import VectorStoreIndex

            # manually set each table with a description of its contents
            agents_text = (
                "This table stores data about the agents who interact with the system.\n"
                "Information like agent name, contact details, and their associated company can be found here."
            )

            batch_items_text = (
                "This table holds the individual items that are part of a particular batch.\n"
                "Details about the item, quantity, and the batch it belongs to are included."
            )

            companies_text = (
                "This table contains information about the different companies involved.\n"
                "Details like company name, address, industry, and contact information are stored."
            )

            company_roles_text = (
                "This table stores information about various roles within a company.\n"
                "Each record can include role title and responsibilities."
            )

            counties_text = (
                "This table contains information about the different counties.\n"
                "Each county has details like its name, state, and other geographical data."
            )

            event_subscriptions_text = (
                "This table records the subscriptions to various events.\n"
                "Information like user ID, event ID, and subscription date are stored."
            )

            events_text = (
                "This table stores information about various events.\n"
                "Details like event name, date, location, and description are included."
            )

            failed_jobs_text = (
                "This table logs any jobs that have failed.\n"
                "It includes information like job name, error message, and timestamp of failure."
            )

            home_sliders_text = (
                "This table stores information about the slider images or content displayed on the home page.\n"
                "Details like slider title, image path, and display order are stored."
            )

            industries_text = (
                "This table describes the various industries that companies can belong to.\n"
                "It has details like industry name, and possibly some metrics associated with the industry."
            )

            invoices_text = (
                "This table stores invoice information.\n"
                "Details like invoice number, date, customer ID, and total amount are included."
            )

            ipay_transactions_text = (
                "This table holds information about transactions made through IPay.\n"
                "Details like transaction ID, date, amount, and customer ID are stored."
            )

            jobs_text = (
                "This table contains data about various jobs in the system.\n"
                "Details like job title, description, and related metrics can be found here."
            )

            logistics_text = (
                "This table stores information about logistics, such as shipment details.\n"
                "Information like shipment ID, dispatch date, destination, and status are included."
            )

            media_text = (
                "This table contains records of all media files used in the system.\n"
                "Each record could include file name, type, path, and usage context."
            )

            messages_text = (
                "This table holds records of all messages exchanged in the system.\n"
                "Each record could include sender ID, recipient ID, message content, and timestamp."
            )

            migrations_text = (
                "This table logs all migrations that have occurred in the system.\n"
                "Each record could include migration name, timestamp, and status."
            )

            mpesa_operations_text = (
                "This table stores information about transactions made through MPesa.\n"
                "Details like transaction ID, date, amount, and customer ID are stored."
            )

            notifications_text = (
                "This table logs all notifications sent within the system.\n"
                "Each record could include the notification content, recipient ID, sender ID, and timestamp."
            )

            order_items_text = (
                "This table contains individual items in an order.\n"
                "Each record could include the order ID, product ID, quantity, and price."
            )

            orders_text = (
                "This table stores information about customer orders.\n"
                "Each record includes details such as the customer ID, order date, total price, and order status."
            )

            password_resets_text = (
                "This table stores password reset requests.\n"
                "Each record includes user email, reset token, and the timestamp of the request."
            )

            payments_text = (
                "This table contains records of all payments made within the system.\n"
                "Details like payment ID, date, amount, and customer ID are stored."
            )

            personal_access_tokens_text = (
                "This table stores personal access tokens for users.\n"
                "Each token is associated with a user ID, and includes details like creation and expiry dates."
            )

            plan_features_text = (
                "This table lists the features of various subscription plans.\n"
                "Each record includes the plan ID and details about the feature."
            )

            plan_subscription_usage_text = (
                "This table tracks the usage of features for each subscription.\n"
                "Details like subscription ID, feature ID, and usage count are included."
            )

            plan_subscriptions_text = (
                "This table stores information about the different subscription plans users are on.\n"
                "Each record includes details like user ID, plan ID, start date, and end date."
            )

            plans_text = (
                "This table holds the various plans that a user can subscribe to.\n"
                "Each plan has details like plan name, price, and included features."
            )

            product_categories_text = (
                "This table stores information about different product categories.\n"
                "Each category has details like its name and description."
            )

            product_images_text = (
                "This table holds images associated with each product.\n"
                "Each record has details like product ID, image path, and image description."
            )

            product_reviews_text = (
                "This table stores reviews written by customers for products.\n"
                "Each record has details like product ID, user ID, review text, and rating."
            )

            products_text = (
                "This table stores information about the various products sold on the platform.\n"
                "Each product has a name, a description, a price, and belongs to a specific category."
            )

            rider_deliveries_text = (
                "This table tracks deliveries made by riders.\n"
                "Each record has details like rider ID, order ID, delivery date, and status."
            )

            riders_text = (
                "This table stores information about riders who deliver orders.\n"
                "Each rider has details like their name, contact information, and associated vehicle."
            )

            roles_text = (
                "This table holds information about different roles a user can have.\n"
                "Each role has a name and description."
            )

            sessions_text = (
                "This table records user sessions.\n"
                "Each record includes user ID, session ID, login time, logout time, and IP address."
            )

            shipping_batches_text = (
                "This table stores information about different shipping batches.\n"
                "Each batch has details like batch ID, creation date, and status."
            )

            shop_settings_text = (
                "This table stores settings related to different shops on the platform.\n"
                "Settings like shop ID, opening hours, and other preferences can be found here."
            )

            shops_text = (
                "This table contains information about the various shops on the platform.\n"
                "Each shop has details like its name, address, and contact information."
            )

            system_settings_text = (
                "This table stores overall system settings.\n"
                "Settings like system name, timezone, default language, and others can be found here."
            )

            transactions_text = (
                "This table holds records of all financial transactions made within the system.\n"
                "Details like transaction ID, date, amount, and associated user ID are stored."
            )

            transfers_text = (
                "This table stores information about money transfers between users.\n"
                "Each record includes details like sender ID, receiver ID, amount, and date."
            )

            users_text = (
                "This table contains data about users of the platform.\n"
                "Information like user ID, username, hashed password, email, and creation date are stored here."
            )

            wallets_text = (
                "This table holds information about users' digital wallets.\n"
                "Each wallet is associated with a user ID and includes details like balance and transaction history."
            )

            withdraw_requests_text = (
                "This table logs all withdrawal requests made by users.\n"
                "Each record includes user ID, amount, date of request, and status."
            )

            table_node_mapping = SQLTableNodeMapping(sql_database=sql_database)
            table_schema_objs = [
                SQLTableSchema(table_name="agents", context_str=agents_text),
                SQLTableSchema(table_name="batch_items", context_str=batch_items_text),
                SQLTableSchema(table_name="companies", context_str=companies_text),
                SQLTableSchema(table_name="company_roles", context_str=company_roles_text),
                SQLTableSchema(table_name="counties", context_str=counties_text),
                SQLTableSchema(table_name="event_subscriptions", context_str=event_subscriptions_text),
                SQLTableSchema(table_name="events", context_str=events_text),
                SQLTableSchema(table_name="failed_jobs", context_str=failed_jobs_text),
                SQLTableSchema(table_name="home_sliders", context_str=home_sliders_text),
                SQLTableSchema(table_name="industries", context_str=industries_text),
                SQLTableSchema(table_name="invoices", context_str=invoices_text),
                SQLTableSchema(table_name="ipay_transactions", context_str=ipay_transactions_text),
                SQLTableSchema(table_name="jobs", context_str=jobs_text),
                SQLTableSchema(table_name="logistics", context_str=logistics_text),
                SQLTableSchema(table_name="media", context_str=media_text),
                SQLTableSchema(table_name="messages", context_str=messages_text),
                SQLTableSchema(table_name="migrations", context_str=migrations_text),
                SQLTableSchema(table_name="mpesa_operations", context_str=mpesa_operations_text),
                SQLTableSchema(table_name="notifications", context_str=notifications_text),
                SQLTableSchema(table_name="order_items", context_str=order_items_text),
                SQLTableSchema(table_name="orders", context_str=orders_text),
                SQLTableSchema(table_name="password_resets", context_str=password_resets_text),
                SQLTableSchema(table_name="payments", context_str=payments_text),
                SQLTableSchema(table_name="personal_access_tokens", context_str=personal_access_tokens_text),
                SQLTableSchema(table_name="plan_features", context_str=plan_features_text),
                SQLTableSchema(table_name="plan_subscription_usage", context_str=plan_subscription_usage_text),
                SQLTableSchema(table_name="plan_subscriptions", context_str=plan_subscriptions_text),
                SQLTableSchema(table_name="plans", context_str=plans_text),
                SQLTableSchema(table_name="product_categories", context_str=product_categories_text),
                SQLTableSchema(table_name="product_images", context_str=product_images_text),
                SQLTableSchema(table_name="product_reviews", context_str=product_reviews_text),
                SQLTableSchema(table_name="products", context_str=products_text),
                SQLTableSchema(table_name="rider_deliveries", context_str=rider_deliveries_text),
                SQLTableSchema(table_name="riders", context_str=riders_text),
                SQLTableSchema(table_name="roles", context_str=roles_text),
                SQLTableSchema(table_name="sessions", context_str=sessions_text),
                SQLTableSchema(table_name="shipping_batches", context_str=shipping_batches_text),
                SQLTableSchema(table_name="shop_settings", context_str=shop_settings_text),
                SQLTableSchema(table_name="shops", context_str=shops_text),
                SQLTableSchema(table_name="system_settings", context_str=system_settings_text),
                SQLTableSchema(table_name="transactions", context_str=transactions_text),
                SQLTableSchema(table_name="transfers", context_str=transfers_text),
                SQLTableSchema(table_name="users", context_str=users_text),
                SQLTableSchema(table_name="wallets", context_str=wallets_text),
                SQLTableSchema(table_name="withdraw_requests", context_str=withdraw_requests_text)
            ]

            obj_index = ObjectIndex.from_objects(
                table_schema_objs,
                table_node_mapping,
                VectorStoreIndex,
                )

            query_engine = SQLTableRetrieverQueryEngine(
                sql_database, obj_index.as_retriever(similarity_top_k=1)
            )

            query_engine = SQLTableRetrieverQueryEngine(
                sql_database, obj_index.as_retriever(similarity_top_k=1)
            )

            from langchain.chains.conversation.memory import ConversationSummaryBufferMemory, ConversationBufferMemory
            from llama_index.langchain_helpers.agents import LlamaIndexTool, LlamaToolkit, IndexToolConfig, create_llama_chat_agent
            from langchain import OpenAI
            from langchain.chains import ConversationChain
            from langchain import PromptTemplate

            index_configs = []
            tool_configs = IndexToolConfig(
                query_engine=query_engine,
                name = "Vector Index",
                description="Always use this when getting answers from kouponzetu database",
                tool_kwargs={"return_direct": True}
            )
            index_configs.append(tool_configs)

            toolkit = LlamaToolkit(
                index_configs=index_configs
            )

            llm = ChatOpenAI(temperature=0,
                            openai_api_key=api_key,
                            model_name="gpt-3.5-turbo")

            template = """The following is a friendly conversation between a human and an AI called Zetu. Zetu is talkative and provides lots of specific details from its context. If Zetu does not know the answer to a question, it truthfully says it does not know. 

            Current conversation:
            {history}
            Human: {input}
            Zetu:"""
            prompt_template = PromptTemplate(
                input_variables=["history", "input"], 
                template=template
            )

            memory_prompt = ConversationChain(
                llm = llm,
                memory = ConversationBufferMemory(llm=llm, max_token_limit=650),
                prompt=prompt_template
            )

            memory_prompt2 = ConversationBufferMemory(memory_key="chat_history")

            agent_chain = create_llama_chat_agent(
            llm=llm,
            toolkit=toolkit,
            memory=memory_prompt2,
            verbose=True
            )

        
            response = agent_chain.run(input=customer_message)
            print(f"Agent: {response}")
            new_entry = ChatbotMessages(session_id = phone_number, role = 'AI', content = response)
            db.session.add(new_entry)
            db.session.commit()

            data = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text":{
                    "body": response,
                }
            }

            outgoing_data = requests.post(url, headers=headers, data=json.dumps(data))
            print(outgoing_data.content)
            print("end of code")


        return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    app.run()