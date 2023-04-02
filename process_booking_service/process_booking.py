import os
import sys
import requests
from flask import Flask, Response, render_template, request, url_for, redirect, jsonify
from flask_cors import CORS, cross_origin
from os import environ
# from pymongo import MongoClient
# from bson import json_util
# from bson.objectid import ObjectId
from datetime import datetime
from kafka import KafkaProducer
import json
import pika
import requests
import amqp_setup

app = Flask(__name__)

CORS(app)

update_booking_URL = "http://localhost:5007/update_booking"

# Setting up kafka producer for recommendation
# p = KafkaProducer(bootstrap_servers=['kafka:9092'],
#                          value_serializer=lambda x: json.dumps(x).encode('utf-8'))
# print("Kafka Producer has been initiated...")


@app.route('/update_payment', methods=['POST'])
def process_booking():

    data = request.get_json()
    # print('This is error output', file=sys.stderr)
    print(data, file=sys.stderr)

    # Sample response data from payment service
    temporary_response_data = {'amount': 200000, 'amount_capturable': 0, 'amount_details': {'tip': {}}, 'amount_received': 200000, 'automatic_payment_methods': {'enabled': True}, 'capture_method': 'automatic', 'client_secret': 'pi_3MqawoJTqG9NvRuT1CIECYYH_secret_FhWhAZ6MUjAnfbAqvBOxOjxwB', 'confirmation_method': 'automatic', 'created': 1680003858, 'currency': 'sgd', 'id': 'pi_3MqawoJTqG9NvRuT1CIECYYH', 'latest_charge': {'id': 'ch_3MqawoJTqG9NvRuT1geYkf4z'}, 'livemode': False, 'metadata': {'courseDescription': "A 3rd semester course at SMU, continues to develop students' understanding of object oriented programming, memory management", 'userEmail': 'celov54484@gpipes.com', 'coursename': 'Data Structure Algorithms', 'runID': '1', 'orderID': '4500', 'userID': '10', 'classId': '3'}, 'object': 'payment_intent', 'payment_method': {'id': 'pm_1Mqax8JTqG9NvRuTdQ8sxHYn'}, 'payment_method_options':
                               {'card': {'request_three_d_secure': 'automatic'}, 'paynow': {}}, 'payment_method_types': ['card', 'paynow'], 'status': 'succeeded'}

    # url = 'http://host.docker.internal:5007/update_booking'
    # headers = {'Content-Type': 'application/json'}
    # response_data = requests.post(url,data=json.dumps(data),headers=headers)

    ##################################
    # Sending of booking data to kafka log
    # p.send('booking', data)
    ##################################

    ##################################
    # Sending amqp to message service
    print('\n\n-----Backend updated, publishing the (class booking) message with routing_key=email.info-----')
    # notification is listening to email_service queue
    # binding key is email.info as well

    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="email.info",
                                     body=dataObject, properties=pika.BasicProperties(delivery_mode=2))
    # No need to return response to process_booking

    # pass payment_response and class_booking jSON
    # class_booking will need to have class id , run id , userid
    # response = requests.request("POST", update_booking_URL,
    # json={
    #     "userEmail" : "celov54484@gpipes.com",
    #     "userName" : "celo",
    #     "orderID" : "4500",
    #     "courseName" : "Data Structure Algorithms",
    #     "coursePrice" : "$2000",
    #     "courseDescription" : "A 3rd semester course at SMU, continues to develop students' understanding of object oriented programming, memory management",
    #     "classId" : 3,
    #     "runId": 1,
    #     "userId": 10,
    #     }
    # )

    return {
        "code": 201,
        "data": {
            "order": "success"
        }
    }


@app.route('/booking/createPayment', methods=['POST'])
@cross_origin()
def create_payment():
    data = request.get_json()
    print('This is file recevied by create_payment', file=sys.stderr)
    print(data, file=sys.stderr)
    # This is for docker
    url = 'http://host.docker.internal:8080/create-payment-intent'
    # url = 'http://localhost:8080/create-payment-intent'
    headers = {'Content-Type': 'application/json'}

    response_data = requests.post(url, data=json.dumps(data), headers=headers)
    for item in response_data:
        print("ITEM IS", item)

    # data received is
    # {'amount': 1500, 'amount_capturable': 0, 'amount_details': {'tip': {}}, 'amount_received': 1500, 'automatic_payment_methods': {'enabled': True}, 'capture_method': 'automatic', 'client_secret': 'pi_3MnMh6JTqG9NvRuT0xGeHdCj_secret_gsKWOlAlwTsdvsj1Ru9cK6goW', 'confirmation_method': 'automatic', 'created': 1679234084, 'currency': 'sgd', 'id': 'pi_3MnMh6JTqG9NvRuT0xGeHdCj', 'latest_charge': {'id': 'ch_3MnMh6JTqG9NvRuT0DB1hg0w'}, 'livemode': False, 'metadata': {}, 'object': 'payment_intent', 'payment_method': {'id': 'pm_1MnMhFJTqG9NvRuT8Hf2rccH'}, 'payment_method_options': {'card': {'request_three_d_secure': 'automatic'}, 'paynow': {}}, 'payment_method_types': ['card', 'paynow'], 'status': 'succeeded'}
    response_str = response_data.content.decode()
    return json.loads(response_str)


"""
Order JSON Object parsed into ProcessEmailService should follow this format
{
userEmail: String,
userName: String,
orderID: String,
courseName: String,
coursePrice: String,
courseDescription: String
}

Example of Order JSON Object
{
    "userEmail" : "celov54484@gpipes.com",
    "userName" : "celo",
    "orderID" : "4500",
    "courseName" : "Data Structure Algorithms",
    "coursePrice" : "$2000",
    "courseDescription" : "A 3rd semester course at SMU, continues to develop students' understanding of object oriented programming, memory management"
    "classID" : 3,
    "runID": 1,
    "userID": 10,
}
"""

# Code from update_booking.py to send msg into AMQP for message service

@app.route("/update_booking",methods=['POST'])
def update_booking():
    data = request.get_json()
    dataObject = json.dumps(data)
    print('request data from process_booking: ',dataObject)

    # flag and code for testing
    payment_successful,code = True, 200
    # payment_successful,code = False, 400


    # if payment response successful
    if payment_successful:
        print('\n\n-----Publishing the (class booking) message with routing_key=booking.*-----')
        # publish class details JSON message to rabbitMQ
        # which will update the backend

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="booking.info", 
            body=dataObject, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues until it is received by some receiver 
        # (the matching queues have to exist and be durable and bound to the exchange)

        # continue even if this invocation fails        
        print("\Booking info ({:d}) published to the RabbitMQ Exchange:".format(
            code), dataObject)
        
        # then when response received from this update, fire off email
        # publish email message and JSON data to rabbitMQ

        print('\n\n-----Backend updated, publishing the (class booking) message with routing_key=email.info-----')
        # notification is listening to email_service queue 
        # binding key is email.info as well

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="email.info", 
            body=dataObject, properties=pika.BasicProperties(delivery_mode = 2)) 
        # No need to return response to process_booking
        return {
            "code": 201,
            "data": {
                "order": "success"
            }
        } 

    
    # else if unsuccessful, fire email only
    else:
        # publish email message and JSON data to rabbitMQ
        print('\n\n-----Payment failed, publishing the (class booking) message with routing_key=email.info-----')
        # notification is listening to email_service queue 
        # binding key is email.info as well

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="email.info", 
            body=dataObject, properties=pika.BasicProperties(delivery_mode = 2)) 

    # No need to return response to process_booking

    return {
        "code": 201,
        "data": {
            "order": "success"
        }
    }

if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " to coordinate payments with updating of class and user services")
    app.run(host="0.0.0.0", port=5008, debug=True)
print(f"Flask app is initialized on port 5008")
